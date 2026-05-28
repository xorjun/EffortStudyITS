from fastapi import APIRouter, HTTPException, status, UploadFile, Depends
from courses.schemas import (
    Course,
    CourseInfo,
    CourseEnrollment,
    CourseSelection,
    CourseSettings,
    CourseValidationError,
)
from courses.parse_tasks import parse_all_tasks
from courses.parse_courses import parse_course
from users.schemas import User, UserLevel
from users.handle_users import current_active_verified_user
from db import database
from io import BytesIO
import numpy as np
import zipfile
import shutil
import os


router = APIRouter(prefix="/course")


@router.get("/get/{course_unique_name}")
async def get_course(
    course_unique_name, user: User = Depends(current_active_verified_user)
) -> Course:
    course = await database.get_course(course_unique_name)
    user_level = max(user.roles)
    course_level = course.visibility
    if user_level < course_level:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to access this resource",
        )
    if course_unique_name not in user.enrolled_courses:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not enrolled in this course",
        )
    else:
        course_enrollment = await database.get_course_enrollment(
            user, course_unique_name
        )
    course_settings_index = course_enrollment.course_settings_index
    # Remove all settings not for the current user
    course.course_settings_list = [course.course_settings_list[course_settings_index]]
    # course_settings = course.course_settings_list[course_settings_index]
    # course = override_course_settings(course, course_settings)
    # course.course_settings_list = [course_settings]
    return course


@router.put("/enroll/{course_unique_name}")
async def enroll(
    course_unique_name, user: User = Depends(current_active_verified_user)
):
    course = await database.get_course(course_unique_name)
    user_level = max(user.roles)
    course_level = course.visibility
    if user_level < course_level:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to access this resource",
        )
    enrolled_courses = user.enrolled_courses.copy()
    if course_unique_name in enrolled_courses:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Course enrollment already present",
        )
    enrolled_courses.append(course_unique_name)
    course_settings_index = np.where(
        np.random.multinomial(1, np.array(course.sample_settings))
        )[0][0]
    course_enrollment = CourseEnrollment(
        user_id=str(user.id),
        username=user.username,
        course_unique_name=course_unique_name,
        tasks_completed=[],
        tasks_attempted=[],
        completed=False,
        course_settings_index=int(course_settings_index),
    )
    # rand_subdomain_orders=[-1])
    user_update_dict = {"enrolled_courses": enrolled_courses}
    await database.update_user(user, user_update_dict)
    await database.create_course_enrollment(course_enrollment)


@router.get("/get_settings/{course_unique_name}")
async def get_course_settings(
    course_unique_name, user: User = Depends(current_active_verified_user)
) -> Course:
    if max(user.roles) < UserLevel.tutor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to access this resource",
        )
    course = await database.get_course(course_unique_name)
    return course


# TODO: Impelement course-ownership for tutors.
@router.post("/update_settings")
async def update_course_settings(
    course: Course, user: User = Depends(current_active_verified_user)
):
    if max(user.roles) < UserLevel.tutor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to access this resource",
        )
    else:
        db_course = await database.get_course(course.unique_name)
        db_course.course_settings_list = course.course_settings_list
        await database.update_course(
            db_course,
            {
                "course_settings_list": course.course_settings_list,
                "sample_settings": course.sample_settings,
                "visibility": course.visibility,
            },
        )


@router.get("/enrolled_courses")
async def get_enrolled_courses(
    user: User = Depends(current_active_verified_user),
) -> CourseInfo:
    courses = await database.get_courses()
    user_level = max(user.roles)
    course_list = []
    for course in courses:
        if course.visibility <= user_level and course.unique_name in user.enrolled_courses:
            course_list.append(
                {
                    "unique_name": course.unique_name,
                    "display_name": course.display_name,
                    "number_tasks": len(course.get_local_curriculum()),
                    "domain": course.domain,
                }
            )
    course_info = CourseInfo(course_list=course_list)
    return course_info


@router.get("/info")
async def get_course_info(
    user: User = Depends(current_active_verified_user),
) -> CourseInfo:
    courses = await database.get_courses()
    user_level = max(user.roles)
    course_list = []
    for course in courses:
        if course.visibility <= user_level and (not course.unique_name in user.enrolled_courses):
            course_list.append(
                {
                    "unique_name": course.unique_name,
                    "display_name": course.display_name,
                    "number_tasks": len(course.get_local_curriculum()),
                    "domain": course.domain,
                }
            )
    course_info = CourseInfo(course_list=course_list)
    return course_info


@router.post("/select")
async def select_course(
    course_selection: CourseSelection, User=Depends(current_active_verified_user)
):
    await database.update_user(
        User, {"current_course": course_selection.course_unique_name}
    )


async def parse_task_folder(task_folder: str):
    db = database.db
    await parse_all_tasks(task_folder, db)


async def unzip_folder(file: UploadFile, temp_dir):
    if os.path.isdir(temp_dir):
        shutil.rmtree(temp_dir)
    contents = await file.read()
    byte_contents = bytes(contents)
    fp = BytesIO(byte_contents)
    with zipfile.ZipFile(fp, "r") as zip_ref:
        zip_ref.extractall(temp_dir)
    course_name = os.listdir(temp_dir)
    if len(course_name) > 1:
        raise CourseValidationError(
            "Uploaded archive should only contain a single course folder which should be named with the course_unique_name"
        )
    return os.path.basename(course_name[0])


# TODO: Upload von Task folder ist nicht user-friendly, weil man keine Kurs-folder hochladen kann.
# TODO: Upload sollte ein update der UI und aller Zustände triggern
@router.post("/update_tasks")
async def update_tasks(
    file: UploadFile,
    temp_dir="./temp",
    user: User = Depends(current_active_verified_user),
):
    if max(user.roles) < UserLevel.tutor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to access this resource",
        )
    await unzip_folder(file, temp_dir)
    try:
        if not "task_folder" in os.listdir(temp_dir):
            raise Exception(
                "The folder that contains tasks should be named task_folder, it couldn't be found in the uploaded archive."
            )
        await parse_task_folder(os.path.join(temp_dir, "task_folder"))
    except Exception as e:
        shutil.rmtree(temp_dir)
        raise e
    shutil.rmtree(temp_dir)


@router.post("/upload_course")
async def upload_course(
    file: UploadFile,
    temp_dir="./temp",
    overwrite: bool = False,
    user: User = Depends(current_active_verified_user),
):
    if max(user.roles) < UserLevel.tutor:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Not authorized to access this resource"
        )
    course_name = await unzip_folder(file, temp_dir)
    try:
        await parse_course(os.path.join(temp_dir, course_name), overwrite)
        await parse_task_folder(os.path.join(temp_dir, course_name, "task_folder"))
    except CourseValidationError as err:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(err))
    finally:
        shutil.rmtree(temp_dir)


async def get_course_enrolment():
    pass
