from models.knowledge_tracing.kt_base import KT_Factor_Analysis_Model_Base
from courses.schemas import Course
from users.schemas import User

from abc import ABC, abstractmethod


class Base_task_selector(ABC):
    def __init__(self, model_class: KT_Factor_Analysis_Model_Base.__class__ | None = None):
        if model_class is not None:
            self.learner_model = model_class()
        else:
            self.learner_model = None

    @abstractmethod
    async def select(self, user: User, topic: str | None = None) -> str:
        raise NotImplementedError

    def validate_course(self, course: Course) -> None:
        if self.learner_model is not None:
            self.learner_model.validate_course(course)

    def check_and_set_default_params(self, course_dict: dict) -> None:
        if self.learner_model is not None:
            self.learner_model.set_missing_default_parameters(course_dict)

    def set_default_params(self, course_dict: dict) -> None:
        if self.learner_model is not None:
            self.learner_model.set_default_parameters(course_dict)

    async def update_course_weights(self, course: Course) -> None:
        if self.learner_model is not None:
            await self.learner_model.update_course_weights(course)
