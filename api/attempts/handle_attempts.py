from fastapi import APIRouter
from fastapi import Depends
from attempts.schemas import Attempt, AttemptState, NestedAttemptState
from users.schemas import User
from users.handle_users import current_active_verified_user
from db import database
from beanie import PydanticObjectId
from datetime import datetime, timedelta, timezone
from edist.sed import sed_backtrace
from edist import edits
from edist.edits import Insertion, Deletion, Replacement, Script
from fastapi import HTTPException
from attempts.exceptions import EditorFileSizeException

router = APIRouter(prefix="/attempt")


@router.get("/get_state/{task_unique_name}")
async def get_attempt_state(task_unique_name, user: User = Depends(current_active_verified_user)):
    attempt = await database.find_attempt(task_unique_name, user.id, user.current_course)
    if attempt is None:
        attempt = Attempt(user_id = str(user.id), task_unique_name=task_unique_name, state_log=[], 
                          course_unique_name=user.current_course, current_state="",
                          start_time_list=[datetime.now().astimezone(timezone.utc).strftime("%d.%m.%Y %H:%M:%S")], 
                          duration_list=[str(timedelta(0))])
        await database.create_attempt(attempt)
        course_enrollment = course_enrollment = await database.get_course_enrollment(user, user.current_course)
        tasks_attempted = course_enrollment.tasks_attempted
        if not task_unique_name in tasks_attempted:
            tasks_attempted.append(task_unique_name)
        await database.update_course_enrollment(course_enrollment, {"tasks_attempted": tasks_attempted})
        return({"attempt_id": str(attempt.id), "code": ""})
    else:
        logged_current_state = attempt.current_state
        attempt.start_time_list.append(datetime.now().astimezone(timezone.utc).strftime("%d.%m.%Y %H:%M:%S"))
        attempt.duration_list.append(str(timedelta(0)))
        await database.update_attempt(attempt)
        if user.settings["dataCollection"] == True:
            compiled_current_state = compile_state_log("", attempt.state_log)
            if compiled_current_state.strip() != logged_current_state.strip():
                state = f"\nA problem occured. We are not sure what your last state is.\nWe have compiled the following state:\n{compiled_current_state}\n but logged the following:\n{logged_current_state}"
                return({"attempt_id": str(attempt.id), "code": state})
        return({"attempt_id": str(attempt.id), "code": logged_current_state})


def compile_state_log(previous_state, change_log: list):
    if not isinstance(previous_state, list):
        previous_state = previous_state.splitlines()
    if len(change_log) == 0:
        return "\n".join(previous_state)
    else:
        storage_diff = change_log[0]["diff"]
        diff = []
        for edit in storage_diff:
            if edit[0] == "I":
                diff.append(Insertion(edit[1], edit[2]))
            elif edit[0] == "D":
                diff.append(Deletion(edit[1]))
            elif edit[0] == "R":
                inner_diff = []
                for inner_edit in edit[2]:
                    if inner_edit[0] == "I": inner_diff.append(Insertion(inner_edit[1], inner_edit[2]))
                    elif inner_edit[0] == "D": inner_diff.append(Deletion(inner_edit[1]))
                    elif inner_edit[0] == "R": inner_diff.append(Replacement(inner_edit[1], inner_edit[2]))
                inner_diff = Script(lst=inner_diff)
                diff.append(Replacement(edit[1], "".join(inner_diff.apply(list(previous_state[edit[1]])))))
            else:
                raise Exception(f"Unknown edit type: {edit[0]}")
        diff = Script(lst=diff)
        next_state = diff.apply(previous_state)
        return compile_state_log(next_state, change_log[1:])
    

def get_diff(previous_code: str, line_update: tuple):
    changed_line = line_update[0][0]
    change_to = line_update[0][1]
    previous_lines = previous_code.splitlines()
    if changed_line == -1:
        next_step_lines = change_to.splitlines()
    elif changed_line == -2:
        #-2 is the code for submissions
        return Script(lst=[])
    else:
        next_step_lines = previous_lines.copy()
        if len(previous_lines) <= changed_line:
            next_step_lines.extend(["" for i in range(0, changed_line-len(previous_lines))])
        next_step_lines[changed_line - 1] = change_to
    if len(next_step_lines) > 1500:
        raise EditorFileSizeException("Script exeeeded maximum number of lines (1500)")
    line_alignment = sed_backtrace(previous_lines, next_step_lines)
    script_lines = edits.alignment_to_script(line_alignment, previous_lines, next_step_lines)
    for i, edit in enumerate(script_lines):
        if edit.__class__.__name__ == "Replacement":
            to_replace_line = previous_lines[edit._index]
            if len(to_replace_line) > 1500:
                raise EditorFileSizeException(f"Line {edit._index} exeeds lengh-limit (1500)")
            char_diff = sed_backtrace(to_replace_line , edit._label)
            char_alignment = edits.alignment_to_script(char_diff, to_replace_line , edit._label)
            script_lines[i]._label = char_alignment
    return script_lines
    
def apply_diff(previous_code: str, diff):
    #char_list = list(previous_code)
    line_list = previous_code.splitlines()
    for i, line_edit in enumerate(diff):
        if line_edit.__class__.__name__ == "Replacement":
            rep_line = list(line_list[line_edit._index])
            rep_line = line_edit._label.apply(rep_line)
            diff[i]._label = "".join(rep_line)
    updated_code = diff.apply(line_list)
    return "\n".join(updated_code)


def transform_edit(edit):
    if hasattr(edit, "_label"):
        storage_edit = [edit.__class__.__name__[0], edit._index, edit._label]
        if storage_edit[0] == "R":
            transform_edit_inner = lambda edit: (edit.__class__.__name__[0], edit._index, edit._label) if hasattr(edit, "_label") else (edit.__class__.__name__[0], edit._index)
            storage_edit[2] = [transform_edit_inner(inner_edit) for inner_edit in storage_edit[2]]
            storage_edit = tuple(storage_edit)
    else: 
        storage_edit = (edit.__class__.__name__[0], edit._index)
    return storage_edit
    

#TODO: In first log entry very often \r string occurs. This is probably a monaco artifact and should be handled somehow!
@router.post("/log")
async def log_attempt_state(state: NestedAttemptState, user: User = Depends(current_active_verified_user)):
    attempt = await database.get_attempt(state.attempt_id)
    state.current_state =  "\n".join(state.current_state.splitlines())
    #TODO: Handle case where data collection settings are changed!
    if user.settings["dataCollection"] == True:
        state.id = str(PydanticObjectId())
        if len(attempt.state_log) > 0:
            previous_code = compile_state_log("", attempt.state_log)
        else: 
            previous_code = ""
        for i, code in enumerate(state.code_list):
            try:
                diff = get_diff(previous_code, code)
            except EditorFileSizeException as e:
                raise HTTPException(500, str(e))
            submission_id = code[0][1] if code[0][0] == -2 else ""
            storage_diff = [transform_edit(edit) for edit in diff]
            code_state = AttemptState(state_datetime=state.state_datetime_list[i], 
                                diff=storage_diff,
                                submission_id=submission_id)
            if user.settings["dataCollection"] == True:
                attempt.state_log.append(code_state)
            previous_code = apply_diff(previous_code, diff)
        if previous_code != state.current_state:
            if state.current_state.strip() == previous_code.strip():
                state.current_state = previous_code
                print("Simple state log repair through stripping occured.")
            else:
                raise NotImplementedError("State log is broken, repair not implemented!")
    if len(state.state_datetime_list) > 0:
        current_attempt_time = datetime.strptime(state.state_datetime_list[-1]["utc"], "%d.%m.%Y %H:%M:%S.%f")
        current_start_time = datetime.strptime(attempt.start_time_list[-1], "%d.%m.%Y %H:%M:%S")
        attempt.duration_list[-1] = str(current_attempt_time - current_start_time)
    attempt.current_state = state.current_state
    await database.update_attempt(attempt)
