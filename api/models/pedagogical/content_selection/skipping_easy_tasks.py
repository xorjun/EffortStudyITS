from models.pedagogical.content_selection.base import Base_task_selector
from db import database
from users.schemas import User
#from models.learner.competency_models import Task_completion_probability
import numpy as np
import math


class Skipping_task_selector(Base_task_selector):

    async def select(self, user: User):
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

        # Flatten the curriculum from a dict of task lists to a normal list of tasks
        if isinstance(curriculum, list) and isinstance(curriculum[0], list):
            curriculum = [item for sublist in curriculum for item in sublist]
            print("curriculum: \n", curriculum)

        uncompleted_tasks = [curriculum_task for curriculum_task in curriculum if curriculum_task not in user_completed_tasks]
        if course.domain == "Surveys":
             return(uncompleted_tasks[0])

        q_matrix = course.q_matrix
        skill_weights = np.array(course.course_parameters["skill_weights_pfa"])
        user_completed_tasks = course_enrollment.tasks_completed
        user_attempted_tasks = course_enrollment.tasks_attempted
        num_skills = len(course.competencies)
        mandatory_tasks = course.mandatory_curriculum
        #new_task_skills = q_matrix.get(Task.unique_name)
        #n=4 #with struggle
        n=3 #without struggle
        #new_task_skills= np.repeat(new_task_skills, n)

        s = np.zeros(num_skills)
        f = np.zeros(num_skills)
        for task in user_attempted_tasks:
            task_skills = q_matrix.get(task)
            if (task in user_completed_tasks):
                s = [sum(x) for x in zip(s, task_skills)]
            else:
                f += [sum(x) for x in zip(s, task_skills)]

        # Computing previous successes and failures
        def completion_probability(example_task):
            new_task_skills = q_matrix.get(example_task)
            new_task_skills= np.repeat(new_task_skills, n)
            new_task_weights = new_task_skills*skill_weights
            logit = 0
        
            for i in range(num_skills): 
                logit += new_task_weights[n*i]*s[i] + new_task_weights[n*i+1]*f[i] + new_task_weights[n*i+2]

            return 1 / (1 + math.exp(-logit))
        

        if ((completion_probability(uncompleted_tasks[0])>0.8) and (uncompleted_tasks[0] not in mandatory_tasks)):
            while ((completion_probability(uncompleted_tasks[0])>0.8) and (len(uncompleted_tasks)>0) and (uncompleted_tasks[0] not in mandatory_tasks)):
                uncompleted_tasks.pop(0)

        return(uncompleted_tasks[0])
