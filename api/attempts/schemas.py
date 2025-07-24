from beanie import Document
from typing import Optional
from beanie import PydanticObjectId

class Attempt(Document):
    user_id: str
    task_unique_name: str
    course_unique_name: str
    state_log: list
    current_state: str
    start_time_list: list
    duration_list: list

class AttemptState(Document):
    state_datetime: Optional[dict]=None
    diff: Optional[tuple]=str
    submission_id: Optional[str]=None

class NestedAttemptState(AttemptState):
    code_list: list[tuple]
    state_datetime_list: list
    current_state: str
    attempt_id: str

