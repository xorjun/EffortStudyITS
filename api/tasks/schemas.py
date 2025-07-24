from beanie import Document
from typing import Optional, List


class Task(Document):
    unique_name: str
    display_name: str
    task: str
    example_solution: str
    tests: dict
    type: str
    prefix: str
    arguments: Optional[list]=None
    function_name: Optional[str]=None
    possible_choices: Optional[list]=None
    correct_choices: Optional[list]=None
    selected_choices: Optional[list]=None
    choice_explanations: Optional[list]=None

