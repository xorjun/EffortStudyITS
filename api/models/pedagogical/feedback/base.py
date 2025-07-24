from models.pedagogical.feedback.step_generator.base import Base_step_generator
from models.pedagogical.feedback.feedback_generator.base import Base_feedback_generator
from submissions.schemas import Base_Submission

class Base_step_feedback_module():

    step_generator = Base_step_generator()
    feedback_generator = Base_feedback_generator()

    async def provide_feedback(self, submission: Base_Submission):
        next_step = await self.step_generator.predict_next_step(submission)
        return await self.feedback_generator.generate_feedback(next_step, submission)
    
    async def provide_feedback_stream(self, submission: Base_Submission):
        raise Exception("Not Implemented!")

    async def get_feedback_available(self, task_type):
        raise NotImplementedError()