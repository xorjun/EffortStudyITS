from models.domain.submissions.judge0_string_builder import getExecutableString_runFunction, getExecutableString_runPrint, getExecutableString_runPlot
from courses.schemas import TaskType
from runs.schemas import Run_code_submission, Evaluated_run_code_submission
from db.db_connector_beanie import User
from db import database
from models.domain.executor import check_user_code, execute_code, parse_argument_types, process_plt_plots


async def handle_run(submission: Run_code_submission, user: User):
    user_id = user.id
    run_result = await run_code(submission)
    
    evaluated_submission = Evaluated_run_code_submission(
        code = submission.code,
        selected_choices = [],
        submission_time=submission.submission_time,
        run_arguments=submission.run_arguments,
        run_output=run_result,
        task_unique_name=submission.task_unique_name,
        type="run",
        user_id=user_id,
        course_unique_name=submission.course_unique_name)
    await database.log_code_submission(evaluated_submission)
    return {"run_id": str(evaluated_submission.id)}

async def run_code(submission: Run_code_submission):
    task_json = await database.get_task(submission.task_unique_name)
    submission_code = task_json.prefix + submission.code
    run_arguments = parse_argument_types(submission.run_arguments)
    if task_json.type == TaskType.Function:
        run_code = getExecutableString_runFunction(submission_code, task_json.function_name, run_arguments)
    elif task_json.type == TaskType.Print:
        run_code = getExecutableString_runPrint(submission_code, task_json.function_name, run_arguments)
    elif task_json.type == TaskType.PlotFunction:
        run_code = getExecutableString_runPlot(submission_code, task_json.function_name, run_arguments)
    else:
        raise ValueError(f"Task type '{task_json.type}' not recognized.")
    
    if task_json.prefix == "": prefix_lines = []
    else: prefix_lines = list(range(1, task_json.prefix.strip().count("\n")+2))
    try:
        safe = check_user_code(submission_code, prefix_lines)
    except Exception as e:
            safe=False
            run_result = f"Error or Exception: {str(e)}"
            #test_result = {"test_name": test_name, "status": 0, "message": f"Error or Exception: {test_message}"}
    if safe:
        result_json = await execute_code(run_code)
        if task_json.type in [TaskType.Function]:
            try:
                run_result = str(result_json["run_result"])
            except Exception as e:
                run_result = result_json.splitlines()[-1]
        elif task_json.type in [TaskType.PlotFunction]:
            try:
                run_result = process_plt_plots(result_json["func_queue"])
            except Exception as e:
                print("Plots could not be processed.")
                run_result = result_json
        else:
            run_result = result_json

    return run_result