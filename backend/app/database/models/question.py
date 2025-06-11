from sqlalchemy import Column, String, Boolean, UUID, ForeignKey, Integer
from app.database import DeclarativeBase
import uuid
from sqlalchemy.orm import validates, relationship


class Question(DeclarativeBase):
    __tablename__ = "Question"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True
    )
    
    author_id = Column(UUID, ForeignKey("Users.id"), index=True)
    author = relationship("User")
    description = Column(String)
    type = Column(Integer)         #0 - один ответ правильный, 1 - несколько ответов
    explanation = Column(String)
    
    topic_id = Column(UUID, ForeignKey("Topic.id"), index=True)
    topic = relationship("Topic")

    answers = relationship(
        "Answer",
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="select",
    )


class AIQuestion(DeclarativeBase):
    __tablename__ = "AIQuestion"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True
    )

    author_id = Column(UUID, ForeignKey("Users.id"), index=True)
    author = relationship("User")
    description = Column(String)
    explanation = Column(String)

    topic_id = Column(UUID, ForeignKey("Topic.id"), index=True)
    topic = relationship("Topic")


class Answer(DeclarativeBase):
    __tablename__ = "Answers"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True
    )

    text = Column(String)
    question_id = Column(UUID, ForeignKey("Question.id"), index=True)
    question = relationship("Question")
    is_correct = Column(Boolean)
