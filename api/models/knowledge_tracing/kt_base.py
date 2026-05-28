from courses.schemas import Course
from users.schemas import User

from abc import ABC, abstractmethod


class KT_Factor_Analysis_Model_Base(ABC):
    
    @staticmethod
    @abstractmethod
    def validate_course(course: Course) -> None:
        pass

    @classmethod
    @abstractmethod
    def set_default_parameters(cls, course_dict: dict) -> None:
        pass

    @classmethod
    @abstractmethod
    def set_missing_default_parameters(cls, course_dict: dict) -> None:
        pass
    
    @classmethod
    @abstractmethod
    async def completion_probability(cls, task_names: str | list[str], user: User, course: Course | None = None) -> list[float]:
        raise NotImplementedError()
    
    @staticmethod
    @abstractmethod
    async def update_course_weights(course: Course) -> None:
        raise NotImplementedError()
