
from models.pedagogical.content_selection.base_selector import Base_task_selector
from models.pedagogical.base_pedagogical import Base_pedagogical_model
from models.pedagogical.model_variants import (
    Prototype_pedagogical_model,
    Skipping_tasks_pfa_pedagogical_model,
    LLM_feedback_textual_pedagogical_model,
    LLM_feedback_code_pedagogical_model,
    Group_A_llm_base,
    Group_C_llm_skipping,
    State_space_feedback_pedagogical_model,
    Simple_state_space_feedback_pedagogical_model,
    Group_B_state_space_base,
    Group_D_state_space_skipping,
    STATE_SPACE_AVAILABLE,
    STATE_SPACE_IMPORT_ERROR,
)
from users.schemas import User
from db import database

import warnings


DEFAULT_PEDAGOGICAL_MODEL = "default"
DEFAULT_LANGUAGE_MODEL = "default"

class Model_Manager():
    """Since the ITS should be a research platform that incorporates different methods for feedback and task selection, the model manager
    aims to simplify the use of varying implementations of the pedagogical, domain and learner model. 
    """
    
    def __init__(self):
        """In the constructor all variants of models should be registered (and instantiated) for later selection.
        """
        
        self.pedagogical_models: dict[str, Base_pedagogical_model] = {
            "prototype": Prototype_pedagogical_model(),
            "skipping_pfa": Skipping_tasks_pfa_pedagogical_model(),
            "prototype_textual_feedback": LLM_feedback_textual_pedagogical_model(),
            "prototype_code_feedback": LLM_feedback_code_pedagogical_model(),
            "group_A": Group_A_llm_base(),
            "group_C": Group_C_llm_skipping(),
        }
        if STATE_SPACE_AVAILABLE:
            self.pedagogical_models.update({
                "state-space": State_space_feedback_pedagogical_model(),
                "simple-state-space": Simple_state_space_feedback_pedagogical_model(),
                "group_B": Group_B_state_space_base(),
                "group_D": Group_D_state_space_skipping(),
            })
        elif STATE_SPACE_IMPORT_ERROR is not None:
            warnings.warn(
                f"State-space pedagogical models are unavailable in this environment: {STATE_SPACE_IMPORT_ERROR}",
                UserWarning,
            )
        self.pedagogical_default = self.pedagogical_models["prototype"]
        
        # TODO instantiate knowledge tracing and selector models here for better performance, but requires more refactoring

    
    def get_pedagogical_model(self, model_name: str = DEFAULT_PEDAGOGICAL_MODEL) -> Base_pedagogical_model:
        if model_name == DEFAULT_PEDAGOGICAL_MODEL:
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

    def get_learner_models(self) -> list[Base_task_selector]:
        # TODO filter unneccessary duplicates
        #return [model.task_selector for model in self.pedagogical_models.values()]
        
        # Doing it manually for now, to avoid unneccessary duplicates
        return [
            self.get_pedagogical_model("skipping_pfa").task_selector
        ]