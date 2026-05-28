import asyncio
import os
import sys
import traceback

from beanie import init_beanie

# Add /app to path so imports work in the container.
sys.path.insert(0, "/app")
os.chdir("/app")

from db import database as db_connection
from users.schemas import User, GlobalAccountList
from submissions.schemas import Base_Submission, Tested_Submission
from courses.schemas import Course, CourseInfo, CourseEnrollment, CourseSelection, CourseSettings
from tasks.schemas import Task, PackedStateSpace, PackedState
from attempts.schemas import Attempt, AttemptState, NestedAttemptState
from system.schemas import AppSettings
from feedback.schemas import Url
from surveys.schemas import Survey
from courses.parse_courses import parse_course
from courses.handle_courses import parse_task_folder

COURSES_DIR = "/tmp/courses"
ALLOWED_COURSES = {"activity_tracker", "activity_tracker_simplified", "Intro_to_PY", "ITS_Course"}


async def bootstrap_beanie() -> None:
    await init_beanie(
        database=db_connection.db,
        document_models=[
            User,
            Base_Submission,
            Tested_Submission,
            Course,
            CourseInfo,
            CourseEnrollment,
            CourseSelection,
            CourseSettings,
            Task,
            Attempt,
            AttemptState,
            NestedAttemptState,
            AppSettings,
            Url,
            GlobalAccountList,
            Survey,
            PackedStateSpace,
            PackedState,
        ],
    )


async def main() -> None:
    await bootstrap_beanie()

    for course_name in sorted(os.listdir(COURSES_DIR)):
        if course_name not in ALLOWED_COURSES:
            continue
        course_dir = os.path.join(COURSES_DIR, course_name)
        if not os.path.isdir(course_dir):
            continue

        course_json = os.path.join(course_dir, "course.json")
        if not os.path.exists(course_json):
            print(f"SKIP {course_name}: no course.json")
            continue

        try:
            await parse_course(course_dir, overwrite_params=True)
            print(f"OK course: {course_name}")
        except BaseException as e:
            print(f"ERR course {course_name}: {type(e).__name__}: {e}")
            traceback.print_exc()
            continue

        task_dir = os.path.join(course_dir, "task_folder")
        if os.path.isdir(task_dir):
            try:
                await parse_task_folder(task_dir)
                print(f"OK tasks: {course_name}")
            except BaseException as e:
                print(f"ERR tasks {course_name}: {type(e).__name__}: {e}")
                traceback.print_exc()


asyncio.run(main())
