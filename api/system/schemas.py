"""General Settings class for the app. In later iterations, I see no need to have such general settings and most settings should probably be set on course level.
"""
from pydantic import BaseModel
from beanie import PydanticObjectId
from beanie import Document
from typing import Optional

class AppSettings(Document):
    api_type: str = ""
    api_url: str = ""
    api_key: Optional[str]=None
    pedagogical_system_prompt: str = ""
    email_whitelist: list
    disable_editor_copy_paste: bool = False
    live_preview_mode: bool = False
    final_preview_link_ttl_minutes: int = 120


class EditorPolicy(BaseModel):
    disable_editor_copy_paste: bool = False


class StudyMetricsSummary(BaseModel):
    participants: int
    enrollments: int
    tasks_attempted: int
    tasks_completed: int
    attempt_sessions: int
    clipboard_events: int
    paste_events: int
    blocked_clipboard_events: int
    state_snapshots: int
    submissions: int
    failed_submissions: int
    runs: int
    failed_runs: int
    feedback_requests: int
    total_logged_minutes: float
    active_logged_minutes: float
    idle_logged_minutes: float
    max_code_complexity: int
    ai_assisted_completed_tasks: int
    ai_follow_up_actions: int
    ai_exact_acceptance_rate: float
    average_ai_modification_distance: float


class StudyMetricsRow(BaseModel):
    username: str
    course_unique_name: str
    current_course: str
    roles: list[str]
    data_collection_enabled: bool
    tasks_attempted: int
    tasks_completed: int
    attempt_sessions: int
    clipboard_events: int
    paste_events: int
    blocked_clipboard_events: int
    state_snapshots: int
    submissions: int
    failed_submissions: int
    runs: int
    failed_runs: int
    feedback_requests: int
    total_logged_minutes: float
    active_logged_minutes: float
    idle_logged_minutes: float
    max_code_complexity: int
    ai_assisted_completed_tasks: int
    ai_follow_up_actions: int
    ai_exact_acceptance_rate: float
    average_ai_modification_distance: float
    registered_utc: Optional[str] = None
    last_activity_utc: Optional[str] = None


class StudyMetricsResponse(BaseModel):
    summary: StudyMetricsSummary
    rows: list[StudyMetricsRow]


class FinalPreviewLink(Document):
    token: str
    created_by_user_id: str
    created_at_utc: str
    expires_at_utc: str
    title: str = "Final App Preview"
    code: str
