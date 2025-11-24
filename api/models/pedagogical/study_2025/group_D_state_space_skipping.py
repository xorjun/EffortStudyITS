from models.pedagogical.base_pedagogical import Base_pedagogical_model
from models.pedagogical.feedback.state_space_feedback_module import State_space_feedback_module
from models.pedagogical.content_selection.skipping_easy_tasks import Skipping_task_selector
from models.knowledge_tracing.pfa_model import PFA_Model

class Group_D_state_space_skipping(Base_pedagogical_model):

    def __init__(self):
        self.task_selector = Skipping_task_selector(PFA_Model)
        self.feedback_module = State_space_feedback_module(selector="embedding", persistent_state_space="true")
        self.feedback_method = "State-space-based"
        self.task_summaries = {}