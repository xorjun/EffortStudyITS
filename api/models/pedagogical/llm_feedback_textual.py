from models.pedagogical.base import Base_pedagogical_model
from models.pedagogical.content_selection.first_uncompleted_task import First_uncompleted_task_selector
from models.pedagogical.feedback.llm_prototype_feedback_module import LLM_prototype_feedback_module

class LLM_feedback_textual_pedagogical_model(Base_pedagogical_model):

    def __init__(self):
        self.task_selector = First_uncompleted_task_selector()
        self.feedback_module = LLM_prototype_feedback_module(feedback_type="textual")
        self.feedback_method = "LLM-next-step"
        self.task_summaries = {}