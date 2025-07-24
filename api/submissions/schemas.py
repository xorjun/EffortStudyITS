from beanie import PydanticObjectId
from beanie import Document
from typing import Optional

# TODO: refactor schemas into base class and classes for the task types
class Base_Submission(Document):
    task_unique_name: str
    course_unique_name: str
    code: str
    submission_time: dict
    type: str
    selected_choices: Optional[list]

    class Settings:
        name = "Submission"
        is_root=True

class Tested_Submission(Base_Submission):
    valid_solution: bool
    test_results: list
    user_id: PydanticObjectId
    possible_choices: Optional[list]
    correct_choices: Optional[list]

    class Settings: 
        name = "Submission"
