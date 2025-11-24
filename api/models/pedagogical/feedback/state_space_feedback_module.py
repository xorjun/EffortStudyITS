from courses.schemas import TaskType
from models.pedagogical.feedback.base import Base_step_feedback_module
from models.pedagogical.feedback.step_generator.synthetic_state_space_step import Synthetic_state_space_step_generator
from db import database
from models.pedagogical.feedback.step_generator.state_space import base_selector, rule_based_state_space, embedding_selector
from models.pedagogical.feedback.feedback_generator.identity import Identity_feedback_generator
from models.pedagogical.feedback.feedback_generator.add_llm_conceptual_feedback import LLM_conceptual_explanation_generator

class State_space_feedback_module(Base_step_feedback_module):

    def __init__(self, selector="embedding", persistent_state_space: bool=True) -> None:
        if selector == "embedding":
            self.step_selector = embedding_selector.Embedding_Selector()
        else:
            self.step_selector = base_selector.Base_next_step_selector()
        self.step_generator = Synthetic_state_space_step_generator(self.step_selector, persistent_state_space)
        self.feedback_generator = LLM_conceptual_explanation_generator(textual_feedback_only=False)

    async def get_feedback_available(self, task_type):
        settings = await database.get_settings()
        if settings.api_url == "" or task_type in [TaskType.MultipleChoice]:
            return False
        else:
            return True
