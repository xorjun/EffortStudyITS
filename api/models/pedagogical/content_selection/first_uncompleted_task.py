from models.pedagogical.content_selection.base import Base_task_selector
from db import database
from users.schemas import User

class First_uncompleted_task_selector(Base_task_selector):

    async def select(self, user: User, topic=None):
        """Task select method fo the ITS prototype. This is not a sophisticated Outer Loop, only very basic curriculum-aware task selection.

        Args:
            user (User): _description_
        """
        course_enrollment = await database.get_course_enrollment(user, user.current_course)
        if course_enrollment.completed:
            return("course completed")
        user_course_unique_name = user.current_course
        course = await database.get_course(user_course_unique_name)
        curriculum = course.curriculum
        user_completed_tasks = course_enrollment.tasks_completed
        
        # Flatten the curriculum from a list of task lists to a normal list of tasks
        if isinstance(curriculum, list) and isinstance(curriculum[0], list):
            curriculum = [item for sublist in curriculum for item in sublist]

        if topic is None and isinstance(curriculum, dict):
            _curriculum = []
            for key in curriculum.keys():
                _curriculum.extend(curriculum[key])
            curriculum = _curriculum
        elif not topic is None and isinstance(curriculum, dict):
            curriculum = curriculum[topic]
        else:
            pass

        uncompleted_tasks = [curriculum_task for curriculum_task in curriculum if curriculum_task not in user_completed_tasks]

        if len(uncompleted_tasks) > 0:
            return uncompleted_tasks[0]
        else:
            return curriculum[-1]
        