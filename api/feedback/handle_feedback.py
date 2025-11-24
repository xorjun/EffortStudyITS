import traceback
from fastapi.routing import APIRouter
from fastapi import Depends
from models.domain.feedback import handle_feedback
from feedback.schemas import Feedback_submission
from users.handle_users import current_active_verified_user
from db.db_connector_beanie import User

router = APIRouter()


@router.post("/feedback")
async def feedback(submission: Feedback_submission, user: User = Depends(current_active_verified_user)):
    try:
        return await handle_feedback(submission, user)
    except Exception as e:
        print(traceback.format_exc())
        {"feedback_id": 0, "status": 500, "message": f"{type(e)}: {str(e)}"}