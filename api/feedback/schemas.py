from submissions.schemas import Base_Submission, Tested_Submission
from beanie import Document

class Feedback_submission(Base_Submission):

    class Settings: 
        name = "Submission"

class Evaluated_feedback_submission(Feedback_submission, Tested_Submission):

    # Default to empty string so legacy MongoDB documents written before these
    # fields were added don't fail Pydantic validation when an admin loads
    # /api/settings/study_metrics (which does a .find().to_list() over the
    # whole Submission collection and re-validates every doc).
    feedback_method: str = ""
    feedback: str = ""

    class Settings:
        name = "Submission"

class Url(Document):
    
    url: str