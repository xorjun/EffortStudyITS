import json
import os
from models import model_manager
from models.model_manager import DEFAULT_MODEL_NAME
from courses.schemas import CourseValidationStatus
from copy import deepcopy
from db import database
import os


PRIVILEDGED_SETTINGS = ["course_settings", "course_settings_list", "course_parameters", "sample_settings"]

async def parse_course(dir, overwrite_params: bool):
    with open(dir+"/course.json", "r") as course_file:
        course_json = course_file.read()
    course_dict: dict = json.loads(course_json)
    course_unique_name = os.path.basename(dir)

    if course_dict.get("unique_name") is None:
        course_dict["unique_name"] = course_unique_name

    if "course_settings" not in course_dict.keys():
        course_dict["course_settings"] = {}

    if "course_unique_name" not in course_dict.keys():
        course_dict["course_settings"]["course_unique_name"] = course_dict["unique_name"]
    elif course_dict["course_settings"]["course_unique_name"] != course_dict["unique_name"]:
        raise Exception("Course Settings do not seem to have the same course_unique_name as course.")
    
    if isinstance(course_dict["curriculum"], dict):
        if not "topics" in course_dict.keys():
            raise Exception("Your curriculum looks like you want to structure it into topics. Please include the topics field as well.")
        if set(course_dict["topics"]) != set(course_dict["curriculum"].keys()):
            raise Exception("The topics do not match the curriculum.")

    if type(course_dict["course_settings"]) != list:

        if "pedagogical_model" not in course_dict["course_settings"].keys():
            course_dict["course_settings"]["pedagogical_model"] = DEFAULT_MODEL_NAME

        if "language_generation_model" not in course_dict.keys():
            course_dict["course_settings"]["language_generation_model"] = DEFAULT_MODEL_NAME


        course_dict["course_settings_list"] = [course_dict["course_settings"]]

        if "sample_settings" not in course_dict.keys():
            course_dict["sample_settings"] = [1]

    else: 
        course_dict["course_settings_list"] = course_dict["course_settings"]

        if "sample_settings" not in course_dict.keys():
            n = len(course_dict["course_settings"])
            course_dict["sample_settings"] = [1/n for i in range(0, n)]
    
    del course_dict["course_settings"]
    
    # check if course is new or updates existing
    # TODO check existance only once (gets checked again in create_course)
    old_course = await database.get_course(course_dict["unique_name"])
    
    # Clean course_dict of priviledged keywords if course already exists and overwriting is not allowed
    if not (overwrite_params or old_course is None):
        for key in PRIVILEDGED_SETTINGS:
            if key in course_dict.keys():
                course_dict[key] = deepcopy(getattr(old_course, key))
    
    status, msg = model_manager.validate_course(course_dict)
    if status in [CourseValidationStatus.Missing]:
        course_dict = model_manager.set_default_params(course_dict)
    if status in [CourseValidationStatus.No_Weights]:
        course_dict = model_manager.set_default_weights(course_dict)
    if status in [CourseValidationStatus.Faulty]:
        return status, msg
    
    #set visibility to "student by default"
    if not "visibility" in course_dict.keys():
        course_dict["visibility"] = "student"
    await database.create_course(course_dict)
    # if course updates another one, trigger learning of model
    if old_course != None:
        await model_manager.update_course_weights(course_dict)
    return status, msg