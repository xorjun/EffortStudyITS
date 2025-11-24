from submissions.schemas import Base_Submission

class Base_step_generator():
    
    def predict_next_step(self, submission: Base_Submission):
        raise NotImplementedError()