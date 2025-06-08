from .user import User
from .settings import Settings
from .question import Question, AIQuestion, Answer
from .topic import Topic, Chapter

table_models = [
    User,
    Settings,
    Question,
    AIQuestion,
    Answer,
    Topic,
    Chapter,
]

__all__ = [
    "User",
    "Settings",
    "Question",
    "AIQuestion",
    "Answer",
    "Topic",
    "Chapter",
]