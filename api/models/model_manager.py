
from models.pedagogical.content_selection.base import Base_task_selector
from models.pedagogical.content_selection.skipping_easy_tasks import Skipping_task_selector
from courses.schemas import Course, CourseValidationStatus
from models.pedagogical.base_pedagogical import Base_pedagogical_model
from models.pedagogical.prototype import Prototype_pedagogical_model
from models.pedagogical.skipping_tasks_pfa import Skipping_tasks_pfa_pedagogical_model
from models.pedagogical.llm_feedback_textual import LLM_feedback_textual_pedagogical_model
from models.pedagogical.llm_feedback_code import LLM_feedback_code_pedagogical_model
from models.pedagogical.state_space_feedback import State_space_feedback_pedagogical_model, Simple_state_space_feedback_pedagogical_model
from users.schemas import User
from db import database

from models.pedagogical.study_2025.group_A_llm_base import Group_A_llm_base
from models.pedagogical.study_2025.group_B_state_space_base import Group_B_state_space_base
from models.pedagogical.study_2025.group_C_llm_skipping import Group_C_llm_skipping
from models.pedagogical.study_2025.group_D_state_space_skipping import Group_D_state_space_skipping

import warnings


DEFAULT_MODEL_NAME = "default"

class Model_Manager():
    """Since the ITS should be a research platform that incorporates different methods for feedback and task selection, the model manager
    aims to simplify the use of varying implementations of the pedagogical, domain and learner model. 
    """
    
    def __init__(self):
        """In the constructor all variants of models should be registered (and instantiated) for later selection.
        """
        
        self.pedagogical_models = {
            "prototype": Prototype_pedagogical_model(),
            "skipping_pfa": Skipping_tasks_pfa_pedagogical_model(),
            "prototype_textual_feedback": LLM_feedback_textual_pedagogical_model(),
            "prototype_code_feedback": LLM_feedback_code_pedagogical_model(),
            "state-space": State_space_feedback_pedagogical_model(),
            "simple-state-space": Simple_state_space_feedback_pedagogical_model(),
            "group_A": Group_A_llm_base(),
            "group_B": Group_B_state_space_base(),
            "group_C": Group_C_llm_skipping(),
            "group_D": Group_D_state_space_skipping(),
        }
        self.pedagogical_default = self.pedagogical_models["skipping_pfa"]
        
        # TODO instantiate knowledge tracing and selector models here for better performance, but requires more refactoring

    
    def get_pedagogical_model(self, model_name: str = None) -> Base_pedagogical_model:
        if model_name is None or model_name == DEFAULT_MODEL_NAME:
            return self.pedagogical_default
        try:
            return self.pedagogical_models[model_name]
        except KeyError as e:
            warnings.warn(f"Pedagogical Model '{model_name}' not known, using default.", UserWarning)
            return self.pedagogical_default

    async def get_pedagogical_model_by_user(self, user: User) -> Base_pedagogical_model:
        course_unique_name = user.current_course
        course_settings = await database.get_course_settings_for_user(user.id, course_unique_name)
        model_name = course_settings["pedagogical_model"]
        return self.get_pedagogical_model(model_name)
    
    def get_selectors(self, course: Course | dict):
        if type(course) == Course:
            course_settings_list = course.course_settings_list
        elif type(course) == dict:
            course_settings_list = course.get("course_settings_list", [])
        
        selectors = []
        for setting in course_settings_list:
            model_name = setting.get("pedagogical_model", DEFAULT_MODEL_NAME)
            model: Base_pedagogical_model = self.get_pedagogical_model(model_name)
            task_selector: Base_task_selector = model.task_selector
            selectors.append(task_selector)
        return selectors
    
    async def update_course_weights(self, course: Course | list = None):
        selectors = self.get_selectors(course)
        
        for task_selector in selectors:
            # newly added selectors might need to be added here
            # TODO surely this can be managed more robustly
            if type(task_selector) == Skipping_task_selector:
                await task_selector.learner_model.update_course_weights(course)

    def validate_course(self, course: Course | dict):
        selectors = self.get_selectors(course)
        for task_selector in selectors:
            # newly added selectors might need to be added here
            # TODO surely this can be managed more robustly
            if type(task_selector) == Skipping_task_selector:
                status, error_msg = task_selector.learner_model.validate_course(course)
            else:
                status, error_msg = CourseValidationStatus.Valid, ""
            if status != CourseValidationStatus.Valid:
                return status, error_msg
        return CourseValidationStatus.Valid, "" # if all tests returned valid or no tests had to be made
    
    def set_default_params(self, course: Course | dict):
        selectors = self.get_selectors(course)
        for task_selector in selectors:
            # newly added selectors might need to be added here
            # TODO surely this can be managed more robustly
            if type(task_selector) == Skipping_task_selector:
                course = task_selector.learner_model.set_default_params(course)
        return course

    def set_default_weights(self, course: Course | dict):
        selectors = self.get_selectors(course)
        for task_selector in selectors:
            # newly added selectors might need to be added here
            # TODO surely this can be managed more robustly
            if type(task_selector) == Skipping_task_selector:
                course = task_selector.learner_model.set_default_weights(course)
        return course
