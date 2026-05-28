from datetime import datetime, timedelta, timezone
from html import escape
import json
import secrets
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
import os
from db import database
from models.domain.executor import execute_code
from system.schemas import FinalPreviewLink
from users.handle_users import current_active_verified_user
from users.schemas import User

router = APIRouter()

ACTIVITY_TRACKER_DEMO_TASKS = [
    "remember_subject",
    "start_sessions",
    "add_session",
    "show_sessions",
    "describe_session",
    "total_study_time",
    "study_recommendation",
]


def _compose_task_source(prefix: str, body: str) -> str:
    prefix = (prefix or "").rstrip()
    body = (body or "").rstrip()
    return "\n".join(part for part in [prefix, body] if part != "")


def _build_activity_tracker_demo_script(task_sources: dict[str, str]) -> str:
    task_source_blocks = [task_sources[task_name] for task_name in ACTIVITY_TRACKER_DEMO_TASKS]
    return "\n\n".join(task_source_blocks) + """

import json
from contextlib import redirect_stdout
from io import StringIO

demo_result = {"available": False, "reason": "Demo could not be prepared."}

try:
    subject = remember_subject("Mathematics")
    sessions = start_sessions()
    sessions = add_session(sessions, subject, "45")
    sessions = add_session(sessions, "Physics", "30")

    show_sessions_buffer = StringIO()
    with redirect_stdout(show_sessions_buffer):
        show_sessions(sessions)

    total_minutes = total_study_time(sessions)
    demo_result = {
        "available": True,
        "rememberedSubject": subject,
        "sessions": sessions,
        "showSessionsOutput": [line for line in show_sessions_buffer.getvalue().splitlines() if line.strip()],
        "firstSessionDescription": describe_session(sessions[0]),
        "totalMinutes": total_minutes,
        "recommendation": study_recommendation(total_minutes),
    }
except Exception as error:
    demo_result = {
        "available": False,
        "reason": str(error),
    }

print("##!serialization!##")
print(json.dumps(demo_result))
print("##!serialization!##")
"""

@router.get("/about")
def get_about():
    filepath = os.path.join(os.path.dirname(__file__), "about.md")
    print(filepath)
    with open(filepath) as f:
        about_markdown = f.read()
    return({"about_markdown": about_markdown})

@router.get("/data_collection")
def get_about():
    filepath = os.path.join(os.path.dirname(__file__), "data_collection.md")
    print(filepath)
    with open(filepath) as f:
        data_collection_markdown = f.read()
    return({"data_collection_markdown": data_collection_markdown})

@router.get("/privacy_policy")
def get_policy():
    filepath = os.path.join(os.path.dirname(__file__), "privacy_policy.md")
    print(filepath)
    with open(filepath) as f:
        privacy_policy_markdown = f.read()
    return({"privacy_policy_markdown": privacy_policy_markdown})

@router.get("/imprint")
def get_imprint():
    filepath = os.path.join(os.path.dirname(__file__), "imprint.md")
    print(filepath)
    with open(filepath) as f:
        imprint_markdown = f.read()
    return({"imprint_markdown": imprint_markdown})


@router.get("/activity_tracker_demo")
async def get_activity_tracker_demo(user: User = Depends(current_active_verified_user)):
    if user.current_course != "activity_tracker":
        return {
            "available": False,
            "reason": "The Activity Tracker demo is only available inside the Activity Tracker course.",
        }

    task_sources: dict[str, str] = {}
    missing_tasks: list[str] = []
    tested_submissions = await database.get_tested_submissions_per_user_and_course(user.id, user.current_course)
    latest_valid_submissions: dict[str, object] = {}

    for submission in tested_submissions:
        if not submission.valid_solution or submission.code.strip() == "":
            continue
        previous_submission = latest_valid_submissions.get(submission.task_unique_name)
        if previous_submission is None or submission.id.generation_time > previous_submission.id.generation_time:
            latest_valid_submissions[submission.task_unique_name] = submission

    for task_name in ACTIVITY_TRACKER_DEMO_TASKS:
        current_body = ""
        try:
            attempt = await database.find_attempt(task_name, user.id, user.current_course)
        except ValueError:
            attempt = None

        if attempt is not None and attempt.current_state.strip() != "":
            current_body = attempt.current_state
        else:
            latest_submission = latest_valid_submissions.get(task_name)
            if latest_submission is not None:
                current_body = latest_submission.code

        task = await database.get_task(task_name)
        composed_source = _compose_task_source(task.prefix or "", current_body)
        if composed_source == "":
            missing_tasks.append(task_name)
            continue
        task_sources[task_name] = composed_source

    if len(missing_tasks) > 0:
        return {
            "available": False,
            "reason": "Complete the remaining Activity Tracker tasks to unlock the final demo.",
            "missingTasks": missing_tasks,
        }

    run_result = await execute_code(_build_activity_tracker_demo_script(task_sources))
    if isinstance(run_result, dict):
        return run_result

    return {
        "available": False,
        "reason": "The saved Activity Tracker solutions could not be executed.",
        "details": str(run_result)[:2000],
    }


@router.post("/final_preview_link")
async def create_final_preview_link(payload: dict, user: User = Depends(current_active_verified_user)):
        code = str(payload.get("code", "")).strip()
        title = str(payload.get("title", "Final App Preview")).strip()[:120] or "Final App Preview"
        if code == "":
                raise HTTPException(status_code=400, detail="No code provided for preview link.")

        settings = await database.get_settings()
        ttl_minutes = max(5, min(1440, int(getattr(settings, "final_preview_link_ttl_minutes", 120))))
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=ttl_minutes)
        token = secrets.token_urlsafe(32)

        await FinalPreviewLink(
                token=token,
                created_by_user_id=str(user.id),
                created_at_utc=now.isoformat(),
                expires_at_utc=expires_at.isoformat(),
                title=title,
                code=code[:50000],
        ).insert()

        return {
                "preview_url": f"/api/info/final_preview/{token}",
                "expires_at_utc": expires_at.isoformat(),
                "ttl_minutes": ttl_minutes,
        }


@router.get("/final_preview/{token}")
async def open_final_preview(token: str):
        preview = await FinalPreviewLink.find_one(FinalPreviewLink.token == token)
        if preview is None:
                raise HTTPException(status_code=404, detail="Preview link not found.")

        now = datetime.now(timezone.utc)
        expires_at = datetime.fromisoformat(preview.expires_at_utc)
        if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
        if now > expires_at:
                return HTMLResponse(
                        "<h1>Preview link expired</h1><p>This temporary link is no longer valid.</p>",
                        status_code=410,
                )

        escaped_title = escape(preview.title)
        escaped_code = escape(preview.code)
        may_be_web_app = "<html" in preview.code.lower() or "<body" in preview.code.lower() or "<script" in preview.code.lower()

        rendered_app_block = ""
        if may_be_web_app:
                rendered_app_block = f"""
                <section>
                    <h2>Live Preview</h2>
                    <iframe sandbox=\"allow-scripts\" srcdoc=\"{escape(preview.code)}\" style=\"width:100%;height:420px;border:1px solid #ccc;border-radius:8px;background:#fff;\"></iframe>
                </section>
                """

        html = f"""
<!doctype html>
<html>
    <head>
        <meta charset=\"utf-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <title>{escaped_title}</title>
        <style>
            body {{ font-family: ui-sans-serif, system-ui, sans-serif; margin: 0; background: #0b1220; color: #e5e7eb; }}
            main {{ max-width: 960px; margin: 0 auto; padding: 1.5rem; }}
            .meta {{ color: #9ca3af; margin-bottom: 1rem; }}
            pre {{ background: #111827; padding: 1rem; border-radius: 8px; overflow: auto; border: 1px solid #1f2937; }}
            h1, h2 {{ margin-bottom: 0.6rem; }}
        </style>
    </head>
    <body>
        <main>
            <h1>{escaped_title}</h1>
            <p class=\"meta\">Temporary preview link. Expires at {escape(preview.expires_at_utc)}.</p>
            {rendered_app_block}
            <section>
                <h2>Submitted Code</h2>
                <pre><code>{escaped_code}</code></pre>
            </section>
        </main>
    </body>
</html>
        """
        return HTMLResponse(html)