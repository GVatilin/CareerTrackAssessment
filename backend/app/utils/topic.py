from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


from app.database.models import User, Topic, Chapter
from app.schemas import TopicCreateForm, ChapterCreateForm
from sqlalchemy.future import select


async def add_topic(topic: TopicCreateForm, session: AsyncSession):
    topic = topic.model_dump()
    topic_data = Topic(**topic)
    session.add(topic_data)

    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    return True


async def add_chapter(chapter: ChapterCreateForm, session: AsyncSession):
    chapter = chapter.model_dump()
    chapter_data = Chapter(**chapter)
    session.add(chapter_data)

    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    return True


async def get_all_topics(session: AsyncSession):
    query = select(Topic)
    result = await session.scalars(query)
    return result.all()


async def get_all_chapters(session: AsyncSession):
    query = select(Chapter)
    result = await session.scalars(query)
    return result.all()