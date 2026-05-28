import os
import json

from courses.schemas import AIAssistanceMode, Course, CourseValidationError
from db import database
from jsonschema import validate
from jsonschema import ValidationError as JsonValidationError
from pydantic import ValidationError as PyValidationError
from models.model_manager import DEFAULT_PEDAGOGICAL_MODEL, DEFAULT_LANGUAGE_MODEL
from copy import deepcopy


PRIVILEDGED_SETTINGS = [
    "course_parameters",
    "course_settings_list",
    "sample_settings",
]
DEFAULT_DOMAIN = "Unknown"
DEFAULT_FEEDBACK_INIT_TIME = 60
DEFAULT_FEEDBACK_COOLDOWN = 30
DEFAULT_VISIBILITY = "student"
DEFAULT_AI_ASSISTANCE_MODE = AIAssistanceMode.Disabled.value


def set_course_settings_defaults(settings_dict: dict) -> None:
    settings_dict.setdefault("feedback_init_time", DEFAULT_FEEDBACK_INIT_TIME)
    settings_dict.setdefault("feedback_cooldown", DEFAULT_FEEDBACK_COOLDOWN)
    settings_dict.setdefault("pedagogical_model", DEFAULT_PEDAGOGICAL_MODEL)
    settings_dict.setdefault("language_generation_model", DEFAULT_LANGUAGE_MODEL)
    settings_dict.setdefault("ai_assistance_mode", DEFAULT_AI_ASSISTANCE_MODE)


# Parses a course and saves it to the database.
# Dir: directory of the course folder.
# Overwrite_params: If false, every keyword under 'PRIVILEDGED_SETTINGS' are preserved
#   and removed if the course is updating an existing one.
#   This setting is ignored if the uploaded course is new.
# If certain values are not present, they are set as defaults.
async def parse_course(dir, overwrite_params: bool) -> None:
    with open(os.path.join(dir, "course.json"), "r") as course_file:
        course_dict: dict = json.load(course_file)

    working_dir = os.path.dirname(os.path.realpath(__file__))
    schema_path = os.path.join(working_dir, "course_schema.json")
    with open(schema_path, "r") as course_schema_file:
        course_schema = json.load(course_schema_file)
    
    # Validate against json schema
    try:
        validate(course_dict, course_schema)
    except JsonValidationError as err:
        raise CourseValidationError(f"Course validation failed against the schema: {err.message}")

    # Setting params as default if they are not present
    course_dict.setdefault("unique_name", os.path.basename(dir))
    course_dict.setdefault("display_name", course_dict["unique_name"])
    course_dict.setdefault("domain", DEFAULT_DOMAIN)
    course_dict.setdefault("mandatory_curriculum", [])
    
    # Ensure default topic is actually a valid topic
    if (course_dict.setdefault("default_topic", list(course_dict["curriculum"].keys())[0])
        not in course_dict["curriculum"].keys()):
        raise CourseValidationError("The default topic is not a valid topic.")
    # Topics get set as curriculum dict keys for compatibility with frontend
    course_dict["topics"] = list(course_dict["curriculum"].keys())
    
    # Setting the course settings defaults if not present
    if isinstance(course_dict.setdefault("course_settings", {}), dict):
        set_course_settings_defaults(course_dict["course_settings"])

        # Transform course settings into list for compatability
        course_dict["sample_settings"] = [1.0]
        course_dict["course_settings_list"] = [course_dict["course_settings"]]
    elif isinstance(course_dict.get("course_settings"), list):
        # Keep multiple course settings for a/b-testing
        n = len(course_dict["course_settings"])
        if n > 0:
            set_course_settings_defaults(course_dict["course_settings"][0])
        course_dict["sample_settings"] = [1 / n for _ in range(n)]
        course_dict["course_settings_list"] = course_dict["course_settings"]
    else:
        raise CourseValidationError(f"""Wrong course_settings type '{type(course_dict["course_settings"])}', must be dict or list.""")
    
    del course_dict["course_settings"]
    
    # Set visibility to "student" by default
    course_dict.setdefault("visibility", DEFAULT_VISIBILITY)

    # Load optional introduction.md from the course directory
    introduction_path = os.path.join(dir, "introduction.md")
    if os.path.isfile(introduction_path):
        with open(introduction_path, "r", encoding="utf-8") as intro_file:
            course_dict["introduction"] = intro_file.read()
    
    # Actually creates the course, should not use course_dict beyond this point
    # If pydantic complains, route error to frontend
    try:
        course = Course(**Course.set_missing_default_parameters(course_dict))
        # Validate content against any potential learner models
        course.validate_for_models()
    except PyValidationError as err:
        raise CourseValidationError(f"Pydantic Error: {str(err)}")
    
    # check if course is new or updates an existing one
    try:
        old_course = await database.get_course(course.unique_name)
        
        # In case of course update:
        # Clean course_dict of priviledged keywords if overwriting is not allowed
        if not overwrite_params:
            for key in PRIVILEDGED_SETTINGS:
                setattr(course, key, deepcopy(getattr(old_course, key, None)))

        # Trigger model's learning process
        await database.update_course(old_course, course.__dict__.copy())
        await course.trigger_model_update()

    except ValueError as err:
        # If course is new, upload as it
        await database.create_course(course)
