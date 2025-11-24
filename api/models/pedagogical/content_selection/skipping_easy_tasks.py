from models.knowledge_tracing.pfa_model import PFA_Model
from models.knowledge_tracing.kt_base import KT_Factor_Analysis_Model_Base
from models.pedagogical.content_selection.base import Base_task_selector
from users.schemas import User
from db import database


class Skipping_task_selector(Base_task_selector):
    
    def __init__(self, model: KT_Factor_Analysis_Model_Base = PFA_Model):
        self.learner_model: KT_Factor_Analysis_Model_Base = model()

    async def select(self, user: User, topic: str = None):
        """Task select method fo the ITS prototype. This is not a sophisticated Outer Loop, only very basic curriculum-aware task selection.

        Args:
            user (User): _description_
        """
        user_course_unique_name = user.current_course
        course = await database.get_course(user_course_unique_name)
        course_enrollment = await database.get_course_enrollment(user, user.current_course)
        if course_enrollment.completed:
            return("course completed")
        user_completed_tasks = course_enrollment.tasks_completed

        curriculum, mandatory_tasks = self.get_curriculum(course)

        uncompleted_tasks = [curriculum_task for curriculum_task in curriculum if curriculum_task not in user_completed_tasks]
        if course.domain == "Surveys":
            return(uncompleted_tasks[0])
        
        await self.learner_model.set_user(user)
        # This can be handled by a switch to potentially handle different methods for other classes
        completion_probability = self.learner_model.completion_probability
        
        if ((completion_probability(uncompleted_tasks[0]) > 0.8) and (uncompleted_tasks[0] not in mandatory_tasks)):
            while ((completion_probability(uncompleted_tasks[0]) > 0.8) and (len(uncompleted_tasks) > 0) and (uncompleted_tasks[0] not in mandatory_tasks)):
                uncompleted_tasks.pop(0)

        self.learner_model.unset_user()
        return uncompleted_tasks[0]
