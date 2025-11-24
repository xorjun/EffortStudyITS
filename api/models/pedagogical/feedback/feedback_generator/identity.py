from models.pedagogical.feedback.feedback_generator.base import Base_feedback_generator
from submissions.schemas import Base_Submission

class Identity_feedback_generator(Base_feedback_generator):

    async def generate_feedback(self, predicted_step: str, submission: Base_Submission):
        return predicted_step