from feedback.schemas import Evaluated_feedback_submission
from db import database
import random
import ast
from services.language_generation import generate_language, parse_code_response
from models.pedagogical.feedback.step_generator.utils.code_preprocessing import remove_comments, remove_docstrings, add_pass_to_empty_blocks, \
      is_valid, convert_to_single_line_strings, detangle_keywords_from_blocks, remove_orphan_decorators, \
      desolve_invalid_try
from models.pedagogical.feedback.step_generator.utils.static_analysis import get_control_list, has_empty_control_structure
from models.pedagogical.feedback.step_generator.state_space.base_selector import Base_next_step_selector
from models.pedagogical.feedback.step_generator.state_space.embedding_selector import Embedding_Selector
from models.pedagogical.feedback.step_generator.state_space.base_state_space import Base_state_space
from models.pedagogical.feedback.step_generator.state_space.rule_based_state_space import Rule_based_state_space
from tasks.schemas import Task
from tasks.schemas import PackedStateSpace, State
from models.domain.submissions.submissions import run_tests
import numpy as np


class InvalidCodeResonse(Exception):
    pass

class Synthetic_state_space_step_generator():

    language_generation_model: str

    def __init__(self, next_step_selector: Embedding_Selector, persistent_state_space: bool=True):
        self.next_step_selector = next_step_selector
        self.persistent_state_space = persistent_state_space


    async def predict_next_step(self, submission: Evaluated_feedback_submission):
        task_name = submission.task_unique_name
        task: Task = await database.get_task(task_name)
        user_id = submission.user_id
        course_id = submission.course_unique_name
        current_attempt = await database.find_attempt(task_unique_name=task_name, user_id=user_id, course_unique_name=course_id)
        course_settings = await database.get_course_settings_for_user(submission.user_id, submission.course_unique_name)
        self.language_generation_model = course_settings["language_generation_model"]

        #Preprocess user code for easier matching and parsing.
        current_snapshot = await self.preprocess_user_code(current_attempt.current_state, task)


        # Try to retrieve a state-space from the database
        if self.persistent_state_space:
            packed_state_space: PackedStateSpace = await database.get_state_space(task_name)
        else: packed_state_space = None
        state_space = Rule_based_state_space()
        if not packed_state_space is None:
            state_space.unpack(packed_state_space)
            closest_state, closest_state_index, min_distance = await self.next_step_selector.get_closest_node(state_space.states, current_snapshot, get_min_dist=True)
            new_state_space = False
            if min_distance <= 0.02:
                need_simulate_traces = False
                print(min_distance)
                print("Omitting trace simulation since a similar state already exists.")
            else:
                print(min_distance) 
                need_simulate_traces = True
        else:
            state_space.initialize(task_unique_name=task_name)
            new_state_space = True
            need_simulate_traces = True

        #Query LLM for a complete solution based on current snaphot
        if need_simulate_traces:
            print("Will try to simulate traces.")
            try:
                inferred_solution = await self.query_solution(current_snapshot, task, test_validity=self.persistent_state_space) #TODO: Remove not running tests for non-persistent state spaces after study.
                can_simulate_traces = True
            except SyntaxError:
                can_simulate_traces = False
            except InvalidCodeResonse:
                can_simulate_traces = False
            
            #Simulate a new or extend the existing state-space based on the inferred complete solution.     
            if can_simulate_traces:
                state_sequence_list = self.simulate_traces(inferred_solution, task)   
                if new_state_space:
                    state_space.infer_states(state_sequence_list, update=False)
                    closest_state, closest_state_index = await self.next_step_selector.get_closest_node(state_space.states, current_snapshot)
                    state_space.state_index_sequences = self.prune_sequence_list(state_space.state_index_sequences, state_space.states, closest_state)
                    state_space.infer_state_space()
                elif not new_state_space:
                    state_index_sequences = state_space.infer_states(state_sequence_list, update=True)
                    closest_state, closest_state_index = await self.next_step_selector.get_closest_node(state_space.states, current_snapshot)
                    state_index_sequences = self.prune_sequence_list(state_index_sequences, state_space.states, closest_state)
                    state_space.infer_state_space(state_index_sequences)

        if need_simulate_traces and new_state_space and not can_simulate_traces:
            #TODO: Maybe simulate with example solution
            return "```\nWe are sorry, no Hint could be generated for this instance.\n```"

        if need_simulate_traces:
            state_space.prune_states()
            if self.persistent_state_space: await database.update_state_space(state_space.pack(packed_state_space))

        #Vorgehen step selection:
        #1. Find closest node.
        #2. Get list of consecutive nodes.
        #3. Sample list/select list item
        next_step = await self.next_step_selector.select(state_space, current_snapshot)
        self.personalise_solution(current_snapshot, next_step)
        return f"```python\n{next_step}\n```"
    
    def prune_sequence_list(self, state_sequence_list: list[int], states: list[State], closest_state: State) -> list[int]:
        """Delete all traces from the state_sequence_list that don't include the State closest_state.

        Args:
            state_sequence_list (list[int]): _description_
            states (list[State]): _description_
            closest_state (State): _description_

        Returns:
            list[int]: Pruned state_sequence_list
        """
        state_hashes = [state.hashed_state for state in states]
        state_index = state_hashes.index(closest_state.hashed_state)
        pruned_state_sequence_list = [state_sequence for state_sequence in state_sequence_list if state_index in state_sequence]
        return pruned_state_sequence_list
    
    def personalise_solution(self, current_snapshot, next_step):
        return next_step

    def simulate_traces(self, solution, task, n=100):
        state_sequence_list = []
        for i in range(0, n):
            task_dict = task.__dict__
            state_sequence_list.append(
                self.infer_attempt(solution, task_dict, self.reverse_from_random_control)[0]
                )
        return state_sequence_list

    def infer_attempt(self, correct_solution: str, task_dict: dict, reverse_step_method,
                    reverse_step_method_2=None, method_kwargs: dict = {}, probs: list = [1]) -> list:
        """Given a correct solution to a tesk, infer how the solution might have been constituated given one or two reverse step methods

        Args:
            correct_solution (str): A python string containinge the correct solution to the task. 
            task_dict (dict): Task information that can be accessed by the reverse step methods.
            reverse_step_method (_type_): A function that reverses a state by one step
            reverse_step_method_2 (_type_, optional): Another function that reverses a state by one step
            probs (list, optional): Probabilities for using each method. Should add to one. 

        Returns:
            list: A list of snapshots. 
            dict: A dictionary of additory callbacks returned by the reverse step method.
        """
        if not correct_solution.startswith(task_dict["prefix"]):
            raise Exception("Correct solution does not start with prefix.")
        reverse_attempt = [correct_solution]
        callback_dict = {}
        max_iter = int(len(correct_solution.splitlines())*2)
        i = 0
        while (self.strip_pass_edges(reverse_attempt[-1]).strip() != task_dict["prefix"]) and (i < max_iter):
            if not reverse_step_method_2 is None: 
                if len(probs) == 2 and sum(probs)==1:
                    method = random.choices([reverse_step_method, reverse_step_method_2], probs, k=1)[0]
                    reverse_step, callbacks = method(reverse_attempt, task_dict, **method_kwargs)
                else: 
                    raise Exception("Something went wrong with reverse step method sampling")
            else:
                reverse_step, callbacks = reverse_step_method(reverse_attempt, task_dict, **method_kwargs)
            reverse_attempt.append(reverse_step)
            if callback_dict == {}:
                callback_keys = callbacks.keys()
                callback_dict = dict([(key, 0) for key in callback_keys])
            for key in callback_keys:
                callback_dict[key] += callbacks[key]
            i += 1
            print_steps=False
            if print_steps:
                print(f"Reverse Step {i+1}")
                print("-------------------------------------------")
                print(reverse_attempt[-1])
                print("--------------------------------------------")
        reverse_attempt.reverse()
        return reverse_attempt, callback_dict
    
    def strip_pass_edges(self, s):
        if s.startswith("pass"):
            s = s[4:]
        if s.endswith("pass"):
            s = s[:-4]
        return s

    def reverse_from_random_control(self, reverse_attempt: str, task_dict: dict):
        last_reverse_step = reverse_attempt[-1]
        try:
            ast_tree = ast.parse(last_reverse_step)
        except SyntaxError as e:
            print("Warning: snapshot could not be parsed:")
            print(last_reverse_step)
            print(task_dict["foldername"])
            raise e
        control_list = get_control_list(ast_tree)
        if len(control_list)==0:
            return self.reverse_last_added_line(reverse_attempt, task_dict)
        if has_empty_control_structure(control_list):
            reverse_step = self.remove_empty_control_structure(last_reverse_step, control_list)
            try: 
                ast_tree = ast.parse(reverse_step)
            except SyntaxError as e:
                if e.args[0] == "expected 'except' or 'finally' block":
                    reverse_step = desolve_invalid_try(reverse_step)
                reverse_step = add_pass_to_empty_blocks(reverse_step)
                reverse_step = remove_orphan_decorators(reverse_step)
        else:
            selected_structure = random.sample(control_list, 1)[0]
            delete_line_start = selected_structure[1]
            delete_line_end = selected_structure[2]
            reverse_step = self.safe_line_deletion(last_reverse_step, delete_line_start-1, delete_line_end-1)
        return reverse_step.strip(), {}

    def reverse_last_added_line(self, reverse_attempt: str, task_dict: dict):
        last_reverse_step = reverse_attempt[-1]
        ast_tree = ast.parse(last_reverse_step)
        control_list = get_control_list(ast_tree)
        if has_empty_control_structure(control_list):
            reverse_step = self.remove_empty_control_structure(last_reverse_step, control_list)
            try:
                ast.parse(reverse_step)
            except SyntaxError as e:
                if e.args[0] == "expected 'except' or 'finally' block":
                    desolve_invalid_try(reverse_step)
        else:
            reverse_step = self.safe_line_deletion(reverse_attempt[-1], -1, len(reverse_attempt[-1].splitlines())-1)
        return reverse_step.strip(), {}#"\n".join(reverse_attempt[-1].splitlines()[:-1]), {}

    def remove_empty_control_structure(self, reverse_step, control_list):
        is_empty_list = [elem[3] for elem in control_list]
        if True in is_empty_list:
            #Question: Use last empty index or change is_only_pass recursion?
            first_empty_index = is_empty_list.index(True)
            delete_line_start = control_list[first_empty_index][1]
            delete_line_end = control_list[first_empty_index][2]
            reverse_step = reverse_step
            for i in range(delete_line_end-delete_line_start+1):
                #The cotrol structure might exist in an else block which we do not delete right away!
                reverse_step = self.remove_line_by_index(reverse_step, delete_line_start-1, remove_else=False)
        return reverse_step
    
    async def preprocess_user_code(self, code, task: Task):
        code = task.prefix + code
        #if not is_valid(code):
        #    code = await self.fix_syntax(code)
        #    if code == "!Invalid Submission":
        #        return code
        return self.preprocess_generated_code(code)
    
    async def fix_syntax(self, code):
        instruction = f"Fix the syntax of the following code snippet:\n```\n{code}\n```\nDo only the minimal necessary changes required to have a correct syntax, nothing more. Especially do not add any lines, explanations or content to the snippet.\nFixed code:\n"
        result = await generate_language(instruction, model=self.language_generation_model)
        code = parse_code_response(result)
        if is_valid(code):
            return code
        else:
            return "!Invalid Submission"

    def preprocess_generated_code(self, code):
        code = remove_comments(code)
        try:
            #Strings and regexp might break the detangling of blocks.
            code_candidate = detangle_keywords_from_blocks(code) 
            if is_valid(code_candidate):
                code = code_candidate
        except Exception:
            pass
        code = remove_docstrings(code)
        try: 
            code_candidate = convert_to_single_line_strings(code)
            code = code_candidate
        except Exception:
            pass
        try:
            ast.parse(code)
        except Exception as e:
            if e.__class__.__name__ == "IndentationError":
                code_candidate = add_pass_to_empty_blocks(code)
                try:
                    ast.parse(code_candidate)
                    code = code_candidate
                except Exception as e:
                    pass
        code = code.strip()
        return code

    def safe_line_deletion(self, reverse_step, allow_start, allow_end):
        """Delete a line from a program while ensuring that the syntax stays correct.
        If incorrect after deletion, additional lines might be deleted to ensure correctness.

        Args:
            reverse_step (_type_): _description_
            allow_start (_type_): _description_
            allow_end (_type_): _description_

        Returns:
            _type_: _description_
        """
        original_step = reverse_step
        for line in range(allow_end, allow_start, -1):
            reverse_step = self.remove_line_by_index(reverse_step, line)
            try:
                ast.parse(reverse_step)
                break
            except SyntaxError as e:
                if e.args[0] == "expected 'except' or 'finally' block":
                    reverse_step = desolve_invalid_try(reverse_step)
                    break
                else:
                    reverse_step_candidate = add_pass_to_empty_blocks(reverse_step)
                    reverse_step_candidate = remove_orphan_decorators(reverse_step_candidate)
                    if is_valid(reverse_step_candidate):
                        reverse_step = reverse_step_candidate
                        break
                    else:
                        continue
        if not(is_valid(reverse_step)):
            print(original_step)
            raise Exception("No valid step could be created by line deletion")
        return reverse_step.strip()

    def remove_line_by_index(self, code_str, line_index, remove_else=True):
        lines = code_str.splitlines(keepends=True)
        if 0 <= line_index < len(lines):
            del lines[line_index]
            if line_index-1 >=0 and lines[line_index-1].strip() in ["else:", "finally:"] and remove_else:
                del lines[line_index-1]
        return ''.join(lines)

    async def query_solution(self, current_state: str, task: Task, recurse=True, test_validity=True) -> str:
        """Query an LLM for the complete solution given the current snapshot and parse and refine the result if necessary.

        Args:
            current_state (str): _description_
            task_description (_type_): _description_

        Raises:
            SyntaxError: Raises Syntax Error if the inferred solution is incorrect repeatedly.
        """
        instruction, system = self.create_instruction(current_state, task=task, add_solution=not recurse)
        inferred_solution = await generate_language(instruction, system=system, model=self.language_generation_model)
        inferred_solution = parse_code_response(inferred_solution)
        if not inferred_solution.startswith(task.prefix):
            inferred_solution = task.prefix + inferred_solution
        inferred_solution = self.preprocess_generated_code(inferred_solution)
        if not is_valid(inferred_solution):
            inferred_solution = await self.fix_syntax(inferred_solution)
            if inferred_solution == "!Invalid Submission":
                print("Warning, no syntactically correct solution for the task could be inferred! Step generation failed!")
                raise SyntaxError
        if test_validity:
            test_results = await run_tests(task, code=inferred_solution)
            valid_solution = all([result["status"] for result in test_results]) > 0
        else: 
            valid_solution = True
        if valid_solution: return inferred_solution
        elif recurse:
            print("Warning, valid solution not generated on first try, trying with more context...") 
            return await self.query_solution(current_state, task, recurse=False)
        else:
            print("Warning, no valid solution to task could be generated!")
            raise InvalidCodeResonse("")


    def create_instruction(self, current_step, task: Task, test_messages="Not provided", add_solution=False):
            system = """You are a prediction model for human programming behavior. You want to give a hint to students learning programming by providing them with a reasonable solution to their programming tasks."""
            if add_solution:
                example_solution_prompt = f"""## 3.1 Example solution
Please use the following example solution only as a broad reference for predicting students solution. Do NOT reveal the example solution.
```python
{task.example_solution}
```

"""
            else:
                example_solution_prompt = ""
            instruction = f"""

## 2. Task Description:    
Consider the following programming task:
"{task.task}"


## 3. Test Messages:
Additionally, you can consider the failure messages from automated unit-tests on the students current state. They can hint at problems in the student code.
But be careful, the unit-test messages can also be incomplete and misleading. The unit test Messages are: 
{test_messages}

{example_solution_prompt}
## 4. Current State:
Predict a reasonable solution for the task based of the student program. It is important to use the partial solution provided as much as possible! Use no additional import statements and no modules that were not imported so far. Only return the edited codeblock and no further explanations. Also, DON'T change the variable naming scheme used by the student if it is reasonable. The reply should be a Markdown code block. The current program state is: 
```python
{current_step}
```

## 5. Next Step:
"""
            return instruction, system
    
