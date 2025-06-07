from sqlalchemy import Column, String, UUID, ForeignKey
from app.database import DeclarativeBase
import uuid
from sqlalchemy.orm import validates, relationship


"""
Деление по сферам деятельности: IT, маркетинг, дизайн и тд
"""
class Chapter(DeclarativeBase):
    __tablename__ = "Chapter"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True
    )

    name = Column(String)



"""
Деление по темам внутри сферы деятельности
"""
class Topic(DeclarativeBase):
    __tablename__ = "Topic"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True
    )

    chapter_id = Column(UUID, ForeignKey("Chapter.id"), index=True)
    chapter = relationship(Chapter)
    name = Column(String)
