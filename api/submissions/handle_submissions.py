import traceback
from fastapi import APIRouter, Depends
from users.handle_users import current_active_verified_user
from db.db_connector_beanie import User
from submissions.schemas import Base_Submission
from models.domain.submissions.submissions import handle_submission

from db import database
from sys import __stdout__

router = APIRouter()

@router.post("/submit")
async def submit(submission: Base_Submission, user: User = Depends(current_active_verified_user)):
    try:
        return await handle_submission(submission, user)
    except Exception as e:
        print(traceback.format_exc())
        {"status": 500, "message": f"{type(e)}: {str(e)}"}
    
@router.get("/submission/feedback/{submission_id}")
async def send_feedback(submission_id):
    feedback = await database.get_submission(str(submission_id))
    return feedback
