import uvicorn
from db import db_connector_beanie, database
from fastapi import FastAPI, Depends, Request
from models import model_manager
from submissions import handle_submissions
from attempts import handle_attempts
from submissions.schemas import Base_Submission, Tested_Submission
from tasks import handle_tasks
from feedback import handle_feedback
from courses import handle_courses
from skills import handle_skills
from surveys import handle_surveys
from surveys.schemas import Survey
from fastapi.middleware.cors import CORSMiddleware
from users import handle_users
from users import schemas as user_schemas
from courses.schemas import Course, CourseInfo, CourseEnrollment, CourseSelection, CourseSettings
from tasks.schemas import Task
from attempts.schemas import Attempt, AttemptState, NestedAttemptState
from beanie import init_beanie
from tasks.schemas import PackedStateSpace, PackedState
from users.schemas import User
from config import config
from runs import handle_runs
from system import retrieve_info
from system import handle_settings
import time
import asyncio
from fastapi.responses import JSONResponse
from starlette.status import HTTP_504_GATEWAY_TIMEOUT
from system.schemas import AppSettings, FinalPreviewLink
from feedback.schemas import Url
from models.domain.skill_weights_pfa_update import update_skill_parameters
from apscheduler.triggers.interval import IntervalTrigger  
from apscheduler.schedulers.asyncio import AsyncIOScheduler  
from contextlib import asynccontextmanager
from asyncio import run



REQUEST_TIMEOUT_ERROR = 45  # Threshold


#Api prefix
prefix = "/api"

app = FastAPI(docs_url=f'{prefix}/docs',
              redoc_url=f'{prefix}/redoc',
              openapi_url=f'{prefix}/openapi.json')


# Adding a middleware returning a 504 error if the request processing time is above a certain threshold
@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    start_time = time.time()
    try:
        return await asyncio.wait_for(call_next(request), timeout=REQUEST_TIMEOUT_ERROR)

    except asyncio.TimeoutError:
        process_time = time.time() - start_time
        return JSONResponse({'detail': 'Request processing time excedeed limit',
                             'processing_time': process_time},
                            status_code=HTTP_504_GATEWAY_TIMEOUT)


app.include_router(handle_submissions.router, prefix=f"{prefix}")
app.include_router(handle_tasks.router, prefix=f"{prefix}")
app.include_router(handle_feedback.router, prefix=f"{prefix}")
app.include_router(handle_attempts.router, prefix=f"{prefix}")
app.include_router(handle_courses.router, prefix=f"{prefix}")
app.include_router(handle_skills.router, prefix=f"{prefix}")
app.include_router(handle_runs.router, prefix=f"{prefix}/run")
app.include_router(retrieve_info.router, prefix=f"{prefix}/info")
app.include_router(handle_settings.router, prefix=f"{prefix}/settings")
app.include_router(handle_surveys.router, prefix=f"{prefix}/surveys")

# User Router and database setup
app.include_router(
    handle_users.fastapi_users.get_auth_router(handle_users.auth_backend,
                                               requires_verification=False), prefix=f"{prefix}/auth/jwt", tags=["auth"]
)
app.include_router(
    handle_users.fastapi_users.get_register_router(user_schemas.UserRead, user_schemas.UserCreate),
    prefix=f"{prefix}/auth",
    tags=["auth"],
)
app.include_router(
    handle_users.fastapi_users.get_reset_password_router(),
    prefix=f"{prefix}/auth",
    tags=["auth"],
)
app.include_router(
    handle_users.fastapi_users.get_verify_router(user_schemas.UserRead),
    prefix=f"{prefix}/auth",
    tags=["auth"],
)
app.include_router(
    handle_users.fastapi_users.get_users_router(user_schemas.UserRead, user_schemas.UserUpdate),
    prefix=f"{prefix}/users",
    tags=["users"],
)

@app.get(f"{prefix}/authenticated-route")
async def authenticated_route(user: User = Depends(handle_users.current_active_user)):
    return {"message": f"Hello {user.email}!"}

@app.on_event("startup")
async def on_startup():

    await init_beanie(
        database=db_connection_beanie.db,
        document_models=[
            User, Base_Submission, Tested_Submission,
            Course, CourseInfo, CourseEnrollment, CourseSelection, CourseSettings,
                            Task, Attempt, AttemptState, NestedAttemptState, AppSettings, FinalPreviewLink, Url,
            user_schemas.GlobalAccountList, Survey, PackedStateSpace, PackedState
        ],
    )
    await initialize_settings(db_connection_beanie)
    await initialize_global_accounts_list(db_connection_beanie)
    #async def scheduled_jobs():
    scheduler = AsyncIOScheduler()
    # TODO implement trigger time as global admin setting
    trigger = IntervalTrigger(hours=1)
    scheduler.add_job(course_parameter_update, trigger)
    scheduler.start()
    #loop = asyncio.get_event_loop()
    #a1 = loop.create_task(get())
    #loop.run_until_complete(a1)

@app.on_event("shutdown")
async def shutdown_event():
    try:
        from services.text_embedding.embedding_model_manager import embedding_model_manager
    except ModuleNotFoundError:
        return
    embedding_model_manager.cleanup()

async def course_parameter_update():
    # TODO: schedule the updates of the course: exact timing not decided yet
    courses = await database.get_courses()
    for course in courses:
        await course.trigger_model_update()


origins = ["http://localhost:4200", "http://localhost:8080",
           "http://localhost", "https://localhost"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Check connection status
@app.get(f"{prefix}/status")
async def get_status():
    print("Status requested")
    return {"message": "Connected!"}

async def initialize_settings(database):
    #TODO: Enable initialization of settings via optional environment variables
    settings = AppSettings(
        api_url=config.llm_api_url,
        api_key=config.llm_api_key or None,
        api_type=config.llm_api_type,
        pedagogical_system_prompt="",
        email_whitelist=[".*"],
    )
    await database.create_settings(settings)
    current_settings = await database.get_settings()
    update_dict = {}
    if not current_settings.api_type and config.llm_api_type:
        update_dict["api_type"] = config.llm_api_type
    if not current_settings.api_url and config.llm_api_url:
        update_dict["api_url"] = config.llm_api_url
    if not current_settings.api_key and config.llm_api_key:
        update_dict["api_key"] = config.llm_api_key
    if update_dict:
        await database.update_settings(update_dict)

async def initialize_global_accounts_list(database):
    global_accounts_list = user_schemas.GlobalAccountList(hashed_email_list=[])
    await database.create_global_accounts_list(global_accounts_list)


""" def parse_cl_arguments():
    parser = argparse.ArgumentParser(description="Command-line argument parser for database network.")
    # Add the --database-network argument with a default value of "localhost"
    parser.add_argument("--database-network", default="localhost", help="Specify the database network address")
    args = parser.parse_args()
    return args """

if __name__ == "__main__":
    database_host = config.database_host
    db_connection_beanie = db_connector_beanie.database(database_host=database_host, 
                                                        database_user=config.database_usr, database_pwd=config.database_pwd)

    uvicorn.run(app, host="0.0.0.0", port=8000, )


# -- SPA static file serving (standalone Docker image) --
# When STATIC_DIR is set, FastAPI serves the pre-built Angular frontend.
# API routes (/api/*) take priority; everything else falls back to index.html.
import os as _os
_STATIC_DIR = _os.environ.get("STATIC_DIR")
if _STATIC_DIR and _os.path.isdir(_STATIC_DIR):
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=_STATIC_DIR, html=True), name="spa")
