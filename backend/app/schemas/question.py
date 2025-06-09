from pydantic import BaseModel
from uuid import UUID
from typing import List


class QuestionCreateForm(BaseModel):
    description: str
    type: int
    topic_id: UUID
    explanation: str


class AIQuestionCreateForm(BaseModel):
    description: str


class QuestionResponse(BaseModel):
    id: UUID
    description: str 
    type: int
    topic_id: UUID
    explanation: str
    

class AnswerCreateForm(BaseModel):
    text: str
    is_correct: bool


class AnswerResponse(BaseModel):
    id: UUID
    text: str
    is_correct: bool
    question_id: UUID


class AnswerOptionsToQuestion(BaseModel):
    question_id: UUID


class UserAnswerForm(BaseModel):
    question_id: UUID
    selected_answer_id: List[UUID]


class CorrectAnswers(BaseModel):
    is_correct: bool
    correct_answer_id: list[UUID]


class QuestionUpdateForm(BaseModel):
    id: UUID
    description: str 
    type: int
    topic_id: UUID
    explanation: str


class QuestionID(BaseModel):
    id: UUID

class AnswerUpdateForm(BaseModel):
    id: UUID
    text: str 
    is_correct: bool


class AnswerID(BaseModel):
    id: UUID