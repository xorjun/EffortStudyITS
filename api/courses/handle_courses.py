from fastapi import APIRouter, HTTPException, status, UploadFile
from fastapi import Depends
from courses.schemas import Course, CourseInfo, CourseEnrollment, CourseSelection, CourseSettings
from users.schemas import User
from users.handle_users import current_active_verified_user
from db import database
from random import randrange
import itertools
import numpy as np
from typing import List
import zipfile
from io import BytesIO
import shutil
import os
from courses.parse_tasks import parse_all_tasks
from courses.parse_courses import parse_course


router = APIRouter(prefix="/course")

@router.get("/get/{course_unique_name}")
async def get_course(course_unique_name, user: User = Depends(current_active_verified_user)) -> Course:
    course = await database.get_course(course_unique_name)
    if course_unique_name not in user.enrolled_courses:
        enrolled_courses = user.enrolled_courses.copy()
        enrolled_courses.append(course_unique_name)
        course_settings_index = np.where(np.random.multinomial(1, np.array(course.sample_settings)))[0]
        course_enrollment = CourseEnrollment(user_id=str(user.id), username=user.username,
                                             course_unique_name=course_unique_name,
                                             tasks_completed=[], tasks_attempted=[], completed=False,
                                             course_settings_index=int(course_settings_index))
                                             #rand_subdomain_orders=[-1])
        user_update_dict = {"enrolled_courses": enrolled_courses}
        await database.update_user(user, user_update_dict)
        await database.create_course_enrollment(course_enrollment)
    else:
        course_enrollment = await database.get_course_enrollment(user, course_unique_name)
    
    curriculum = course.curriculum
    
    course_settings_index = course_enrollment.course_settings_index
    course_settings = course.course_settings_list[course_settings_index]
    course = override_course_settings(course, course_settings)
    course.course_settings_list = [course_settings]

    return(course)


@router.get("/get_settings/{course_unique_name}")
async def get_course_settings(course_unique_name, user: User = Depends(current_active_verified_user)) -> Course:
    if (not "admin" in user.roles) and (not "tutor" in user.roles):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to access this resource"
        )
    course = await database.get_course(course_unique_name)
    return course

#TODO: Impelement course-ownership for tutors.
@router.post("/update_settings")
async def update_course_settings(course: Course, user: User = Depends(current_active_verified_user)):
    if (not "admin" in user.roles) and (not "tutor" in user.roles):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to access this resource"
        )
    else:
        db_course = await database.get_course(course.unique_name)
        db_course.course_settings_list = course.course_settings_list
        await database.update_course(db_course, {"course_settings_list": course.course_settings_list, 
                                                 "sample_settings": course.sample_settings})

def override_course_settings(course: Course, course_settings):
    #TODO: turn the course settings into an object and access values accordingly!
    base_settings = course.course_settings_list[0]
    for key in course_settings.keys():
        base_settings.update([(key, course_settings[key])])
    course.course_settings_list = None
    course.course_settings = base_settings
    return course

@router.get("/info")
async def get_course_info(User = Depends(current_active_verified_user)) -> CourseInfo:
    courses = await database.get_courses()
    course_list = [{"unique_name": course.unique_name, 
                    "display_name": course.display_name,
                     "number_tasks": len(list(itertools.chain(*course.curriculum))),
                      "domain": course.domain } for course in courses]
    course_info = CourseInfo(course_list=course_list)
    return course_info

@router.post("/select")
async def select_course(course_selection: CourseSelection, User = Depends(current_active_verified_user)):
    await database.update_user(User, {"current_course": course_selection.course_unique_name})


async def parse_task_folder(task_folder: str):
    db = database.db
    await parse_all_tasks(task_folder, db)


async def unzip_folder(file: UploadFile, temp_dir):
    if os.path.isdir(temp_dir):
        shutil.rmtree(temp_dir)
    contents = await file.read()
    byte_contents = bytes(contents)
    fp = BytesIO(byte_contents)
    with zipfile.ZipFile(fp, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)


#TODO: Upload von Task folder ist nicht user-friendly, weil man keine Kurs-folder hochladen kann.
#TODO: Upload sollte ein update der UI und aller Zustände triggern
@router.post("/update_tasks")
async def update_tasks(file: UploadFile, temp_dir="./temp", user: User = Depends(current_active_verified_user)):
    if (not "admin" in user.roles) and (not "tutor" in user.roles):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to access this resource"
        )
    await unzip_folder(file, temp_dir)
    try:
        if not "task_folder" in os.listdir(temp_dir):
            raise Exception("The folder that contains tasks should be named task_folder, it couldn't be found in the uploaded archive.")
        await parse_task_folder(os.path.join(temp_dir, "task_folder"))
    except Exception as e:
        shutil.rmtree(temp_dir)
        raise e
    shutil.rmtree(temp_dir)


@router.post("/upload_course")
async def upload_course(file: UploadFile, temp_dir="./temp", user: User = Depends(current_active_verified_user)):
    if (not "admin" in user.roles) and (not "tutor" in user.roles):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to access this resource"
        )
    await unzip_folder(file, temp_dir)
    course_name = os.listdir(temp_dir)
    if len(course_name) > 1:
        raise Exception("Uploaded archive should only contain a single course folder which should be named with the course_unique_name")
    course_name = os.path.basename(course_name[0])
    try:
        await parse_course(os.path.join(temp_dir, course_name))
        await parse_task_folder(os.path.join(temp_dir, course_name, "task_folder"))
    except Exception as e:
        shutil.rmtree(temp_dir)
        raise e
    shutil.rmtree(temp_dir)


async def get_course_enrolment():
    pass