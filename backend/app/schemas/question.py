from pydantic import BaseModel, ConfigDict, computed_field
from uuid import UUID
from typing import List


#  -------------Creating------------------
class QuestionCreateForm(BaseModel):
    """
    Форма создания Question с выбором вариантов ответов
    """ 
    description: str
    type: int
    topic_id: UUID
    explanation: str


class AnswerCreateForm(BaseModel):
    """
    Форма создания варианта ответа для Question
    """ 
    text: str
    is_correct: bool


class AIQuestionCreateForm(BaseModel):
    """
    Форма создания Question со свободным ответом
    """
    description: str
    topic_id: UUID
    explanation: str


# --------------Response-----------------
class QuestionResponse(BaseModel):
    id: UUID
    description: str 
    type: int
    topic_id: UUID
    explanation: str
    

class AIQuestionResponse(BaseModel):
    id: UUID
    description: str
    explanation: str

    author_id: UUID
    topic_id: UUID


class AnswerResponse(BaseModel):
    id: UUID
    text: str
    is_correct: bool
    question_id: UUID


#  -------------Update--------------------
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


#  -----------Check User answers--------------
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


class UserGenAnswerForm(BaseModel):
    """
    Форма для проверки сгенерированного вопроса
    """
    question_id: str
    description: str
    answer: str

class CorrectAnswers(BaseModel):
    """
    Возвращает список правильных вариантов ответа и правильно ли ответил пользователь
    """
    is_user_right: bool                 
    correct_answer_id: list[UUID]


#  ------------Get Questions and Answers for Quiz--------------
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


#  ------------------Quiz----------------------
class QuizResponse(BaseModel):
    """
    Возвращает квиз
    """
    questions: List[QuestionQuizResponse]
    ai_questions: List[AIQuestionQuizResponse]
    gen_question: List[str]


class QuizSubmission(BaseModel):
    """
    Форма отправки квиза
    """
    answers: List[UserAnswerForm]
    ai_answers: List[UserAIAnswerForm]
    gen_answers: List[UserGenAnswerForm]


class QuestionResult(BaseModel):
    """
    Результаты вопроса
    """
    question_id: UUID | str
    description: str
    explanation: str
    is_user_right: bool


class QuizResult(BaseModel):
    """
    Результаты квиза
    """
    answers: list[QuestionResult]
    ai_recommendations: str

    @computed_field
    @property
    def total_questions(self) -> int:
        return len(self.answers)

    @computed_field
    @property
    def score_percent(self) -> float:
        return round(self.total_correct_answers / self.total_questions * 100, 2) if self.total_questions else 0.0
    
    @computed_field
    @property
    def total_correct_answers(self) -> int:
        return sum(ans.is_user_right for ans in self.answers)
