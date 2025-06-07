from pydantic import BaseModel
from uuid import UUID


class ChapterCreateForm(BaseModel):
    name: str


class TopicCreateForm(BaseModel):
    name: str
    chapter_id: UUID


class ChapterDebug(BaseModel):
    id: UUID
    name: str


class TopicDebug(BaseModel):
    id: UUID
    name: str
    chapter_id: UUID