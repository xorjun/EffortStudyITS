from models.knowledge_tracing.pfa_model import PFA_Model
from models.knowledge_tracing.kt_base import KT_Factor_Analysis_Model_Base
from models.pedagogical.content_selection.base_selector import Base_task_selector
from users.schemas import User
from db import database


class Skipping_task_selector(Base_task_selector):

    def __init__(self, model_class: KT_Factor_Analysis_Model_Base.__class__ = PFA_Model):
        self.learner_model: KT_Factor_Analysis_Model_Base.__class__ = model_class

    async def select(self, user: User, topic: str | None = None) -> str:
        """Task select method fo the ITS prototype. This is not a sophisticated Outer Loop, only very basic curriculum-aware task selection.

        Args:
            user (User): _description_
        """
        user_course_unique_name = user.current_course
        course = await database.get_course(user_course_unique_name)
        course_enrollment = await database.get_course_enrollment(user, user.current_course)

        if course_enrollment.completed:
            return "course completed"

        uncompleted_tasks = [task for task in course.get_local_curriculum(topic) if task not in course_enrollment.tasks_completed]

        if len(uncompleted_tasks) == 0:
            return "course completed"

        if course.domain == "Surveys":
            return uncompleted_tasks[0]
        
        
        probabilities = await self.learner_model.completion_probability(uncompleted_tasks, user, course)
        # iterate through tasks to find the first task with below 80% probability of completion
        for i, prob in enumerate(probabilities):
            if prob > 0.8 and uncompleted_tasks[i] not in course.mandatory_curriculum:
                return uncompleted_tasks[i]
        # default to returning last task
        return uncompleted_tasks[-1]
