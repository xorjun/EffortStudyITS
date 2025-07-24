import traceback
from models.domain.runs import run_code
from fastapi import APIRouter
from runs.schemas import Run_code_submission
from db.db_connector_beanie import User
from fastapi import Depends
from users.handle_users import current_active_verified_user

router = APIRouter()


@router.post("/run_code")
async def handle_run_code(submission: Run_code_submission, user: User = Depends(current_active_verified_user)):
    try:
        return await run_code(submission, user)
    except Exception as e:
        print(traceback.format_exc())
        {"run_id": 0, "status": 500, "message": f"{type(e)}: {str(e)}"}