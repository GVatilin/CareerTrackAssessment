from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import List


class QuestionCreateForm(BaseModel):
    """
    Форма создания Question с выбором вариантов ответов
    """ 
    description: str
    type: int
    topic_id: UUID
    explanation: str


class AIQuestionCreateForm(BaseModel):
    """
    Форма создания Question со свободным ответом
    """
    description: str
    topic_id: UUID
    explanation: str


class QuestionResponse(BaseModel):
    id: UUID
    description: str 
    type: int
    topic_id: UUID
    explanation: str
    

class AIQuestionDebug(BaseModel):
    id: UUID
    description: str
    explanation: str

    author_id: UUID
    topic_id: UUID


class AnswerCreateForm(BaseModel):
    """
    Форма создания варианта ответа для Question
    """ 
    text: str
    is_correct: bool


class AnswerResponse(BaseModel):
    id: UUID
    text: str
    is_correct: bool
    question_id: UUID


class AnswerOptionsToQuestion(BaseModel):
    """
    Форма для возврата всех вариантов ответа к конкретному Question
    """
    question_id: UUID


class UserAnswerForm(BaseModel):
    """
    Форма для проверки выбранных пользователем вариантов ответа
    """
    question_id: UUID
    selected_answer_id: List[UUID]


class UserAIAnswerForm(BaseModel):
    """
    Форма для проверки свободного ответа пользователя
    """
    question_id: UUID
    text: str


class CorrectAnswers(BaseModel):
    """
    Возвращает список правильных вариантов ответа и правильно ли ответил пользователь
    """
    is_user_right: bool                 
    correct_answer_id: list[UUID]


class QuestionUpdateForm(BaseModel):
    """
    Форма для изменения Question
    """
    id: UUID
    description: str 
    type: int
    topic_id: UUID
    explanation: str


class AnswerUpdateForm(BaseModel):
    """
    Форма для изменения Answer
    """
    id: UUID
    text: str 
    is_correct: bool


class AnswerQuizResponse(BaseModel):
    """
    Возвращает варианты ответа для вопроса в квизе
    """
    id: UUID
    text: str

    model_config = ConfigDict(from_attributes=True)


class QuestionQuizResponse(BaseModel):
    """
    Возвращает вопрос с вариантами ответа в квизе
    """
    id: UUID
    description: str
    type: int
    answers: List[AnswerQuizResponse]

    model_config = ConfigDict(from_attributes=True)


class AIQuestionQuizResponse(BaseModel):
    """
    Возвращает вопрос с свободным ответом в квизе
    """
    id: UUID
    description: str

    model_config = ConfigDict(from_attributes=True)


class QuizResponse(BaseModel):
    """
    Возвращает квиз
    """
    questions: List[QuestionQuizResponse]
    ai_questions: List[AIQuestionQuizResponse]


class QuizSubmission(BaseModel):
    """
    Форма отправки квиза
    """
    answers: List[UserAnswerForm]
    ai_answers: List[UserAIAnswerForm]