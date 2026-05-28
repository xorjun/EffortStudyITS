import traceback
from fastapi.routing import APIRouter
from fastapi import Depends, HTTPException
from models.domain.feedback import handle_feedback
from feedback.schemas import Feedback_submission
from users.handle_users import current_active_verified_user
from db.db_connector_beanie import User

router = APIRouter()


@router.post("/feedback")
async def feedback(submission: Feedback_submission, user: User = Depends(current_active_verified_user)):
    try:
        return await handle_feedback(submission, user)
    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Feedback generation failed.")