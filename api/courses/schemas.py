import itertools
from pydantic import model_validator
from beanie import Document
from typing import Any, Optional, Self
from enum import StrEnum

from users.schemas import UserLevel

# This is to avoid circular imports purely for type checking
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.pedagogical.content_selection.base_selector import Base_task_selector


class CourseValidationError(BaseException):
    """Exception raised in case the validation of a course fails."""

    def __init__(self, message):
        self.message = message
        super().__init__(message)


class TaskType(StrEnum):
    Function = "function"
    PlotFunction = "plot_function"
    Print = "print"
    MultipleChoice = "multiple_choice"


class AIAssistanceMode(StrEnum):
    Disabled = "disabled"
    Hints = "hints"


class Course(Document):
    unique_name: str
    display_name: str
    domain: str
    curriculum: dict[str, list[str]]
    mandatory_curriculum: Optional[list[str]] = None
    topics: list[str]
    default_topic: str
    sample_settings: list[float]
    course_settings_list: list[dict]
    visibility: UserLevel = UserLevel.student
    introduction: Optional[str] = None
    # Model related
    course_parameters: dict = {}
    q_matrix: dict[str, list[int]]
    competencies: list[str]
    
    
    # Set any missing default values for learner models
    # Note: The missing parameters for ALL models get set here, not only the required once, in case the models get switched later
    #@model_validator(mode='before')
    @classmethod
    def set_missing_default_parameters(cls, values: Any) -> Any:
        # Ensure this is a dict
        if isinstance(values, dict):
            for task_selector in cls.get_all_selectors():
                task_selector.check_and_set_default_params(values)
        else:
            raise ValueError("Malformed course dict.")
        return values
    
    def validate_for_models(self) -> Self:
        for task_selector in self.get_all_selectors():
            task_selector.validate_course(self)
        return self

    async def trigger_model_update(self) -> Self:
        for task_selector in self.get_course_selectors():
            await task_selector.update_course_weights(self)
        return self

    def get_local_curriculum(self, topic: str | None = None) -> list[str]:
        """Flatten the curriculum from a dict of task lists to a normal list of tasks."""
        if not topic is None:
            return self.curriculum[topic]
        else:
            curriculum = list(itertools.chain.from_iterable(self.curriculum.values()))
        return curriculum
    
    # Gets a list of all selectors currently in the Course settings
    def get_course_selectors(self) -> "list[Base_task_selector]":
        # Dependency injection to avoid circular imports
        from models import model_manager

        selectors = [
            model_manager.get_pedagogical_model(setting["pedagogical_model"]).task_selector
            for setting in self.course_settings_list
        ]
        return selectors
    
    # Gets a list of ALL available selectors
    @staticmethod
    def get_all_selectors() -> "list[Base_task_selector]":
        # Dependency injection to avoid circular imports
        from models import model_manager
        return model_manager.get_learner_models()


class CourseInfo(Document):
    course_list: list[dict]


class CourseSettings(Document):
    feedback_init_time: Optional[int] = None
    feedback_cooldown: Optional[int] = None
    pedagogical_model: Optional[str] = None
    language_generation_model: Optional[str] = None
    ai_assistance_mode: Optional[AIAssistanceMode] = AIAssistanceMode.Disabled


class CourseEnrollment(Document):
    user_id: str
    username: str
    course_unique_name: str
    tasks_completed: list[str]
    tasks_attempted: list[str]
    completed: bool
    course_settings_index: int


class CourseSelection(Document):
    course_unique_name: str
