
from models.pedagogical.prototype import Prototype_pedagogical_model
from models.pedagogical.skipping_tasks_pfa import Skipping_tasks_pfa_pedagogical_model
from models.pedagogical.llm_feedback_textual import LLM_feedback_textual_pedagogical_model
from models.pedagogical.llm_feedback_code import LLM_feedback_code_pedagogical_model
from users.schemas import User
from courses.schemas import Course
from db import database

from models.pedagogical.group_A_code_base import Group_A_code_base
from models.pedagogical.group_B_textual_base import Group_B_textual_base
from models.pedagogical.group_C_code_skipping import Group_C_code_skipping
from models.pedagogical.group_D_textual_skipping import Group_D_textual_skipping

class Model_manager():
    """Since the ITS should be a research platform that incorporates different methods for feedback and task selection, the model manager
    aims to simplify the use of varying implementations of the pedagogical, domain and learner model. 
    """
    
    def __init__(self):
        """In the constructor all variants of models should be registered (and instantiated) for later select^ion.
        """
        self.prototype = Prototype_pedagogical_model()
        self.skipping_pfa = Skipping_tasks_pfa_pedagogical_model()
        self.prototype_textual_feedback = LLM_feedback_textual_pedagogical_model()
        self.prototype_code_feedback = LLM_feedback_code_pedagogical_model()
        self.default = Skipping_tasks_pfa_pedagogical_model()
        
        self.group_A = Group_A_code_base()
        self.group_B = Group_B_textual_base()
        self.group_C = Group_C_code_skipping()
        self.group_D = Group_D_textual_skipping()

    async def pedagogical_model(self, user: User):
        course_unique_name = user.current_course
        course_settings = await database.get_course_settings_for_user(user.id, course_unique_name)
        model_name = course_settings["pedagogical_model"]
        if model_name is None:
            return self.default
        try:
            return getattr(self, model_name)
        except AttributeError as e:
            print("Warning: Pedagogical Model {model_name} not known, using default.")
            return self.default
    
    async def learner_model(self):
        raise Exception("Not implemented!")
