from pydantic import BaseModel
from typing import List


class Skill(BaseModel):
    name: str
    value: float
    gain: float

class SkillOverview(BaseModel):
    skill_list: List[Skill]


class ReasonDescription(BaseModel):
    reason: str

class ReasonData(BaseModel): # TODO: maybe use this and format in the frontend
    method_name: str
    skill_name: str
    tasks_solved_correctly: List[str]
    tasks_solved_incorrectly: List[str]
    tasks_not_attempted: List[str]

class ExplanationDescription(BaseModel):
    explanation: str