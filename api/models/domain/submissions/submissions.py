from _ast import Call, Del, Delete, Global, Interactive, Nonlocal, Name
import re
from typing import Any
import asyncio
import ast
from courses.schemas import TaskType
from models.domain.submissions.judge0_string_builder import getExecutableString_plotFunction, getExecutableString_function
from db.db_connector_beanie import User
from submissions.schemas import Base_Submission, Tested_Submission
from config import config
import traceback

from db import database
from sys import __stdout__
import aiohttp
import json

import io
import base64
import matplotlib.pyplot as plt


async def handle_submission(submission: Base_Submission, user: User):
    """Split point for all types of submissions."""
    task = await database.get_task(submission.task_unique_name)
    match task.type:
        case TaskType.Function | TaskType.Print:
            return await handle_code_submission(submission, task, user)
        case TaskType.MultipleChoice:
            return await handle_mc_submission(submission, task, user)
        case TaskType.PlotFunction:
            return await handle_code_submission(submission, task, user)
        case _:
            raise ValueError(f"Task type '{task.type}' not recognized.")

async def handle_code_submission(submission: Base_Submission, task_json, user: User):
    """Preprocess coda and run a series of test cases on a code submission.

    Args:
        submission (Code_submission): Submission object as defined in schemas.py
    """
    course_enrollment = await database.get_course_enrollment(user, course_unique_name=submission.course_unique_name)
    test_results = await run_tests(task_json, submission)
    valid_solution = all([result["status"] for result in test_results]) > 0

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
                                               valid_solution=valid_solution)
    #TODO: Handle course and enrollment updates by learner model, trigger learner model.
    if valid_solution and (not submission.task_unique_name in course_enrollment.tasks_completed):
        course_enrollment.tasks_completed.append(submission.task_unique_name)
        course = await database.get_course(unique_name=user.current_course)
        if course.curriculum == course_enrollment.tasks_completed:
            if course_enrollment.course_unique_name not in course_enrollment.completed:
                course_enrollment.completed = True
        await database.update_course_enrollment(course_enrollment, {"completed": course_enrollment.completed, 
                                                                    "tasks_completed": course_enrollment.tasks_completed})
    await database.log_code_submission(tested_submission)
    return  {"submission_id": str(tested_submission.id)}

async def handle_mc_submission(submission: Base_Submission, task_json, user: User):
    course_enrollment = await database.get_course_enrollment(user, course_unique_name=submission.course_unique_name)
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
    if valid_solution and (not submission.task_unique_name in course_enrollment.tasks_completed):
        course_enrollment.tasks_completed.append(submission.task_unique_name)
        course = await database.get_course(unique_name=user.current_course)
        if course.curriculum == course_enrollment.tasks_completed:
            if course_enrollment.course_unique_name not in course_enrollment.completed:
                course_enrollment.completed = True
        await database.update_course_enrollment(course_enrollment, {"completed": course_enrollment.completed, 
                                                                    "tasks_completed": course_enrollment.tasks_completed})
    await database.log_code_submission(tested_submission)
    return  {"submission_id": str(tested_submission.id)}

async def run_tests(task_json, submission):
    tests = task_json.tests
    test_results = []
    for test_name in tests.keys():
        prefix_lines = list(range(1, task_json.prefix.strip().count("\n")+2))
        try:
            submission_code = task_json.prefix + submission.code
            safe = check_user_code(submission_code, prefix_lines)
            if not safe: continue
            test_result = None
            test_result = await get_test_results(tests[test_name], test_name, submission_code, task_json.type)
            if test_result is None:
                submission.type = "timed_out_submission"
                await database.log_code_submission(submission)
                raise asyncio.TimeoutError
        except Exception as e:
            test_message = str(e)
            print(traceback.format_exc())
            test_result = {"test_name": test_name, "status": 0, "message": f"Error or Exception: {test_message}"}
        test_results.append(test_result)
    return test_results

async def get_test_results(test_code, test_name, submission_code, task_type):
    """Run a single test case in an isolated environment and output the test.reults as a dict"""
    if task_type in [TaskType.Function, TaskType.Print]:
        test_submission_code = getExecutableString_function(test_code, test_name, submission_code)
    elif task_type in [TaskType.PlotFunction]:
        test_submission_code = getExecutableString_plotFunction(test_code, test_name, submission_code)
    else: raise ValueError(f"Task type {task_type} not recognized.")
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
            result_plot = process_plt_plot(result_dict["plot_args"])
            message = f"{result_message} {result_plot}".strip()
        else: raise ValueError(f"Task type {task_type} not recognized.")
    else:
        test_result = 0
        message = f"Test failure: {result_string}"
    return {"test_name": test_name, "status": test_result, "message": message}

def process_plt_plot(plot_args):
    plot_string = ""
    for plot_arg in plot_args:
        img_stream = io.BytesIO()
        img_format = "png"
        plt.cla()
        plt.plot(*plot_arg['args'], **plot_arg['kwargs'])
        plt.savefig(img_stream, format=img_format, bbox_inches='tight')
        img_stream.seek(0)
        img_base64 = base64.b64encode(img_stream.read()).decode()
        img_style = "max-width:88%; padding: 0% 5% 0% 5%"
        plot_string = plot_string + f"\n<img alt='test plot' src='data:image/{img_format};base64,{img_base64}' style='{img_style}'>"
        #plot_string = plot_string + f"<img alt='test plot' src='data:image/{img_format};base64,BASE64' style='{img_style}'> \n"
    return plot_string

async def execute_code_judge0(code_payload, url=f"http://{config.judge0_host}:2358"):
    """Execute a code snippet in judge0 and wait for the result to return.

    Args:
        code_payload (str): string containing an executable python program
        url (str, optional): Url of the Judge0 server. Defaults to "http://host:2358".

    Raises:
        Exception: _description_

    Returns:
        _type_: _description_
    """
    async with aiohttp.ClientSession() as session:
        payload = {
            #"expected_output": "null",
            "language_id": "10",
            "max_file_size": "1000", #kb
            #"max_processes_and_or_threads": "1",
            "memory_limit": 100000, #kb
            "source_code": base64.b64encode(bytes(code_payload, 'utf-8')).decode("ascii"),
            #"stack_limit": "null",
            #"stdin": "null",
            "wall_time_limit": "10", #sec
            "cpu_time_limit": "10", #sec
            "enable_network": "false",
            "redirect_stderr_to_stdout": "true",
            }
        async with session.post(f"{url}/submissions/?base64_encoded=true", data=payload) as response:
            run_token = await response.text()
            run_token = json.loads(run_token)["token"]
        max_iter = 100
        for i in range(0, max_iter): #max_iter for querying the status
            async with session.get(f"{url}/submissions/{run_token}") as response:
                run_result = await response.text()
                run_result = json.loads(run_result)
                if run_result["status"]["description"] not in ["In Queue", "Processing"]:
                    # In case of unexpected return status, return an informative error
                    if (run_result["stdout"] is None) and (run_result["status"]["description"] != "Accepted"):
                        raise Exception("Empty run result: execution status: {0}".format(run_result))
                    elif (run_result["stdout"] is None) and (run_result["status"]["description"] == "Accepted"):
                        run_result["stdout"] = ""
                    return run_result["stdout"]
                await asyncio.sleep(0.2)
        raise Exception("Code Sandbox status frozen!")

def check_user_code(code, prefix_lines=[]):
    class ImportVisitor(ast.NodeVisitor):
        def __init__(self, prefix_lines: list=[]):
            self.prefix_lines = prefix_lines

        def visit_Import(self, node):
            if node.lineno not in self.prefix_lines:
                raise Exception("Imports are not allowed in this context.")
            else: 
                self.generic_visit(node)

        def visit_ImportFrom(self, node):
            if node.lineno not in self.prefix_lines:
                raise Exception("Imports are not allowed in this context")
            else:
                self.generic_visit(node)
        
        def visit_Interactive(self, node: Interactive):
            if node.lineno in self.prefix_lines:
                raise Exception("Interactive Mode is not allowed")
            else: 
                self.generic_visit(node)
        
        def visit_Delete(self, node: Delete):
            if node.lineno not in self.prefix_lines:
                raise Exception("Deletes are not allowed in this context")
            else:
                self.generic_visit(node)
        
        def visit_Global(self, node: Global):
            if node.lineno not in self.prefix_lines:
                raise Exception("Global Scope is not allowed")
            else:
                self.generic_visit(node)

        def visit_Nonlocal(self, node: Nonlocal):
            if node.lineno not in self.prefix_lines: 
                raise Exception("Nonlocal Scope is not allowed")
            else:
                self.generic_visit(node)
        
        #def visit_Load(self, node: Load) -> Any:
        #    raise Exception("Load not allowed")
        
        #def visit_Store(self, node: Store) -> Any:
        #    raise Exception("Store not allowed")
        
        def visit_Del(self, node: Del) -> Any:
            if node.lineno not in self.prefix_lines:
                raise Exception("Del not allowed")
            else: self.generic_visit(node)
        
        def visit_Call(self, node: Call) -> Any:
            if "id" in node.func._fields:
                func_id = node.func.id
            else:
                func_id = node.func.attr
                #module_id = node.func.value.id
            if func_id == "exec":
                raise Exception("exec() is not allowed in this context")
            if func_id in ["eval", "open", "breakpoint", "callable",
                                 "delattr", "dir", "getattr", "globals",
                                 "hasattr", "help", "id", "input", "locals", 
                                 "memoryview", "property", "setattr", 
                                 "staticmethod", "vars", "__import__"]:
                raise Exception(f"{func_id}() is not allowed in this context")
            self.generic_visit(node)

        def visit_Name(self, node: Name) -> Any:
            bad_func_list = ["exec", "eval", "open", "breakpoint", "callable",
                                 "delattr", "dir", "getattr", "globals",
                                 "hasattr", "help", "id", "input", "locals", 
                                 "memoryview", "property", "setattr", 
                                 "staticmethod", "vars", "__import__"]
            id = node.id
            if id in bad_func_list:
                raise Exception(f"Name {id} is not allowed in this context")
            self.generic_visit(node)


    ast_tree = ast.parse(code)
    visitor = ImportVisitor(prefix_lines=prefix_lines)
    visitor.visit(ast_tree)
    bad_strings = ["__builtins__", "np.distutil", "multiprocessing", "APIRouter", "asyncio", "current_active_user", "database", "run_with_timeout"]
    for string in bad_strings:
        if string in code:
            raise Exception("Bad symbol detected, please don't use {0} in your program".format(string))
    return True
