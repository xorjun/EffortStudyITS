from submissions.schemas import Base_Submission, Tested_Submission
from beanie import Document

class Feedback_submission(Base_Submission):

    class Settings: 
        name = "Submission"

class Evaluated_feedback_submission(Feedback_submission, Tested_Submission):
    
    feedback_method: str
    feedback: str

    class Settings: 
        name = "Submission"

class Url(Document):
    
    url: str