import re
import asyncio
from models.domain.executor import check_user_code, execute_code, execute_code_judge0, process_plt_plots
from courses.schemas import TaskType
from models.domain.submissions.judge0_string_builder import getExecutableString_plotFunction, getExecutableString_function, getExecutableString_runPlot
from db.db_connector_beanie import User
from submissions.schemas import Base_Submission, Tested_Submission
import traceback

from db import database
from sys import __stdout__
import json


async def handle_submission(submission: Base_Submission, user: User):
    """Split point for all types of submissions."""
    task = await database.get_task(submission.task_unique_name)
    match task.type:
        case TaskType.Function | TaskType.Print:
            tested_submission = await handle_code_submission(submission, task, user)
        case TaskType.MultipleChoice:
            tested_submission = await handle_mc_submission(submission, task, user)
        case TaskType.PlotFunction:
            tested_submission = await handle_code_submission(submission, task, user)
        case _:
            raise ValueError(f"Task type '{task.type}' not recognized.")
    await database.log_code_submission(tested_submission)
    return  {"submission_id": str(tested_submission.id)}

async def handle_code_submission(submission: Base_Submission, task_json, user: User):
    """Preprocess coda and run a series of test cases on a code submission.

    Args:
        submission (Code_submission): Submission object as defined in schemas.py
    """
    #course_enrollment = await database.get_course_enrollment(user, course_unique_name=submission.course_unique_name)
    try:
        test_results = await run_tests(task_json, submission.code)
    except asyncio.TimeoutError as e:
            submission.type = "timed_out_submission"
            await database.log_code_submission(submission)
    valid_solution = all([result["status"] for result in test_results]) > 0
    
    # return example solution only if PlotFunction
    reference_output = ""
    if task_json.type in [TaskType.PlotFunction]:
        solution_code = task_json.prefix + '\n' + task_json.example_solution
        run_code = getExecutableString_runPlot(solution_code, task_json.function_name, {})
        result_json = await execute_code(run_code)
        reference_output = process_plt_plots(result_json["func_queue"])

    # Log code submit to database
    tested_submission = Tested_Submission(task_unique_name = submission.task_unique_name,
                                          course_unique_name=submission.course_unique_name,
                                          code = submission.code,
                                          possible_choices = [],
                                          correct_choices = [],
                                          selected_choices = [],
                                          test_results = test_results,
                                          user_id=user.id,
                                          type="submission",
                                          submission_time=submission.submission_time,
                                          valid_solution=valid_solution,
                                          reference_output=reference_output)
    #TODO: Handle course and enrollment updates by learner model, trigger learner model.
    if task_json.type not in [TaskType.PlotFunction]:
        await mark_task_completed(submission.task_unique_name, user)
    return tested_submission

async def handle_mc_submission(submission: Base_Submission, task_json, user: User):
    test_results = []
    valid_solution = True

    possible_choices = task_json.possible_choices
    correct_choices = task_json.correct_choices
    selected_choices = submission.selected_choices
    choice_explanations = task_json.choice_explanations
    
    course = await database.get_course(submission.course_unique_name)

    # TODO surveys could be multiple choice
    if course.domain=="Surveys":
        if len(selected_choices) != 1:
            result_msg="Only 1 answer is expected. Please choose only 1 option."
            valid_solution = False
        else:
            result_msg="Test success."
            valid_solution = True
    else: 
        # Check which choices were made
        answers = [element in selected_choices for element in possible_choices]
        # Check which choices are correct
        results = [a == b for a, b in zip(answers, correct_choices)]
        # Check if all choices are correct
        valid_solution = all(results)
        
        success_text = "Test success:" if valid_solution else "Test failure:"
        result_msg = f"{success_text} \n"

        for choice, correct, explanation in zip(possible_choices, results, choice_explanations):
            correct_choice_msg = "correct" if correct else f"incorrect Reason: \n{explanation}"
            result_msg = f"{result_msg}{choice} is {correct_choice_msg}\n\n"


    test_result = {"test_name": "test_for_mc", "status": valid_solution, "message": result_msg}
    test_results.append(test_result)

    # Log code submit to database
    tested_submission = Tested_Submission(task_unique_name = submission.task_unique_name, 
                                               course_unique_name=submission.course_unique_name,
                                               code = submission.code, 
                                               possible_choices = possible_choices,
                                               correct_choices = correct_choices,
                                               selected_choices = selected_choices, 
                                               test_results = test_results,
                                               user_id=user.id, 
                                               type="submission",
                                               submission_time=submission.submission_time, 
                                               valid_solution=valid_solution)
    #TODO: Handle course and enrollment updates by learner model, trigger learner model.
    await mark_task_completed(submission.task_unique_name, user)
    return tested_submission

async def mark_task_completed(task_unique_name: str, user: User):
    course = await database.get_course(unique_name=user.current_course)
    course_enrollment = await database.get_course_enrollment(user, course_unique_name=course.unique_name)
    if not task_unique_name in course_enrollment.tasks_completed:
        course_enrollment.tasks_completed.append(task_unique_name)
        if course.curriculum == course_enrollment.tasks_completed:
            if course_enrollment.course_unique_name not in course_enrollment.completed:
                course_enrollment.completed = True
        await database.update_course_enrollment(course_enrollment, {"completed": course_enrollment.completed, 
                                                                    "tasks_completed": course_enrollment.tasks_completed})

async def run_tests(task_json, code: str):
    tests = task_json.tests
    test_results = []
    for test_name in tests.keys():
        prefix_lines = list(range(1, task_json.prefix.strip().count("\n")+2))
        try:
            if not code.strip().startswith(task_json.prefix):
                submission_code = task_json.prefix.rstrip("\n") + "\n" + code.lstrip("\n")
            else:
                submission_code = code
            safe = check_user_code(submission_code, prefix_lines)
            if not safe: continue
            test_result = None
            test_result = await get_test_results(tests[test_name], test_name, submission_code, task_json.type)
            if test_result is None:
                raise asyncio.TimeoutError
        except Exception as e:
            test_message = str(e)
            print(traceback.format_exc())
            test_result = {"test_name": test_name, "status": 0, "message": f"Error or Exception: {test_message}"}
        test_results.append(test_result)
    return test_results

async def get_test_results(test_code, test_name, submission_code, task_type: TaskType):
    """Run a single test case in an isolated environment and output the test.reults as a dict"""
    if task_type in [TaskType.Function, TaskType.Print]:
        test_submission_code = getExecutableString_function(test_code, test_name, submission_code)
    elif task_type in [TaskType.PlotFunction]:
        test_submission_code = getExecutableString_plotFunction(test_code, test_name, submission_code)
    else: raise ValueError(f"Task type {task_type} not recognized.")
    print(test_submission_code)
    result_string = await execute_code_judge0(test_submission_code)
    
    if "##!serialization!##" in result_string:
        pattern = r".*?\##!serialization!##(.*?)\##!serialization!##.*"
        parsed_result_string = re.findall(pattern, result_string, re.DOTALL)
        if len(parsed_result_string) > 1: raise ValueError("Unexpected serialization tags.")
        result_dict = json.loads(parsed_result_string[0])
        test_result = result_dict["test_result"]
        result_message = "Test success" if test_result else "Test failure:"
        
        if task_type in [TaskType.Function, TaskType.Print]:
            message = f"{result_message} {result_dict['test_message']}".strip()
        elif task_type in [TaskType.PlotFunction]:
            result_plot = process_plt_plots(result_dict["func_queue"])
            message = f"{result_plot}".strip()
        else: raise ValueError(f"Task type '{task_type}' not recognized.")
    else:
        test_result = 0
        message = f"Test failure: {result_string}"
    return {"test_name": test_name, "status": test_result, "message": message}
