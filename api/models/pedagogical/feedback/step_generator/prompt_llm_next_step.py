from models.pedagogical.feedback.step_generator.base import Base_step_generator
#from submissions.schemas import Code_submission
from feedback.schemas import Evaluated_feedback_submission
from db import database
#import aiohttp
#import json
from services.language_generation import generate_language

class Prompt_llm_step_generator(Base_step_generator):

    async def predict_next_step(self, submission: Evaluated_feedback_submission):
        """This implementation of give_feedback uses the ollama API to receive llm-generated next-step feedback.

        Args:
            submission (Code_submission): The users code submission
        """
        #Retrieve task info and create prompt.
        task_json = await database.get_task(submission.task_unique_name)
        previous_step = task_json.prefix+submission.code
        example_solution = task_json.prefix+task_json.example_solution
        test_messages = "\n".join([test["message"] for test in submission.test_results])
        task = task_json.task
        instruction, system = self.create_instruction(previous_step, task=task) #TODO: Get short version of tasks or differentiate between local and server.
        course_settings = await database.get_course_settings_for_user(submission.user_id, submission.course_unique_name)
        language_generation_model = course_settings["language_generation_model"]
        next_step = await generate_language(instruction, system=system, model=language_generation_model)
        next_step = self.extract_code_block(next_step)
        return next_step

    def extract_code_block(self, next_step):
        next_step = next_step.split("```\n")[0] + "```"
        return(next_step)

    def create_instruction(self, previous_step, task="", test_messages="Not provided"):
        system = """You are a prediction model for human programming behavior. You want to give a hint to students learning programming by providing them with a reasonable next step in programming tasks."""
        instruction = f"""## Examples:
Here are two Examples of a reasonably predicted next step that a student might take given their previous state:

### Example 1

**Task Description**
Write a Python code to check if the given number is palindrome. A palindrome number is a number that is the same after reverse. For example, 545 is the palindrome number.

**Previous state**
```python
def palindrome(number):
    original_num = number
    
    # reverse the given number
    reverse_num = 0
    while number > 0:
        remainder = number % 10
        reverse_num 

    if original_num == reverse_num:
        return True
    else:
        return False
```

**Next step**
```python
def palindrome(number):
    original_num = number
    
    # reverse the given number
    reverse_num = 0
    while number > 0:
        remainder = number % 10
        reverse_num = (reverse_num * 10) + remainder
        number = number // 10

    if original_num == reverse_num:
        return True
    else:
        return False
```

### Example 2
**Task Description**
For an input lists x and y, compute their Pearson correlation. Using the NumPy package.

**Previous state**
```python
def pearson_correlation(x, y):

    # Check if the input arrays have the same length
    if len(x) != len(y):
        raise ValueError("Input arrays must have the same length for Pearson correlation calculation.")

    # Calculate means
    mean_x = np.mean(x)
    mean_y = np.mean(y)

    # Calculate numerator and denominators
    numerator = np.sum((x - mean_x) * (y - mean_y))
```

**Next step**
```python
def pearson_correlation(x, y):

    # Check if the input arrays have the same length
    if len(x) != len(y):
        raise ValueError("Input arrays must have the same length for Pearson correlation calculation.")

    # Calculate means
    mean_x = np.mean(x)
    mean_y = np.mean(y)

    # Calculate numerator and denominators
    numerator = np.sum((x - mean_x) * (y - mean_y))
    denominator_x = np.sqrt(np.sum((x - mean_x)**2))
    denominator_y = np.sqrt(np.sum((y - mean_y)**2))
```

## 2. Task Description:    
Consider the following programming task:
"{task}"


## 3. Previous State:
Predict a reasonable next step of the student program. It is important to only predict the next step and not the complete solution! Use no additional import statements and no modules that were not imported so far. Also, there should be only the edited codeblock and no further explanations. The reply should be a Markdown code block. Please consider the students approach to the problem when predicting the next step. NEVER disclose the full solution. The current program state is: 
{previous_step}

## 4. Test Messages:
Additionally, you can consider the failure messages from automated unit-tests on the students current state. They can hint at problems in the student code.
But be careful, the unit-test messages can also be incomplete and misleading. The unit test Messages are: 
{test_messages}

**Next Step:**
"""
        return instruction, system