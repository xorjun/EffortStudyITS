import itertools

from models.knowledge_tracing.kt_base import KT_Factor_Analysis_Model_Base
from courses.schemas import Course, CourseEnrollment, CourseValidationError
from users.schemas import User
from db import database

from sklearn.linear_model import LogisticRegression
import numpy as np
from collections.abc import Iterable
from submissions.schemas import Tested_Submission


DEFAULT_COMPETENCY = ["default_competency"]
DEFAULT_SKILL_WEIGHT = 0.0
N = 3


class PFA_Model(KT_Factor_Analysis_Model_Base):
    
    """Validates the given course for a functioning Q-Matrix. Assumes all parameters are present (can be generated default)."""
    @staticmethod
    def validate_course(course: Course) -> None:
        # Check q-matrix against curriculum
        if set(course.q_matrix.keys()) != set(course.get_local_curriculum()):
            raise CourseValidationError("PFA: Q-Matrix does not match the curriculum.")
        
        # Check q-matrix against skill weights and competencies
        for value in course.q_matrix.values():
            if len(value) * N != len(course.course_parameters["skill_weights_pfa"]):
                raise CourseValidationError("PFA: Q-Matrix does not fit to the skill weights.")
            if len(value) != len(course.competencies):
                raise CourseValidationError("PFA: Q-Matrix does not fit to the competencies.")
    
    @classmethod
    async def completion_probability(cls, task_names: str | list[str], user: User, course: Course | None = None) -> list[float]:
        if course == None:
            course = await database.get_course(user.current_course)
        if type(task_names) == str:
            task_names = [task_names]
        
        # preprocessing
        course_enrollment = await database.get_course_enrollment(user, course.unique_name)
        succ_rate, fail_rate = cls.get_sf_rate(course_enrollment, course)
        skill_weights = np.array(course.course_parameters.get("skill_weights_pfa"))
        
        # calculate probability of completion for each given task
        competion_probabilities = []
        for task_name in task_names:
            task_weights = np.repeat(course.q_matrix[task_name], N) * skill_weights

            # TODO could probably be optimized with numpy
            logit = 0
            for i in range(len(course.competencies)):
                logit += (task_weights[N*i] * succ_rate[i]
                + task_weights[N*i+1] * fail_rate[i]
                + task_weights[N*i+2])
            competion_probabilities.append(1 / (1 + np.exp(-logit)))
        return competion_probabilities
    
    @staticmethod
    async def update_course_weights(course: Course) -> None:
        if course.domain == "Surveys": return
        
        #get all the task completions and order it for users and time stamps (last submissions available?) call all_course_submissions + correctness
        all_course_enrollments = await database.get_all_enrolled_users(course.unique_name)
        # Only update if there are any actual enrollments
        if len(all_course_enrollments) == 0: return

        q_matrix = course.q_matrix
        num_skills = len(course.competencies)
        course_parameters_new = course.course_parameters.copy()
        
        Xlogreg_reg = []
        Ylogreg = []
        
        # TODO refactor to use get_sf_rate
        for course_enrollment in all_course_enrollments:
            s = np.zeros(num_skills)
            f = np.zeros(num_skills)
            attempted_tasks = course_enrollment.tasks_attempted
            attempted_tasks = [task for task in attempted_tasks if task in q_matrix.keys()]
            for task in attempted_tasks:     
                task_skills = q_matrix[task]
                new_row= np.zeros(num_skills*N)
                for j in range(num_skills):
                # adding the entry  
                    new_row[3*j + 0] = s[j]
                    new_row[3*j + 1] = f[j]
                    new_row[3*j + 2] = task_skills[j]
                if (task in course_enrollment.tasks_completed):
                    s = [sum(x) for x in zip(s, task_skills)]
                    Ylogreg.append(1)
                else:
                    f += [sum(x) for x in zip(s, task_skills)]
                    Ylogreg.append(0)
                Xlogreg_reg.append(new_row)
        
        pfa_model = LogisticRegression(penalty = 'l2', C = 1.0, fit_intercept = False)
        pfa_model.fit(Xlogreg_reg, Ylogreg)

        coefficients = (-pfa_model.coef_[0]).tolist()
        course_parameters_new["skill_weights_pfa"] = coefficients

        await database.update_course(course, {"course_parameters": course_parameters_new})
    
    @staticmethod
    def get_sf_rate(course_enrollment: CourseEnrollment, course: Course):
        attempted_tasks = course_enrollment.tasks_attempted
        attempted_tasks = [task for task in attempted_tasks if task in course.q_matrix.keys()]
        completed_tasks = course_enrollment.tasks_completed
        completed_tasks = [task for task in completed_tasks if task in course.q_matrix.keys()]
        
        succ_rate = np.zeros(len(course.competencies))
        fail_rate = np.zeros(len(course.competencies))
        for task in attempted_tasks:
            if task in completed_tasks:
                succ_rate = np.add(succ_rate, course.q_matrix[task])
            else:
                fail_rate = np.add(fail_rate, course.q_matrix[task])
        return succ_rate, fail_rate

    @staticmethod
    def get_sf_rate_based_on_submissions(tested_submissions : Iterable[Tested_Submission], course: Course):
        succ_rate = np.zeros(len(course.competencies))
        fail_rate = np.zeros(len(course.competencies))

        for tested_submission in tested_submissions:
            if tested_submission.valid_solution:
                succ_rate += course.q_matrix[tested_submission.task_unique_name]
            else:
                fail_rate += course.q_matrix[tested_submission.task_unique_name]
        return succ_rate, fail_rate

    @classmethod
    def set_default_parameters(cls, course_dict: dict) -> None:
        print(f"""Generating default PFA parameters for course '{course_dict.get("unique_name", "undefined")}'.""")
        cls.set_default_q_matrix(course_dict)
        cls.set_default_weights(course_dict)

    @classmethod
    def set_missing_default_parameters(cls, course_dict: dict) -> None:
        print(f"""Generating missing default PFA parameters for course '{course_dict.get("unique_name", "undefined")}'.""")
        # Pydantic is assigning weird default values on object creation
        if ("q_matrix" not in course_dict
            or "competencies"not in course_dict):
            cls.set_default_q_matrix(course_dict)
        if ("course_parameters" not in course_dict
            or course_dict.get("course_parameters", {}).get("skill_weights_pfa") is None):
            cls.set_default_weights(course_dict)

    # Sets the course's q-matrix and competencies to default
    @staticmethod
    def set_default_q_matrix(course_dict: dict) -> None:
        course_dict["competencies"] = DEFAULT_COMPETENCY
        flat_curriculum = list(itertools.chain.from_iterable(course_dict["curriculum"].values()))
        course_dict["q_matrix"] = {task: [1]*len(DEFAULT_COMPETENCY) for task in flat_curriculum}
    
    # Sets the course's skill weights to default
    @staticmethod
    def set_default_weights(course_dict: dict) -> None:
        skill_weights_pfa = [DEFAULT_SKILL_WEIGHT] * N * len(course_dict.get("competencies", DEFAULT_COMPETENCY))
        course_dict.setdefault("course_parameters", {})["skill_weights_pfa"] = skill_weights_pfa
