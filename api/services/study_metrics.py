from __future__ import annotations

import ast
import asyncio
import re
import time
from collections import defaultdict
from datetime import datetime, timedelta

from beanie import PydanticObjectId

from attempts.schemas import Attempt
from courses.schemas import CourseEnrollment
from db import database
from feedback.schemas import Evaluated_feedback_submission
from runs.schemas import Evaluated_run_code_submission
from services.language_generation import parse_code_response
from submissions.schemas import Tested_Submission
from system.schemas import StudyMetricsResponse, StudyMetricsRow, StudyMetricsSummary
from users.schemas import User


TIME_FORMATS = ("%d.%m.%Y %H:%M:%S.%f", "%d.%m.%Y %H:%M:%S")
IDLE_GAP_THRESHOLD = timedelta(minutes=2)
ERROR_PATTERN = re.compile(
    r"Traceback \(most recent call last\)|"
    r"Error or Exception|"
    r"Time limit exceeded|"
    r"\b(?:Assertion|Attribute|Import|Index|Indentation|Key|ModuleNotFound|Name|Runtime|Syntax|Type|Value|ZeroDivision)Error\b|"
    r"\bException\b"
)


def _parse_timestamp(raw_value) -> datetime | None:
    if raw_value is None:
        return None
    if isinstance(raw_value, dict):
        raw_value = raw_value.get("utc") or raw_value.get("local")
    if not raw_value:
        return None
    for fmt in TIME_FORMATS:
        try:
            return datetime.strptime(raw_value, fmt)
        except ValueError:
            continue
    return None


def _format_timestamp(timestamp: datetime | None) -> str | None:
    if timestamp is None:
        return None
    return timestamp.strftime("%d.%m.%Y %H:%M:%S")


def _parse_duration(duration_value: str | None) -> timedelta:
    if not duration_value:
        return timedelta(0)

    days = 0
    time_value = duration_value.strip()
    if ", " in time_value and "day" in time_value:
        day_part, time_value = time_value.split(", ", 1)
        days = int(day_part.split()[0])

    hours_str, minutes_str, seconds_str = time_value.split(":", 2)
    return timedelta(
        days=days,
        hours=int(hours_str),
        minutes=int(minutes_str),
        seconds=float(seconds_str),
    )


def _normalize_code(code: str) -> str:
    normalized_lines = [line.rstrip() for line in (code or "").strip().splitlines()]
    return "\n".join(normalized_lines).strip()


def _looks_like_run_error(run_output: str | None, console_output: str | None = None) -> bool:
    combined_output = "\n".join([part for part in [run_output, console_output] if part]).strip()
    if combined_output == "":
        return False
    return bool(ERROR_PATTERN.search(combined_output))


def _levenshtein_distance(left: str, right: str) -> int:
    if left == right:
        return 0
    if left == "":
        return len(right)
    if right == "":
        return len(left)

    previous_row = list(range(len(right) + 1))
    for left_index, left_char in enumerate(left, start=1):
        current_row = [left_index]
        for right_index, right_char in enumerate(right, start=1):
            insert_cost = current_row[right_index - 1] + 1
            delete_cost = previous_row[right_index] + 1
            replace_cost = previous_row[right_index - 1] + (left_char != right_char)
            current_row.append(min(insert_cost, delete_cost, replace_cost))
        previous_row = current_row
    return previous_row[-1]


def _normalized_modification_distance(reference_code: str, compared_code: str) -> float:
    normalized_reference = _normalize_code(reference_code)
    normalized_compared = _normalize_code(compared_code)
    longest_length = max(len(normalized_reference), len(normalized_compared), 1)
    return round(_levenshtein_distance(normalized_reference, normalized_compared) / longest_length * 100, 2)


def _estimate_cyclomatic_complexity(code: str) -> int:
    normalized_code = _normalize_code(code)
    if normalized_code == "":
        return 0
    try:
        syntax_tree = ast.parse(normalized_code)
    except SyntaxError:
        return 0

    complexity = 1
    for node in ast.walk(syntax_tree):
        if isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler, ast.IfExp, ast.Match)):
            complexity += 1
        elif isinstance(node, ast.BoolOp):
            complexity += max(len(node.values) - 1, 0)
        elif isinstance(node, ast.comprehension):
            complexity += 1
    return complexity


def _compose_task_code(task, code: str) -> str:
    normalized_code = code or ""
    task_prefix = _task_attr(task, "prefix", "")
    if task_prefix in ["", "no_prefix"]:
        return normalized_code
    if normalized_code.startswith(task_prefix):
        return normalized_code
    return f"{task_prefix}\n{normalized_code}" if normalized_code else task_prefix


def _collect_attempt_activity(attempt: Attempt) -> tuple[timedelta, timedelta, int, int, int, list[datetime], int]:
    active_duration = timedelta(0)
    idle_duration = timedelta(0)
    clipboard_events = 0
    paste_events = 0
    blocked_clipboard_events = 0
    latest_activity_candidates: list[datetime] = []
    state_snapshots = len(attempt.state_log or [])

    interaction_timestamps: list[datetime] = []
    for state in attempt.state_log or []:
        parsed_timestamp = _parse_timestamp(state.state_datetime)
        if parsed_timestamp is not None:
            interaction_timestamps.append(parsed_timestamp)
            latest_activity_candidates.append(parsed_timestamp)

    for clipboard_event in attempt.clipboard_log or []:
        clipboard_events += 1
        if clipboard_event.action == "paste":
            paste_events += 1
        if clipboard_event.blocked:
            blocked_clipboard_events += 1
        parsed_timestamp = _parse_timestamp(clipboard_event.event_datetime)
        if parsed_timestamp is not None:
            interaction_timestamps.append(parsed_timestamp)
            latest_activity_candidates.append(parsed_timestamp)

    interaction_timestamps.sort()

    start_times = attempt.start_time_list or []
    duration_values = attempt.duration_list or []
    for session_index, start_time in enumerate(start_times):
        parsed_start = _parse_timestamp(start_time)
        if parsed_start is None:
            continue
        session_duration = _parse_duration(duration_values[session_index] if session_index < len(duration_values) else None)
        if session_duration <= timedelta(0):
            continue
        session_end = parsed_start + session_duration
        session_events = [event_time for event_time in interaction_timestamps if parsed_start <= event_time <= session_end]
        if len(session_events) == 0:
            idle_duration += session_duration
            continue

        previous_marker = parsed_start
        for current_marker in [*session_events, session_end]:
            gap = current_marker - previous_marker
            if gap < timedelta(0):
                continue
            active_slice = min(gap, IDLE_GAP_THRESHOLD)
            active_duration += active_slice
            idle_duration += gap - active_slice
            previous_marker = current_marker

    return (
        active_duration,
        idle_duration,
        clipboard_events,
        paste_events,
        blocked_clipboard_events,
        latest_activity_candidates,
        state_snapshots,
    )


async def _preload_task_cache(task_unique_names: set[str]) -> dict[str, dict]:
    """Fetch all referenced tasks in one batch query.

    Returns a dict mapping task_id → raw MongoDB document for fast lookups.
    """
    if not task_unique_names:
        return {}
    tasks = await database.db["tasks"].find(
        {"task_id": {"$in": list(task_unique_names)}}
    ).to_list(length=None)
    return {t["task_id"]: t for t in tasks}


def _task_attr(task: dict | None, attr: str, default=""):
    """Safely read an attribute from a task dict or Beanie object."""
    if task is None:
        return default
    if isinstance(task, dict):
        return task.get(attr, default)
    return getattr(task, attr, default)


# ── Metrics response cache ───────────────────────────────────────────

_metrics_cache: dict = {"response": None, "timestamp": 0.0, "ttl": 300.0}


def _metrics_cache_get() -> StudyMetricsResponse | None:
    if _metrics_cache["response"] is not None:
        if time.monotonic() - _metrics_cache["timestamp"] < _metrics_cache["ttl"]:
            return _metrics_cache["response"]
    return None


def _metrics_cache_set(response: StudyMetricsResponse) -> None:
    _metrics_cache["response"] = response
    _metrics_cache["timestamp"] = time.monotonic()


def _metrics_cache_invalidate() -> None:
    _metrics_cache["response"] = None
    _metrics_cache["timestamp"] = 0.0


async def collect_study_metrics(
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    force_refresh: bool = False,
) -> StudyMetricsResponse:
    """Collect per-enrollment study metrics.

    Parameters
    ----------
    from_date / to_date : Optional[datetime]
        Filter submissions, feedback, and runs to this time window.
    force_refresh : bool
        Bypass the 5‑minute response cache.
    """
    if not force_refresh:
        cached = _metrics_cache_get()
        if cached is not None:
            return cached

    # ── 1. Fetch all data in 6 parallel queries (not N×6) ──────────
    (
        enrollments,
        all_users,
        all_attempts,
        all_tested,
        all_feedback,
        all_runs,
    ) = await asyncio.gather(
        CourseEnrollment.find().to_list(),
        User.find().to_list(),
        Attempt.find().to_list(),
        Tested_Submission.find().to_list(),
        Evaluated_feedback_submission.find().to_list(),
        Evaluated_run_code_submission.find().to_list(),
    )

    # ── 2. Build lookup indexes ────────────────────────────────────
    users_by_id: dict[str, User] = {str(u.id): u for u in all_users}

    attempts_by_key: dict[tuple[str, str], list[Attempt]] = defaultdict(list)
    for a in all_attempts:
        attempts_by_key[(str(a.user_id), a.course_unique_name)].append(a)

    tested_by_key: dict[tuple[str, str], list[Tested_Submission]] = defaultdict(list)
    for ts in all_tested:
        if from_date and ts.submission_time:
            parsed = _parse_timestamp(ts.submission_time)
            if parsed and parsed < from_date:
                continue
        if to_date and ts.submission_time:
            parsed = _parse_timestamp(ts.submission_time)
            if parsed and parsed > to_date:
                continue
        tested_by_key[(str(ts.user_id), ts.course_unique_name)].append(ts)

    feedback_by_key: dict[tuple[str, str], list[Evaluated_feedback_submission]] = defaultdict(list)
    for fb in all_feedback:
        if from_date and fb.submission_time:
            parsed = _parse_timestamp(fb.submission_time)
            if parsed and parsed < from_date:
                continue
        if to_date and fb.submission_time:
            parsed = _parse_timestamp(fb.submission_time)
            if parsed and parsed > to_date:
                continue
        feedback_by_key[(str(fb.user_id), fb.course_unique_name)].append(fb)

    runs_by_key: dict[tuple[str, str], list[Evaluated_run_code_submission]] = defaultdict(list)
    for r in all_runs:
        if from_date and r.submission_time:
            parsed = _parse_timestamp(r.submission_time)
            if parsed and parsed < from_date:
                continue
        if to_date and r.submission_time:
            parsed = _parse_timestamp(r.submission_time)
            if parsed and parsed > to_date:
                continue
        runs_by_key[(str(r.user_id), r.course_unique_name)].append(r)

    # ── 3. Preload task cache from all referenced task names ────────
    all_task_names: set[str] = set()
    for a in all_attempts:
        all_task_names.add(a.task_unique_name)
    for ts in all_tested:
        all_task_names.add(ts.task_unique_name)
    for fb in all_feedback:
        all_task_names.add(fb.task_unique_name)
    for r in all_runs:
        all_task_names.add(r.task_unique_name)
    task_cache = await _preload_task_cache(all_task_names)

    # ── 4. Compute per-enrollment metrics ───────────────────────────
    rows: list[StudyMetricsRow] = []
    participant_ids: set[str] = set()

    summary_totals = {
        "tasks_attempted": 0,
        "tasks_completed": 0,
        "attempt_sessions": 0,
        "clipboard_events": 0,
        "paste_events": 0,
        "blocked_clipboard_events": 0,
        "state_snapshots": 0,
        "submissions": 0,
        "failed_submissions": 0,
        "runs": 0,
        "failed_runs": 0,
        "feedback_requests": 0,
        "total_logged_minutes": 0.0,
        "active_logged_minutes": 0.0,
        "idle_logged_minutes": 0.0,
        "max_code_complexity": 0,
        "ai_assisted_completed_tasks": 0,
        "ai_follow_up_actions": 0,
        "ai_exact_acceptances": 0,
        "ai_modification_distance_total": 0.0,
        "ai_modification_distance_count": 0,
    }

    for enrollment in enrollments:
        user = users_by_id.get(str(enrollment.user_id))
        if user is None:
            continue
        participant_ids.add(str(user.id))
        key = (str(user.id), enrollment.course_unique_name)

        attempts = attempts_by_key.get(key, [])
        tested_submissions = tested_by_key.get(key, [])
        feedback_submissions = feedback_by_key.get(key, [])
        run_submissions = runs_by_key.get(key, [])

        total_duration = timedelta(0)
        attempt_sessions = 0
        clipboard_events = 0
        paste_events = 0
        blocked_clipboard_events = 0
        state_snapshots = 0
        active_duration = timedelta(0)
        idle_duration = timedelta(0)
        max_code_complexity = 0
        latest_activity_candidates: list[datetime] = []

        for attempt in attempts:
            attempt_sessions += len(attempt.start_time_list or [])
            total_duration += sum((_parse_duration(value) for value in attempt.duration_list or []), timedelta(0))

            (
                attempt_active_duration,
                attempt_idle_duration,
                attempt_clipboard_events,
                attempt_paste_events,
                attempt_blocked_clipboard_events,
                attempt_latest_activity,
                attempt_state_snapshots,
            ) = _collect_attempt_activity(attempt)

            active_duration += attempt_active_duration
            idle_duration += attempt_idle_duration
            clipboard_events += attempt_clipboard_events
            paste_events += attempt_paste_events
            blocked_clipboard_events += attempt_blocked_clipboard_events
            state_snapshots += attempt_state_snapshots
            latest_activity_candidates.extend(attempt_latest_activity)

            for start_time in attempt.start_time_list or []:
                parsed_time = _parse_timestamp(start_time)
                if parsed_time is not None:
                    latest_activity_candidates.append(parsed_time)

            if attempt.current_state.strip() != "":
                task = task_cache.get(attempt.task_unique_name)
                max_code_complexity = max(
                    max_code_complexity,
                    _estimate_cyclomatic_complexity(_compose_task_code(task, attempt.current_state)),
                )

        regular_submissions = [submission for submission in tested_submissions if submission.type == "submission"]
        submission_count = len(regular_submissions)
        failed_submissions = sum(1 for submission in regular_submissions if not submission.valid_solution)
        feedback_count = len(feedback_submissions)

        for submission in tested_submissions:
            parsed_time = _parse_timestamp(submission.submission_time)
            if parsed_time is not None:
                latest_activity_candidates.append(parsed_time)

        failed_runs = 0
        for run_submission in run_submissions:
            parsed_time = _parse_timestamp(run_submission.submission_time)
            if parsed_time is not None:
                latest_activity_candidates.append(parsed_time)
            if _looks_like_run_error(run_submission.run_output, run_submission.console_output):
                failed_runs += 1

        completion_times_by_task: dict[str, list[datetime]] = defaultdict(list)
        follow_up_artifacts_by_task: dict[str, list[tuple[datetime, str]]] = defaultdict(list)

        for submission in regular_submissions:
            parsed_time = _parse_timestamp(submission.submission_time)
            if parsed_time is None:
                continue
            if submission.valid_solution:
                completion_times_by_task[submission.task_unique_name].append(parsed_time)
            task = task_cache.get(submission.task_unique_name)
            follow_up_artifacts_by_task[submission.task_unique_name].append(
                (parsed_time, _compose_task_code(task, submission.code))
            )

        for run_submission in run_submissions:
            parsed_time = _parse_timestamp(run_submission.submission_time)
            if parsed_time is None:
                continue
            task = task_cache.get(run_submission.task_unique_name)
            follow_up_artifacts_by_task[run_submission.task_unique_name].append(
                (parsed_time, _compose_task_code(task, run_submission.code))
            )

        for artifact_list in follow_up_artifacts_by_task.values():
            artifact_list.sort(key=lambda artifact: artifact[0])

        ai_follow_up_actions = 0
        ai_exact_acceptances = 0
        ai_modification_distances: list[float] = []
        completed_after_hint_tasks: set[str] = set()

        for feedback_submission in feedback_submissions:
            feedback_time = _parse_timestamp(feedback_submission.submission_time)
            if feedback_time is None:
                continue
            task_unique_name = feedback_submission.task_unique_name
            if any(completion_time > feedback_time for completion_time in completion_times_by_task.get(task_unique_name, [])):
                completed_after_hint_tasks.add(task_unique_name)

            if "```" not in feedback_submission.feedback:
                continue

            task = task_cache.get(task_unique_name)
            suggested_code = _compose_task_code(task, parse_code_response(feedback_submission.feedback))
            normalized_suggested_code = _normalize_code(suggested_code)
            if normalized_suggested_code == "":
                continue

            next_follow_up = next(
                (
                    artifact_code
                    for artifact_time, artifact_code in follow_up_artifacts_by_task.get(task_unique_name, [])
                    if artifact_time > feedback_time
                ),
                None,
            )
            if next_follow_up is None:
                continue

            ai_follow_up_actions += 1
            normalized_follow_up_code = _normalize_code(next_follow_up)
            if normalized_suggested_code == normalized_follow_up_code:
                ai_exact_acceptances += 1
            ai_modification_distances.append(
                _normalized_modification_distance(normalized_suggested_code, normalized_follow_up_code)
            )

        ai_assisted_completed_tasks = len(completed_after_hint_tasks)

        registered_at = _parse_timestamp(user.register_datetime)
        if registered_at is not None:
            latest_activity_candidates.append(registered_at)

        total_logged_minutes = round(total_duration.total_seconds() / 60, 2)
        active_logged_minutes = round(active_duration.total_seconds() / 60, 2)
        idle_logged_minutes = round(idle_duration.total_seconds() / 60, 2)
        latest_activity = max(latest_activity_candidates) if latest_activity_candidates else None
        ai_exact_acceptance_rate = round((ai_exact_acceptances / ai_follow_up_actions) * 100, 2) if ai_follow_up_actions > 0 else 0.0
        average_ai_modification_distance = round(sum(ai_modification_distances) / len(ai_modification_distances), 2) if len(ai_modification_distances) > 0 else 0.0

        row = StudyMetricsRow(
            username=user.username,
            course_unique_name=enrollment.course_unique_name,
            current_course=user.current_course,
            roles=[str(role) for role in user.roles],
            data_collection_enabled=bool(user.settings.get("dataCollection", False)),
            tasks_attempted=len(enrollment.tasks_attempted),
            tasks_completed=len(enrollment.tasks_completed),
            attempt_sessions=attempt_sessions,
            clipboard_events=clipboard_events,
            paste_events=paste_events,
            blocked_clipboard_events=blocked_clipboard_events,
            state_snapshots=state_snapshots,
            submissions=submission_count,
            failed_submissions=failed_submissions,
            runs=len(run_submissions),
            failed_runs=failed_runs,
            feedback_requests=feedback_count,
            total_logged_minutes=total_logged_minutes,
            active_logged_minutes=active_logged_minutes,
            idle_logged_minutes=idle_logged_minutes,
            max_code_complexity=max_code_complexity,
            ai_assisted_completed_tasks=ai_assisted_completed_tasks,
            ai_follow_up_actions=ai_follow_up_actions,
            ai_exact_acceptance_rate=ai_exact_acceptance_rate,
            average_ai_modification_distance=average_ai_modification_distance,
            registered_utc=_format_timestamp(registered_at),
            last_activity_utc=_format_timestamp(latest_activity),
        )
        rows.append(row)

        summary_totals["tasks_attempted"] += row.tasks_attempted
        summary_totals["tasks_completed"] += row.tasks_completed
        summary_totals["attempt_sessions"] += row.attempt_sessions
        summary_totals["clipboard_events"] += row.clipboard_events
        summary_totals["paste_events"] += row.paste_events
        summary_totals["blocked_clipboard_events"] += row.blocked_clipboard_events
        summary_totals["state_snapshots"] += row.state_snapshots
        summary_totals["submissions"] += row.submissions
        summary_totals["failed_submissions"] += row.failed_submissions
        summary_totals["runs"] += row.runs
        summary_totals["failed_runs"] += row.failed_runs
        summary_totals["feedback_requests"] += row.feedback_requests
        summary_totals["total_logged_minutes"] += row.total_logged_minutes
        summary_totals["active_logged_minutes"] += row.active_logged_minutes
        summary_totals["idle_logged_minutes"] += row.idle_logged_minutes
        summary_totals["max_code_complexity"] = max(summary_totals["max_code_complexity"], row.max_code_complexity)
        summary_totals["ai_assisted_completed_tasks"] += row.ai_assisted_completed_tasks
        summary_totals["ai_follow_up_actions"] += row.ai_follow_up_actions
        summary_totals["ai_exact_acceptances"] += ai_exact_acceptances
        summary_totals["ai_modification_distance_total"] += sum(ai_modification_distances)
        summary_totals["ai_modification_distance_count"] += len(ai_modification_distances)

    rows.sort(key=lambda row: (row.course_unique_name.lower(), row.username.lower()))

    ai_exact_acceptance_rate = round(
        (summary_totals["ai_exact_acceptances"] / summary_totals["ai_follow_up_actions"]) * 100,
        2,
    ) if summary_totals["ai_follow_up_actions"] > 0 else 0.0
    average_ai_modification_distance = round(
        summary_totals["ai_modification_distance_total"] / summary_totals["ai_modification_distance_count"],
        2,
    ) if summary_totals["ai_modification_distance_count"] > 0 else 0.0

    summary = StudyMetricsSummary(
        participants=len(participant_ids),
        enrollments=len(rows),
        tasks_attempted=summary_totals["tasks_attempted"],
        tasks_completed=summary_totals["tasks_completed"],
        attempt_sessions=summary_totals["attempt_sessions"],
        clipboard_events=summary_totals["clipboard_events"],
        paste_events=summary_totals["paste_events"],
        blocked_clipboard_events=summary_totals["blocked_clipboard_events"],
        state_snapshots=summary_totals["state_snapshots"],
        submissions=summary_totals["submissions"],
        failed_submissions=summary_totals["failed_submissions"],
        runs=summary_totals["runs"],
        failed_runs=summary_totals["failed_runs"],
        feedback_requests=summary_totals["feedback_requests"],
        total_logged_minutes=round(summary_totals["total_logged_minutes"], 2),
        active_logged_minutes=round(summary_totals["active_logged_minutes"], 2),
        idle_logged_minutes=round(summary_totals["idle_logged_minutes"], 2),
        max_code_complexity=summary_totals["max_code_complexity"],
        ai_assisted_completed_tasks=summary_totals["ai_assisted_completed_tasks"],
        ai_follow_up_actions=summary_totals["ai_follow_up_actions"],
        ai_exact_acceptance_rate=ai_exact_acceptance_rate,
        average_ai_modification_distance=average_ai_modification_distance,
    )
    response = StudyMetricsResponse(summary=summary, rows=rows)
    _metrics_cache_set(response)
    return response