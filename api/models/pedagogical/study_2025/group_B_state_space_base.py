from models.pedagogical.base_pedagogical import Base_pedagogical_model
from models.pedagogical.content_selection.first_uncompleted_task import First_uncompleted_task_selector
from models.pedagogical.feedback.state_space_feedback_module import State_space_feedback_module

class Group_B_state_space_base(Base_pedagogical_model):

    def __init__(self):
        self.task_selector = First_uncompleted_task_selector()
        self.feedback_module = State_space_feedback_module(selector="embedding", persistent_state_space="true")
        self.feedback_method = "State-space-based"
        self.task_summaries = {}