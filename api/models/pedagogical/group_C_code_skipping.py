from models.pedagogical.base import Base_pedagogical_model
from models.pedagogical.content_selection.first_uncompleted_task import First_uncompleted_task_selector
from models.pedagogical.feedback.llm_prototype_feedback_module import LLM_prototype_feedback_module
from models.pedagogical.content_selection.skipping_easy_tasks import Skipping_task_selector

class Group_C_code_skipping(Base_pedagogical_model):

    def __init__(self):
        self.task_selector = Skipping_task_selector()
        self.feedback_module = LLM_prototype_feedback_module(feedback_type="code")
        self.feedback_method = "LLM-next-step"
        self.task_summaries = {}