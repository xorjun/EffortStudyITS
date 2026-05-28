from typing import List
from typing import Iterable
import motor.motor_asyncio
from fastapi_users.db import BeanieUserDatabase
from courses.schemas import Course, CourseEnrollment
from users.schemas import User, GlobalAccountList
from tasks.schemas import Task, PackedStateSpace
from attempts.schemas import Attempt
from submissions.schemas import Base_Submission as Submission
from submissions.schemas import Tested_Submission
from runs.schemas import Evaluated_run_code_submission as Run_submission
from feedback.schemas import Evaluated_feedback_submission as Feedback_submission
from system.schemas import AppSettings
from surveys.schemas import Survey
from beanie import PydanticObjectId
from pydantic import ValidationError

from beanie.odm.operators.update.general import Set


async def get_user_db():
    yield BeanieUserDatabase(User)


class database:

    def __init__(
        self,
        database_host: str,
        database_user: str,
        database_pwd: str,
        database_port: int = 27017,
    ) -> None:
        DATABASE_URL = f"mongodb://{database_user}:{database_pwd}@{database_host}:{str(database_port)}/?authSource=admin"
        client = motor.motor_asyncio.AsyncIOMotorClient(
            DATABASE_URL, uuidRepresentation="standard"
        )
        self.db = client["its_db"]

    async def log_code_submission(self, tested_submission) -> None:
        await tested_submission.insert()

    async def get_user(self, user_id) -> User:
        user = await User.find_one(User.id == user_id)
        if user is None:
            raise ValueError(f"User '{user}' not found!")
        return user

    async def update_user(self, user: User, update_dict) -> None:
        # TODO: use easier command: "Uset.update" after new versions of MongoDB run on the server.
        await user.update(Set(update_dict))

    async def create_course(self, course: Course) -> None:
        await Course.insert_one(course)
        print(f"New course '{course.unique_name}' uploaded.")

    async def get_courses(self) -> List[Course]:
        return await Course.find().to_list()

    async def get_course(self, unique_name: str) -> Course:
        course = await Course.find_one(Course.unique_name == unique_name)
        if course is None:
            raise ValueError(f"Course '{unique_name}' not found!")
        return course

    async def update_course(self, course: Course, update_dict: dict) -> None:
        await course.update(Set(update_dict))

    async def create_task(self, task_dict) -> None:
        existing = await Task.find_one(Task.unique_name == task_dict["unique_name"])
        if existing is not None:
            for field, value in task_dict.items():
                setattr(existing, field, value)
            await existing.replace()
        else:
            new_task = Task(**task_dict)
            await Task.insert_one(new_task)
            print(f"New Task '{new_task.unique_name}' uploaded.")

    async def get_task(self, unique_name) -> Task:
        task = await Task.find_one(Task.unique_name == unique_name)
        if task is None:
            raise ValueError(f"Task '{task}' not found!")
        return task

    async def get_submission(self, submission_id) -> Submission:
        submission = await Submission.find_one(
            Submission.id == PydanticObjectId(submission_id), with_children=True
        )
        if submission is None:
            raise ValueError(f"Submission '{submission_id}' not found!")
        elif submission.type == "run":
            submission = await Run_submission.find_one(
                Run_submission.id == PydanticObjectId(submission_id)
            )
        elif submission.type == "feedback_request":
            submission = await Feedback_submission.find_one(
                Feedback_submission.id == PydanticObjectId(submission_id)
            )
        if submission is None:
            raise ValueError(f"Submission '{submission_id}' not found!")
        return submission
    
    async def get_tested_submissions_per_user_and_course(self, user_id, course_unique_name) -> Iterable[Tested_Submission]:
        submissions = await Tested_Submission.find(
            Tested_Submission.user_id==PydanticObjectId(user_id),
            Tested_Submission.course_unique_name==course_unique_name,
            Tested_Submission.type == "submission",
            with_children=False).to_list()
        return submissions
    
    async def get_course_settings_for_user(self, user_id, course_unique_name):
        course = await self.get_course(course_unique_name)
        user = await self.get_user(user_id)
        course_enrollment = await self.get_course_enrollment(user, course_unique_name)
        base_settings = course.course_settings_list[0]
        override_index = course_enrollment.course_settings_index
        if override_index != 0:
            override_settings = course.course_settings_list[
                course_enrollment.course_settings_index
            ]
            for key in override_settings.keys():
                base_settings.update([(key, override_settings[key])])
        return base_settings

    async def create_course_enrollment(
        self, course_enrollment: CourseEnrollment
    ) -> None:
        await course_enrollment.insert()

    async def get_course_enrollment(
        self, user: User, course_unique_name
    ) -> CourseEnrollment:
        course_enrollment = await CourseEnrollment.find_one(
            CourseEnrollment.user_id == str(user.id),
            CourseEnrollment.course_unique_name == course_unique_name,
        )
        if course_enrollment is None:
            raise AttributeError(
                f"Course enrollment not found for user_id='{str(user.id)}' in course '{course_unique_name}'."
            )
        else:
            return course_enrollment

    async def update_course_enrollment(
        self, course_enrollment: CourseEnrollment, update_dict
    ) -> None:
        await course_enrollment.update({"$set": update_dict})

    async def get_attempt(self, attempt_id):
        attempt = await Attempt.get(PydanticObjectId(attempt_id))
        if attempt is None:
            raise ValueError(f"Attempt id={attempt_id} not found!")
        return attempt

    async def find_attempt(
        self, task_unique_name, user_id: PydanticObjectId, course_unique_name
    ) -> Attempt:
        attempt = await Attempt.find_one(
            Attempt.task_unique_name == task_unique_name,
            Attempt.user_id == str(user_id),
            Attempt.course_unique_name == course_unique_name,
        )
        if attempt is None:
            raise ValueError(
                f"Attempt (task_name={task_unique_name}, user_id={user_id}, course_name={course_unique_name}) not found!"
            )
        return attempt

    async def update_attempt(self, attempt: Attempt) -> None:
        await attempt.save()

    async def create_attempt(self, attempt: Attempt) -> None:
        await attempt.insert()

    async def get_settings(self) -> AppSettings:
        settings = await AppSettings.find_one()
        if settings is None:
            raise ValueError(f"AppSettings not found!")
        return settings

    async def create_settings(self, settings: AppSettings) -> None:
        try:
            old_settings = await AppSettings.find().to_list()
        except ValidationError as e:
            print("Warning admin settings could not be restored, exiting!")
            raise e
        if len(old_settings) == 0:
            await settings.insert()

    async def update_settings(self, update_dict) -> None:
        settings = await self.get_settings()
        if settings is None:
            raise ValueError(f"Settings not found!")
        await settings.update(Set(update_dict))

    async def get_global_accounts_list(self) -> GlobalAccountList:
        global_accounts_list = await GlobalAccountList.find_one()
        if global_accounts_list is None:
            raise ValueError(f"Global Accounts list not found!")
        return global_accounts_list

    async def create_global_accounts_list(
        self, global_accounts_list: GlobalAccountList
    ) -> None:
        existing_list = await GlobalAccountList.find().to_list()
        if len(existing_list) == 0:
            await global_accounts_list.insert()

    async def update_global_accounts_list(self, update_dict) -> None:
        global_accounts_list = await GlobalAccountList.find_one()
        if global_accounts_list is None:
            raise ValueError(f"global_accounts_list not found!")
        await global_accounts_list.update(Set(update_dict))

    async def get_all_enrolled_users(
        self, course_unique_name
    ) -> List[CourseEnrollment]:
        courses = await CourseEnrollment.find(
            CourseEnrollment.course_unique_name == course_unique_name
        ).to_list()
        return courses

    async def create_survey(self, survey: Survey):
        await survey.insert()

    async def get_survey(self, corresponding_id, id_type):
        surveys = await Survey.find(
            Survey.corresponding_id == corresponding_id,
            Survey.corresponding_id_type == id_type,
        ).to_list()
        if len(surveys) > 1:
            raise ValueError("More than one survey for one survey item!")
        if len(surveys) == 0:
            return None
        else:
            return surveys[0]

    async def update_survey(self, survey: Survey) -> None:
        await survey.save()

    async def update_state_space(self, state_space: PackedStateSpace) -> None:
        await state_space.save()

    async def get_state_space(self, task_unique_name):
        state_spaces = await PackedStateSpace.find(
            PackedStateSpace.task_unique_name == task_unique_name
        ).to_list()
        if len(state_spaces) == 0:
            return None
        else:
            return state_spaces[0]
