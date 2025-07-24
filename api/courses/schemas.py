from beanie import Document
from typing import Optional, Union
from enum import StrEnum


class CourseSettings(Document):
    course_unique_name: str
    feedback_init_time: Optional[int] = None
    feedback_cooldown: Optional[int] = None
    pedagogical_model: Optional[str] = None
    language_generation_model: Optional[str] = None
    #Override curriculum: should be optional
    #curriculum: Optional[list] = None

class Course(Document):
    curriculum: Union[dict, list]
    mandatory_curriculum: Optional[list] = None
    unique_name: str
    display_name: str
    #TODO: change naming to "topic"
    domain: str
    sub_domains: list
    competencies: Optional[list] = None
    #course_options: list
    course_settings: Optional[CourseSettings] = None
    course_settings_list: Optional[list]
    # Use p-array
    sample_settings: list
    # Model related
    q_matrix: Optional[dict] = None
    course_parameters: Optional[dict] = None
    default_topic: Optional[str] = None
    topics: Optional[list] = None

class CourseInfo(Document):
    course_list: list[dict]

class CourseEnrollment(Document):
    user_id: str
    username: str
    course_unique_name: str
    tasks_completed: list[str]
    tasks_attempted: list[str]
    #rand_subdomain_orders: list
    completed: bool
    course_settings_index: int

class CourseSelection(Document):
    course_unique_name: str

class TaskType(StrEnum):
    Function = "function"
    PlotFunction = "plot_function"
    Print = "print"
    MultipleChoice = "multiple_choice"