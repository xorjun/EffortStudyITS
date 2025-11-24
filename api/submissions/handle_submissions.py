import traceback
from fastapi import APIRouter, Depends
from courses.schemas import TaskType
from users.handle_users import current_active_verified_user
from db.db_connector_beanie import User
from submissions.schemas import Base_Submission
from models.domain.submissions.submissions import handle_submission, mark_task_completed

from db import database
from sys import __stdout__

router = APIRouter()

@router.post("/submit")
async def submit(submission: Base_Submission, user: User = Depends(current_active_verified_user)):
    try:
        return await handle_submission(submission, user)
    except Exception as e:
        print(traceback.format_exc())
        return {"status": 500, "message": f"{type(e)}: {str(e)}"}
    
@router.get("/submission/feedback/{submission_id}")
async def send_feedback(submission_id):
    feedback = await database.get_submission(str(submission_id))
    return feedback

# Temporary
@router.post("/mark_solved/{task_unique_name}")
async def mark_solved(task_unique_name: str, user: User = Depends(current_active_verified_user)):
    # only allow plot functions to be marked as solved via this
    task = await database.get_task(task_unique_name)
    if task.type in [TaskType.PlotFunction]:
        return await mark_task_completed(task_unique_name, user)
    else:
        return {"status": 403, "message": "Marking as solved is only allowed to task type 'PlotFunctuon'."}