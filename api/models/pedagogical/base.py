from models.pedagogical.feedback.base import Base_step_feedback_module
from models.pedagogical.content_selection.base import Base_task_selector
from users.schemas import User
from submissions.schemas import Base_Submission


class Base_pedagogical_model():

    feedback_module: Base_step_feedback_module
    task_selector: Base_task_selector

    #Outer Loop
    async def select_task(self, user: User, topic: str = None):
        return await self.task_selector.select(user, topic)
    
    #Inner Loop
    async def provide_feedback(self, submission: Base_Submission):
        return await self.feedback_module.provide_feedback(submission)
