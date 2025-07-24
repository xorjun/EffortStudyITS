import motor.motor_asyncio
from courses.schemas import Course, CourseEnrollment
from beanie import Document
from fastapi_users.db import BeanieUserDatabase
from typing import Optional
from users.schemas import User, GlobalAccountList
from tasks.schemas import Task
from attempts.schemas import Attempt
from submissions.schemas import Base_Submission as Submission
from runs.schemas import Evaluated_run_code_submission as Run_submission
from tasks.schemas import Task
from feedback.schemas import Evaluated_feedback_submission as Feedback_submission
from system.schemas import AppSettings
from beanie import PydanticObjectId
from surveys.schemas import Survey


async def get_user_db():
    yield BeanieUserDatabase(User)

class database():
    
    def __init__(self, database_host: str, database_user: str, database_pwd: str, database_port: str=27017) -> None:
        DATABASE_URL = f"mongodb://{database_user}:{database_pwd}@{database_host}:{database_port}/?authSource=admin"
        client = motor.motor_asyncio.AsyncIOMotorClient(
            DATABASE_URL, uuidRepresentation="standard"
        )
        self.db = client["its_db"]

    async def log_code_submission(self, tested_submission):
        await tested_submission.insert()

    async def get_task(self, unique_name):
        task = await Task.find_one(Task.unique_name == unique_name)
        return(task)
        #cursor = self.db.tasks.find({"task_id": task_id})
        #task_json = await cursor.to_list(length=1)
        #if len(task_json) == 1:
        #    return(task_json[0])
        #else: 
        #    raise Exception("Multiple Tasks with same ID present")

    async def create_task(self, task_dict):
        old_task = await self.get_task(task_dict["unique_name"])
        if old_task is None:
            new_task = Task(**task_dict)
            await Task.insert_one(new_task)
        else:
            await old_task.update({"$set": task_dict})

    async def create_course(self, course_dict):
        old_course = await self.get_course(course_dict["unique_name"])
        if old_course is None:
            new_course = Course(**course_dict)
            await Course.insert_one(new_course)
        else:
            await old_course.update({"$set": course_dict})

        
    async def get_submission(self, submission_id):
        submission = await Submission.find_one(Submission.id == PydanticObjectId(submission_id), with_children=True)
        if submission.type == "run":
            submission = await Run_submission.find_one(Run_submission.id == PydanticObjectId(submission_id))
        elif submission.type == "feedback_request":
            submission = await Feedback_submission.find_one(Feedback_submission.id == PydanticObjectId(submission_id))
        return(submission)

    async def get_user(self, user_id): 
        #Use fastapi_users boilerplate indirectly to increase modularity.
        #user = await get_user_db.get(user_id)
        user = await User.find_one(User.id == user_id)
        return(user)

    async def update_user(self, user: User, update_dict):
        #TODO: use easier command: "Uset.update" after new versions of MongoDB run on the server.
        #await get_user_db().update(user)
        await user.update({"$set": update_dict})
        #await user.save()

    async def get_course(self, unique_name):
        course = await Course.find_one(Course.unique_name == unique_name)
        return course
    
    async def get_courses(self):
        courses = await Course.find().to_list()
        return courses
    
    async def get_course_settings_for_user(self, user_id, course_unique_name):
        course = await self.get_course(course_unique_name)
        user = await self.get_user(user_id)
        course_enrollment = await self.get_course_enrollment(user, course_unique_name)
        base_settings = course.course_settings_list[0]
        override_index = course_enrollment.course_settings_index
        if override_index != 0:
            override_settings = course.course_settings_list[course_enrollment.course_settings_index]
            for key in override_settings.keys():
                base_settings.update([(key, override_settings[key])])
        return base_settings
    
    async def update_course(self, course: Course, update_dict):
        await course.update({"$set": update_dict})

    async def create_course_enrollment(self, course_enrollment: CourseEnrollment):
        await course_enrollment.insert()
    
    async def get_course_enrollment(self, user: User, course_unique_name):
        course_enrollment = await CourseEnrollment.find_one(CourseEnrollment.user_id==str(user.id), 
                                                            CourseEnrollment.course_unique_name==course_unique_name)
        if course_enrollment is None:
            raise Exception(f"Course enrollment not found for {str(User.id)} and {course_unique_name}")
        else:
            return course_enrollment
        
    async def update_course_enrollment(self, course_enrollment: CourseEnrollment, update_dict):
        await course_enrollment.update({"$set": update_dict})
    
    async def get_attempt(self, attempt_id):
        attempt = await Attempt.get(PydanticObjectId(attempt_id))
        return attempt

    async def find_attempt(self, task_unique_name, user_id: PydanticObjectId, course_unique_name):
        attempt = await Attempt.find_one(Attempt.task_unique_name == task_unique_name, 
                                         Attempt.user_id == str(user_id), 
                                         Attempt.course_unique_name == course_unique_name)
        return attempt
    
    async def update_attempt(self, attempt: Attempt): 
        await attempt.save()

    async def create_attempt(self, attempt: Attempt): 
        await attempt.insert()

    async def get_settings(self):
        settings = await AppSettings.find_one()
        return settings

    async def create_settings(self, settings: AppSettings):
        old_settings = await AppSettings.find().to_list()
        if len(old_settings) == 0:
            await settings.insert()

    async def update_settings(self, update_dict):
        settings = await self.get_settings()
        await settings.update({"$set": update_dict})

    async def get_global_accounts_list(self):
        global_accounts_list = await GlobalAccountList.find_one()
        return global_accounts_list
    
    async def create_global_accounts_list(self, global_accounts_list: GlobalAccountList):
        existing_list = await GlobalAccountList.find().to_list()
        if len(existing_list) == 0:
            await global_accounts_list.insert()
    
    async def update_global_accounts_list(self, update_dict):
        global_accounts_list = await GlobalAccountList.find_one()
        await global_accounts_list.update({"$set": update_dict})

    async def get_all_enrolled_users(self, course_unique_name):
        courses = await CourseEnrollment.find(CourseEnrollment.course_unique_name==course_unique_name).to_list()
        return courses
    
    async def create_survey(self, survey: Survey):
        await survey.insert()

    async def get_survey(self, corresponding_id, id_type):
        surveys = await Survey.find(Survey.corresponding_id==corresponding_id,
                                    Survey.corresponding_id_type==id_type).to_list()
        if len(surveys) > 1:
            raise Exception("More than one survey for one survey item!")
        if len(surveys) == 0:
            return None
        else:
            return surveys[0]
    
    async def update_survey(self, survey: Survey):
        await survey.save()