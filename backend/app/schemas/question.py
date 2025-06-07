from pydantic import BaseModel
from uuid import UUID
from typing import List


class QuestionCreateForm(BaseModel):
    description: str 
    answers: List[str] = []
    type: int
    right_answers: List[str] = []


class AIQuestionCreateForm(BaseModel):
    description: str


class QuestionDebug(BaseModel):
    id: UUID
    description: str 
    answers: List[str] = []
    type: int
    right_answers: List[str] = []