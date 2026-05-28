from models.pedagogical.content_selection.base_selector import Base_task_selector
from db import database
from users.schemas import User


class First_uncompleted_task_selector(Base_task_selector):

    async def select(self, user: User, topic = None) -> str:
        """Task select method fo the ITS prototype. This is not a sophisticated Outer Loop, only very basic curriculum-aware task selection.

        Args:
            user (User): _description_
        """
        
        course_enrollment = await database.get_course_enrollment(
            user, user.current_course
        )
        user_course_unique_name = user.current_course
        course = await database.get_course(user_course_unique_name)

        if course_enrollment.completed:
            return "course completed"
        user_completed_tasks = course_enrollment.tasks_completed

        uncompleted_tasks = [
            curriculum_task
            for curriculum_task in course.get_local_curriculum(topic)
            if curriculum_task not in user_completed_tasks
        ]

        if len(uncompleted_tasks) > 0:
            return uncompleted_tasks[0]
        else:
            return "course completed"
