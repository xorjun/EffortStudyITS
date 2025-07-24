from courses.schemas import TaskType
from models.pedagogical.feedback.base import Base_step_feedback_module
from models.pedagogical.feedback.step_generator.prompt_llm_next_step import Prompt_llm_step_generator
from models.pedagogical.feedback.feedback_generator.identity import Identity_feedback_generator
from models.pedagogical.feedback.feedback_generator.add_llm_conceptual_feedback import LLM_conceptual_explanation_generator
from db import database


class LLM_prototype_feedback_module(Base_step_feedback_module):

    def __init__(self, feedback_type="both") -> None:
        self.step_generator = Prompt_llm_step_generator()
        #self.feedback_generator = Identity_feedback_generator()
        if feedback_type == "both":
            self.feedback_generator = LLM_conceptual_explanation_generator(textual_feedback_only=False)
        if feedback_type == "textual":
            self.feedback_generator = LLM_conceptual_explanation_generator(textual_feedback_only=True)
        if feedback_type == "code":
            self.feedback_generator = Identity_feedback_generator()

    async def get_feedback_available(self, task_type):
        settings = await database.get_settings()
        if settings.ollama_url == "" or task_type in [TaskType.MultipleChoice]:
            return False
        else:
            return True