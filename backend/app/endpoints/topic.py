from fastapi import APIRouter, Depends, status, HTTPException, Body
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated


from app.utils.user import get_current_user, User
from app.database.connection import get_session
from app.schemas import TopicCreateForm, ChapterCreateForm, TopicDebug, ChapterDebug
from app.utils.topic import (
    add_topic,
    add_chapter,
    get_all_topics,
    get_all_chapters,
)


api_router = APIRouter(
    prefix="/topic",
    tags=["Topic"]
)


@api_router.post('/create_topic',
            status_code=status.HTTP_200_OK,
            responses={
                     status.HTTP_401_UNAUTHORIZED: {
                         "descriprion": "Non authorized"
                     }
                 })
async def create_topic(topic: Annotated[TopicCreateForm, Body()],
                       session: Annotated[AsyncSession, Depends(get_session)]) -> None:
    is_success = await add_topic(topic, session)

    if is_success:
        return {"message": "Topic created"}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, \
                        detail="Error creating topic")


@api_router.post('/create_chapter',
            status_code=status.HTTP_200_OK,
            responses={
                     status.HTTP_401_UNAUTHORIZED: {
                         "descriprion": "Non authorized"
                     }
                 })
async def create_chapter(chapter: Annotated[ChapterCreateForm, Body()],
                         session: Annotated[AsyncSession, Depends(get_session)]) -> None:
    is_success = await add_chapter(chapter, session)

    if is_success:
        return {"message": "Chapter created"}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, \
                        detail="Error creating chapter")


@api_router.get('/debug/get_topics',
            status_code=status.HTTP_200_OK,
            responses={
                     status.HTTP_401_UNAUTHORIZED: {
                         "descriprion": "Non authorized"
                     }
                 })
async def get_question_debug(session: Annotated[AsyncSession, Depends(get_session)]) -> list[TopicDebug]:
    return await get_all_topics(session)


@api_router.get('/debug/get_chapters',
            status_code=status.HTTP_200_OK,
            responses={
                     status.HTTP_401_UNAUTHORIZED: {
                         "descriprion": "Non authorized"
                     }
                 })
async def get_question_debug(session: Annotated[AsyncSession, Depends(get_session)]) -> list[ChapterDebug]:
    return await get_all_chapters(session)
