from fastapi import APIRouter, HTTPException, status
from fastapi import Depends
from courses.schemas import Course
from users.schemas import User
from users.handle_users import current_active_verified_user
from db import database
from models import model_manager
from models.pedagogical.model_variants import Skipping_tasks_pfa_pedagogical_model
from models.pedagogical.content_selection.skipping_easy_tasks import Skipping_task_selector
from models.knowledge_tracing.pfa_model import PFA_Model
from services.language_generation import generate_language
from skills.schemas import SkillOverview, Skill, ReasonDescription, ExplanationDescription

from datetime import datetime, timedelta, timezone
from dateutil import parser


router = APIRouter(prefix="/skills")

#TODO: convert in percentage with provided number at 100 percent
async def compute_pfa_skill_estimation(pfa_model: PFA_Model, user: User, course: Course):

    skill_names = course.competencies
    #weights = pfa_model.skill_weights
    weights = course.course_parameters["skill_weights_pfa"]

    tested_submissions = await database.get_tested_submissions_per_user_and_course(user.id, course.unique_name)
    split_point_utc = datetime.now(timezone.utc) - timedelta(days=7)
    
    submissions_last_week = []
    older_submissions = []
    for submission in tested_submissions:
        
        # Is stored as text directly from the frontend in the db, format used 'dd.MM.yyyy HH:mm:ss'
        if parser.parse(submission.submission_time["utc"], dayfirst=True).timestamp() > split_point_utc.timestamp():
            submissions_last_week.append(submission) 
        else:
            older_submissions.append(submission)

    success_rate_last_week, fail_rate_last_week = pfa_model.get_sf_rate_based_on_submissions(older_submissions, course)
    success_rate_gain, fail_rate_gain = pfa_model.get_sf_rate_based_on_submissions(submissions_last_week, course)

    success_rate_now = success_rate_last_week + success_rate_gain
    fail_rate_now =  fail_rate_last_week + fail_rate_gain

    result = []
    for i, name in enumerate(skill_names):
        value_last_week = (weights[i*3] * success_rate_last_week[i]
            + weights[i*3+1] * fail_rate_last_week[i]
            + weights[i*3+2])
        value_now = (weights[i*3] * success_rate_now[i]
            + weights[i*3+1] * fail_rate_now[i]
            + weights[i*3+2])
        
        result.append(Skill(name=name, value=value_last_week, gain = value_now - value_last_week))
    return result


# TODO: check if user is involved in the courses every time
@router.get("/{course_unique_name}")
async def get_skills_overview(course_unique_name: str, user: User = Depends(current_active_verified_user)) -> SkillOverview:
    course = await database.get_course(course_unique_name)
    if course == None:
        raise HTTPException(            
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No course with this unique name was found")
    
    course_enrollment = await database.get_course_enrollment(user, course_unique_name)
    if course_enrollment == None:
        raise HTTPException(            
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not enrolled in the course")
    
    skill_names = course.competencies # TODO: (maybe better extract this out of the pfa_model)
    if skill_names == None:
        raise HTTPException(            
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This course has no skills")

    pedagogical_model: Skipping_tasks_pfa_pedagogical_model = model_manager.get_pedagogical_model("skipping_pfa") # TODO: check if these 'type casts' hold always
    task_selector: Skipping_task_selector = pedagogical_model.task_selector
    pfa_model: PFA_Model = task_selector.learner_model

    result = await compute_pfa_skill_estimation(pfa_model, user, course)
        
    return SkillOverview(skill_list=result)


def get_tasks_for_skill(skill_list, skill_name, q_matrix):
    skill_index = skill_list.index(skill_name)
    associated_tasks = []
    for task_name, skill_vector in q_matrix.items():
        if skill_vector[skill_index] > 0.5:
            associated_tasks.append(task_name)
    return associated_tasks

def classify_tasks(task_list, course_enrollment):
    solved_correctly = []
    solved_incorrectly = []
    not_attempted = []
    for task_name in task_list:
        if task_name in course_enrollment.tasks_attempted:
            if task_name in course_enrollment.tasks_completed:
                solved_correctly.append(task_name)
            else:
                solved_incorrectly.append(task_name)
        else:
            not_attempted.append(task_name)
    return solved_correctly, solved_incorrectly, not_attempted

#maybe more somthing like detail instead of reason
@router.get("/{course_unique_name}/{skill_name}/reason")
async def get_reason(course_unique_name: str, skill_name: str, user: User = Depends(current_active_verified_user)):
    course = await database.get_course(course_unique_name)
    if course == None:
        raise HTTPException(            
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No course with this unique name was found")
    
    if course.competencies == None or skill_name not in course.competencies:
        raise HTTPException(            
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No skill with this name was found")
    
    course_enrollment = await database.get_course_enrollment(user, course_unique_name)
    if course_enrollment == None:
        raise HTTPException(            
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not enrolled in the course")

    associated_tasks = get_tasks_for_skill(course.competencies, skill_name, course.q_matrix)

    solved_correctly, solved_incorrectly, not_attempted = classify_tasks(associated_tasks, course_enrollment)
    
    reason = f"""
The estimation of the skill development is provided with help of Performance Factor Analysis based on the performance in the tasks associated with the skill {skill_name}: \n
Solved correctly: {solved_correctly}
Solved incorrectly: {solved_incorrectly}
Not attempted: {not_attempted}"""
    
    return ReasonDescription(reason=reason)

def generate_prompt(course_display_name, skill_development_data):
    recommendation = """
Solving tasks that were not attempted or solved correctly before. 
Revisiting course materials. 
Recapping core concepts related to the skill
Revisiting previously solved tasks. 
"""

    system = """You are a **tutor** supporting a student in programming. You are **professional, helpful and kind**.  You want to provide **explanations to their current skill state and recommendation for further actions** based on their performance, so that the student can continue on their own. Note that you should only give feedback to the specific skill. The explanation should be phrased as suggestions. The suggestion should be formulated in 2-3 sentences.  """

    instruction = f"""Note that more skills can be available in the course, but you only need to give feedback to the mentioned one. Based on the student performance, please recommend how the student should proceed with their learning for this specific skill. . 
Here is the example of the of student performance: 

Course: 

{course_display_name}

Student progress and skill development data: 

{skill_development_data}

Please explain to the student in two to three sentences their current performance in the skill and how they should proceed. Here are examples of potential interventions: 

{recommendation}

Address the student directly. Formulate your summary and recommendation in 2-3 sentences.
"""
    return system, instruction

@router.get("/{course_unique_name}/{skill_name}/explanation")
async def get_llm_explanation(course_unique_name: str, skill_name: str, user: User = Depends(current_active_verified_user)):
    course = await database.get_course(course_unique_name)
    if course == None:
        raise HTTPException(            
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No course with this unique name was found")
    
    if course.competencies == None or skill_name not in course.competencies:
        raise HTTPException(            
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No skill with this name was found")
    
    course_enrollment = await database.get_course_enrollment(user, course_unique_name)
    if course_enrollment == None:
        raise HTTPException(            
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not enrolled in the course")

    course_settings = await database.get_course_settings_for_user(user.id, course_unique_name)
    language_generation_model = course_settings["language_generation_model"]

    pedagogical_model: Skipping_tasks_pfa_pedagogical_model = model_manager.get_pedagogical_model("skipping_pfa") # TODO: check if these 'type casts' hold always
    task_selector: Skipping_task_selector = pedagogical_model.task_selector
    pfa_model: PFA_Model = task_selector.learner_model

    skill_estimation_list = await compute_pfa_skill_estimation(pfa_model, user, course)

    associated_tasks = get_tasks_for_skill(course.competencies, skill_name, course.q_matrix)
    solved_correctly, solved_incorrectly, not_attempted = classify_tasks(associated_tasks, course_enrollment)
    print("tasks")
    associated_tasks_str = f"""
The following tasks are associated with the skill.
Solved correctly: {solved_correctly}
Solved incorrectly: {solved_incorrectly}
Not attempted: {not_attempted}"""
    skill_development_data = f"""{associated_tasks_str}
Here is an overview over the skills
{skill_estimation_list}
"""
    system, instruction = generate_prompt(course.display_name, skill_development_data)
    text = await generate_language(instruction, language_generation_model, system)
    
    return ExplanationDescription(explanation=text)
