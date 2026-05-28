from fastapi import APIRouter, Depends
from fastapi import HTTPException
from users.schemas import User
from users.handle_users import current_active_verified_user
from models import model_manager
from typing import Optional

from db import database

router = APIRouter()

@router.get("/task/for_user/")
async def get_task_for_user(topic: Optional[str] = None, user: User = Depends(current_active_verified_user)):
    pedagogical_model = await model_manager.get_pedagogical_model_by_user(user)
    task_unique_name = await pedagogical_model.select_task(user, topic)
    if task_unique_name == "course completed":
        return({"unique_name": "course completed", "task": ""})
    return(await read_task(task_unique_name, user))


@router.get("/task/for_user/{topic}")
async def get_task_for_user_with_topic(topic: str, user: User = Depends(current_active_verified_user)):
    return await get_task_for_user(topic, user)


@router.get("/task/by_name/{unique_name}")
async def read_task(unique_name, user: User = Depends(current_active_verified_user)):
    #if task_id =="1":
    #    pedagogical_model.task_id = 1
    task = await database.get_task(unique_name)
    task_description = task.task
    if task_description == "":
        raise HTTPException(status_code=400, detail="Task not known")
    pedagogical_model = await model_manager.get_pedagogical_model_by_user(user)
    course_settings = await database.get_course_settings_for_user(user.id, user.current_course)
    ai_assistance_enabled = course_settings.get("ai_assistance_mode", "disabled") == "hints"
    return({
        "unique_name": unique_name, 
        "task": task_description, 
        "type": task.type, 
        "prefix": task.prefix, 
        "arguments": task.arguments, 
        "additional_files": task.additional_files,
        "possible_choices": task.possible_choices,
        "feedback_available": ai_assistance_enabled and await pedagogical_model.feedback_module.get_feedback_available(task.type)
    })


@router.get("/task/status/{course_unique_name}/{topic}")
async def get_task_status(course_unique_name, topic: Optional[str] = None, user: User = Depends(current_active_verified_user)):
    course_enrollment = await database.get_course_enrollment(user, course_unique_name)
    course = await database.get_course(course_unique_name)
    if not topic is None:
        local_curriculum = course.curriculum[topic]
    else:
        local_curriculum = course.curriculum
    task_status_dict = {}
    completed_tasks = course_enrollment.tasks_completed
    attempted_tasks = course_enrollment.tasks_attempted
    for task in local_curriculum:
        if task in completed_tasks:
            task_status_dict[task] = "completed"
        elif task in attempted_tasks:
            task_status_dict[task] = "attempted"
        else:
            task_status_dict[task] = "not attempted"
    return({"local_curriculum": local_curriculum, "task_status_dict": task_status_dict})
