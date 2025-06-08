from pydantic import BaseModel
from uuid import UUID


class ChapterCreateForm(BaseModel):
    name: str


class TopicCreateForm(BaseModel):
    name: str
    chapter_id: UUID


class ChapterResponse(BaseModel):
    id: UUID
    name: str


class TopicResponse(BaseModel):
    id: UUID
    name: str
    chapter_id: UUID