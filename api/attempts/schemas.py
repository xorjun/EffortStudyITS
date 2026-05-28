from beanie import Document
from typing import Optional
from beanie import PydanticObjectId
from pydantic import BaseModel, Field


class ClipboardEvent(BaseModel):
    action: str
    blocked: bool = False
    event_datetime: Optional[dict] = None


class AttemptState(Document):
    state_datetime: Optional[dict]=None
    diff: Optional[tuple]=str
    submission_id: Optional[str]=None

class Attempt(Document):
    user_id: str
    task_unique_name: str
    course_unique_name: str
    state_log: list[AttemptState]
    clipboard_log: list[ClipboardEvent] = Field(default_factory=list)
    current_state: str
    start_time_list: list
    duration_list: list


class NestedAttemptState(AttemptState):
    """Class for transporting Attempt states from the frontend to the backend.
    The code_list contains a list of tuples which represent line changes, 
    meaning that at index 0, a line number is given and at index 1, 
    it is given what the line should be replaced with.
    The line-number -1 means that a complete snapshot was necessary to represent the diff.

    Args:
        AttemptState (_type_): _description_
    """
    code_list: list[tuple]
    state_datetime_list: list
    current_state: str
    attempt_id: str


class ClipboardTelemetry(BaseModel):
    attempt_id: str
    action: str
    blocked: bool = False
    event_datetime: dict

