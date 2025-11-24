import warnings
from models.knowledge_tracing.kt_base import KT_Factor_Analysis_Model_Base
from courses.schemas import Course, CourseValidationStatus
from tasks.schemas import Task
from users.schemas import User
from db import database

from sklearn.linear_model import LogisticRegression
import numpy as np


DEFAULT_COMPETENCY = ["default_competency"]
DEFAULT_SKILL_WEIGHT = [0]

class PFA_Model(KT_Factor_Analysis_Model_Base):
    current_user: User
    q_matrix: dict
    competencies: list
    skill_weights: np.ndarray
    succ_rate: np.ndarray
    fail_rate: np.ndarray
    
    def __init__(self, n_parameters: int = 3):
        self.n = n_parameters
        super().__init__()
    
    async def set_user(self, user: User, course: Course = None):
        self.current_user = user
        if course == None:
            course = await database.get_course(user.current_course)
        course_enrollment = await database.get_course_enrollment(user, course.unique_name)
        
        #await self.validate_course(course)
        
        self.q_matrix = course.q_matrix
        self.competencies = course.competencies
        self.skill_weights = np.array(course.course_parameters.get("skill_weights_pfa"))
        
        self.succ_rate, self.fail_rate = self.get_sf_rate(course_enrollment)
        return self
    
    """Checks the course if all required paramters are present."""
    def check_missing_params(self, course: Course | dict):
        if type(course) == Course:
            course = course.__dict__
        q_matrix_exists = course.get("q_matrix") != None
        comp_exists = course.get("competencies") != None
        params_exist = course.get("course_parameters") != None
        weights_exist = course.get("course_parameters", {}).get("skill_weights_pfa") != None
        
        if not (q_matrix_exists or comp_exists or params_exist or weights_exist):
            warn_msg = f"""PFA: Generating default PFA components (Q-Matrix, Competencies, and Skill Weights) for '{course.get("unique_name")}' as none have been found."""
            status = CourseValidationStatus.Missing
        elif not q_matrix_exists:
            warn_msg = f"""PFA: Q-Matrix not found for course '{course.get("unique_name")}'."""
            status = CourseValidationStatus.Faulty
        elif not comp_exists:
            warn_msg = f"""PFA: Course competencies not found for course '{course.get("unique_name")}'."""
            status = CourseValidationStatus.Faulty
        elif not params_exist:
            warn_msg = f"""PFA: Generating default parameters for course '{course.get("unique_name")}' as none have been found."""
            status = CourseValidationStatus.No_Weights
        elif not weights_exist:
            warn_msg = f"""PFA: Skill weights not found for course '{course.get("unique_name")}'."""
            status = CourseValidationStatus.Faulty
        else: 
            warn_msg = ""
            status = CourseValidationStatus.Valid
        if warn_msg != "": warnings.warn(warn_msg)
        return status, warn_msg
    
    """Validates the given course for a functioning Q-Matrix. Assumes all parameters are present (can be generated default)."""
    def validate_course(self, course: Course | dict):
        if type(course) == Course:
            course = course.__dict__
        status, warn_msg = self.check_missing_params(course)
        if status != CourseValidationStatus.Valid:
            return status, warn_msg
        
        weights_exist = "skill_weights_pfa" in course.get("course_parameters").keys()
        #matching_curriculum = set(course.get("curriculum")).issubset(course.get("q_matrix").keys())
        curriculum = course.get("curriculum", {})
        if isinstance(curriculum, list):
            matching_curriculum = set(curriculum).issubset(course.get("q_matrix").keys())
        elif isinstance(curriculum, dict):
            curriculum_tasks_set = curriculum.values()
            curriculum_tasks_set = set([task for topic in curriculum_tasks_set for task in topic])
            matching_curriculum = curriculum_tasks_set.issubset(course.get("q_matrix").keys())
        else:
            raise ValueError("Curriculum malformatted.")
        if weights_exist:
            matching_qmatrix = len(course.get("competencies")) * self.n == len(course.get("course_parameters").get("skill_weights_pfa"))
            q_matrix: dict = course.get("q_matrix")
            matching_qmatrix = matching_qmatrix and all([len(course.get("competencies")) == len(q_matrix.get(key)) for key in q_matrix.keys()])
        
        if not weights_exist:
            warn_msg = f"""PFA: Generating default skill weights for course '{course.get("unique_name")}' as none have been found."""
            status = CourseValidationStatus.No_Weights
        # also set faulty if q-matrix is not matching the curriculum anymore
        # (for example if course has been updated with new tasks)
        elif not matching_curriculum:
            warn_msg = f"""PFA: Q-matrix not matching curriculum for course '{course.get("unique_name")}'."""
            status = CourseValidationStatus.Faulty
        elif not matching_qmatrix:
            warn_msg = f"""PFA: Course competencies do not match skill weights or q-matrix for course '{course.get("unique_name")}'."""
            status = CourseValidationStatus.Faulty
        else:
            warn_msg = ""
            status = CourseValidationStatus.Valid
        if warn_msg != "": warnings.warn(warn_msg)
        return status, warn_msg

    def unset_user(self):
        self.current_user = None
        self.q_matrix = None
        self.competencies = None
        self.skill_weights = None
        self.succ_rate = None
        self.fail_rate = None
    
    def completion_probability(self, task: Task):
        if self.current_user == None:
            raise AttributeError("PFA Model has not been set to a user. Call 'set_user' before calculating completion probability.")
        
        new_task_skills = self.q_matrix.get(task)
        if new_task_skills == None:
            raise AttributeError(f"Task '{task}' not found in Q-Matrix! Try deleting and regenerating it.")
        new_task_skills = np.repeat(new_task_skills, self.n)
        new_task_weights = new_task_skills * self.skill_weights

        logit = 0
        for i in range(len(self.competencies)):
            logit += new_task_weights[self.n*i]*self.succ_rate[i]
            + new_task_weights[self.n*i+1]*self.fail_rate[i]
            + new_task_weights[self.n*i+2]
        return 1 / (1 + np.exp(-logit))
        
    async def update_course_weights(self, course: Course | list = None):
        if course == None: 
            if self.current_user == None: raise ValueError("No current user has been set.")
            course = await database.get_course(self.current_user.current_course)
        elif type(course) == dict:
            course = await database.get_course(course.get("unique_name"))
        
        if course.domain == "Surveys": return
        
        #get all the task completions and order it for users and time stamps (last submissions available?) call all_course_submissions + correctness
        all_course_enrollments = await database.get_all_enrolled_users(course.unique_name)

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
                task_skills = q_matrix.get(task)
                new_row= np.zeros(num_skills*self.n)
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
        return 
    
    def get_sf_rate(self, course_enrollment):
        attempted_tasks = course_enrollment.tasks_attempted
        attempted_tasks = [task for task in attempted_tasks if task in self.q_matrix.keys()]
        completed_tasks = course_enrollment.tasks_completed
        completed_tasks = [task for task in completed_tasks if task in self.q_matrix.keys()]
        
        succ_rate = np.zeros(len(self.competencies))
        fail_rate = np.zeros(len(self.competencies))
        for task in attempted_tasks:
            if task in completed_tasks:
                succ_rate = np.add(succ_rate, self.q_matrix.get(task))
            else:
                fail_rate = np.add(fail_rate, self.q_matrix.get(task))
        return succ_rate, fail_rate

    def set_default_params(self, course: Course | dict):
        # Need to distinguish between course and course_dict
        
        if type(course) == Course:
            course.competencies = DEFAULT_COMPETENCY
            course.q_matrix = {task: [1] for task in course.curriculum}
            
        elif type(course) == dict:
            course["competencies"] = DEFAULT_COMPETENCY
            course["q_matrix"] = {task: [1] for task in course["curriculum"]}  
        
        course = self.set_default_weights(course)
        return course

    def set_default_weights(self, course: Course | dict):
        # Need to distinguish between course and course_dict
        
        if type(course) == Course:
            skill_weights_pfa = DEFAULT_SKILL_WEIGHT * self.n
            if course.course_parameters == None:
                course.course_parameters = {"skill_weights_pfa": skill_weights_pfa}
            else:
                course.course_parameters["skill_weights_pfa"] = skill_weights_pfa
        
        elif type(course) == dict:    
            skill_weights_pfa = DEFAULT_SKILL_WEIGHT * self.n
            if course.get("course_parameters") == None:
                course["course_parameters"] = {"skill_weights_pfa": skill_weights_pfa}
            else:
                course["course_parameters"]["skill_weights_pfa"] = skill_weights_pfa
        
        return course