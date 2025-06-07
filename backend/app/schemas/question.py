from pydantic import BaseModel
from uuid import UUID


class QuestionCreateForm(BaseModel):
    description: str
    type: int


class AIQuestionCreateForm(BaseModel):
    description: str


class QuestionDebug(BaseModel):
    id: UUID
    description: str 
    type: int
    

class AnswerCreateForm(BaseModel):
    text: str
    is_correct: bool


class AnswerDebug(BaseModel):
    id: UUID
    text: str
    is_correct: bool
    question_id: UUID