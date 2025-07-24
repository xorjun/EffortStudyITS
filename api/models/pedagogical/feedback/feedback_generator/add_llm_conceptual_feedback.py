from models.pedagogical.feedback.feedback_generator.base import Base_feedback_generator
from services.language_generation import generate_language
from feedback.schemas import Evaluated_feedback_submission
from db import database

class LLM_conceptual_explanation_generator(Base_feedback_generator):

    def __init__(self, textual_feedback_only: bool = True) -> None:
        super().__init__()
        self.textual_feedback_only = textual_feedback_only

    async def generate_feedback(self, predicted_step: str, submission: Evaluated_feedback_submission):
        task_json = await database.get_task(submission.task_unique_name)
        previous_state = task_json.prefix+submission.code
        task_description = task_json.task
        test_messages = "\n".join([test["message"] for test in submission.test_results])
        instruction, system = self.generate_instruction(predicted_step, previous_state, task_description, test_messages=test_messages)
        course_settings = await database.get_course_settings_for_user(submission.user_id, submission.course_unique_name)
        language_generation_model = course_settings["language_generation_model"]
        conceptual_explanation = await generate_language(instruction, system=system, model=language_generation_model)
        conceptual_explanation = conceptual_explanation.strip("'").strip().strip("`")
        if self.textual_feedback_only: 
            return conceptual_explanation
        else:
            return predicted_step + "\n" + conceptual_explanation
    
#    def generate_instruction(self, predicted_step, previous_state, task_description, test_messages):
#        system = """You are a tutor suporting a student in programming. You are a professional, helpful and kind. 
#You want to provide just enough support, so that the student can continue on their own."""
#        instruction = f"""This is a programming task that a student tried to solve: 
#{task_description}
#
#The current state of the students attempt at the task is: 
#{previous_state}
#
#A prediction model has predicted the following next step: 
#{predicted_step}
#
#Additionally, you can consider the failure messages from automated unit-tests on the students current state. They can hint at problems in the student code.
#But be careful, the unit-test messages can also be incomplete and misleading. The unit test Messages are: 
#{test_messages}
#
#Please explain to the student in one or two sentences the key concept they need to arrive from the current state at this particular next step.
#Note that the predicted step is not known by the student as they have not yet taken it. Be careful to not reveal the full solution or any further steps.
#Adress the student directly.
#
#**Explanation:**
#"""
#        return instruction, system

    def generate_instruction(self, predicted_step, previous_state, task_description, test_messages):
        system = """You are a **tutor** suporting a student in programming. You are **professional, helpful and kind**. 
You want to provide **just enough support**, so that the student can continue on their own."""
        instruction = f"""## 1. Examples
Here are two examples of helpful conceptual explanations of predicted next student step:

### Example 1

**Task Description**
Write a that takes two parameters: a list of numbers and an integer threshold. The function should create a new list containing all numbers in the input list greater than the given threshold. The order of numbers in the result list should be the same as in the input list.

**previous state:**
```python
def get_larger_elements(int_list, thresh):
    new_list = []
    for i in range(0, len(int_list) - 1):
        if integer >= thresh:
            new_list.append(integer)
    return new_list
```

**Reasonable next step:**
```python
def get_larger_elements(int_list, thresh):
    new_list = []
    for i in range(0, len(int_list)):
        if integer > thresh:
            new_list.append(integer)
    return new_list
```

**Explanation:**
Well done, you are almost ready. There are just a few small corrections to be done. First of all, you should consider how the range function works in python. 
The lower limit (first parameter) of range will be included in the resulting indices, but the upper limit (second parameter) not.
Additionally, re-read the task-description carefully to spot the second mistake. Hint: it has to do with how you compare the size of two numbers.

### Example 2

**Explanation:**
Write a function of a factorial: the product of all positive interegers less or equal to a given positive integer: 
$$n! := \prod_{{i=1}}^n i$$
Note, that the factorial is not defined for negative numbers.

**previous state:**
```python
def factorial(n):
#!prefix!#
    if n < 0:
        raise ValueError("Factorial is undefined for negative numbers.")
```

**Reasonable next step:**
```python
def factorial(n):
#!prefix!#
    if n < 0:
        raise ValueError("Factorial is undefined for negative numbers.")
    elif n == 0:
        return 1
```

**Explanation:**
Good start, now you have different options of actually implementing the factorial calculation. You could eithe go for a recursive approach or use a loop. 
The recursive approach would include a termination case, can you think about what that would be? Hint: The factorial of 0 is defined as 1.

## 2. Task Description:
This is a programming task that a student tried to solve:
{task_description}

## 3. Previous State:
The current state of the students attempt at the task is: 
{previous_state}

## 4. Test Messages:
Additionally, you can consider the failure messages from automated unit-tests on the students current state. They can hint at problems in the student code.
But be careful, the unit-test messages can also be incomplete and misleading. The unit test Messages are: 
{test_messages}

## 5. Predicted Step:
A prediction model has predicted the following next step: 
{predicted_step}

Please explain to the student in one or two sentences the key concept they need to arrive from the current state at this particular next step.
Note that the predicted step is not known by the student as they have not yet taken it. Be careful to not reveal the full solution or any further step.
Adress the student directly.

## Explanation:
"""
        return instruction, system