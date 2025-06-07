from fastapi import APIRouter, Depends, status, HTTPException, Body
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated


from app.utils.user import get_current_user, User
from app.database.connection import get_session
from app.schemas import QuestionCreateForm, QuestionDebug
from app.utils.question import (
    add_question,
    get_all_question,
)


api_router = APIRouter(
    prefix="/question",
    tags=["Question"]
)


@api_router.post('/create_question',
            status_code=status.HTTP_200_OK,
            responses={
                     status.HTTP_401_UNAUTHORIZED: {
                         "descriprion": "Non authorized"
                     }
                 })
async def create_question(question: Annotated[QuestionCreateForm, Body()],
                          current_user: Annotated[User, Depends(get_current_user)],
                          session: Annotated[AsyncSession, Depends(get_session)]) -> None:
    is_success = await add_question(question, current_user, session)

    if is_success:
        return {"message": "Question created"}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, \
                        detail="Error creating question")


@api_router.post('/debug/get_simple_questions',
            status_code=status.HTTP_200_OK,
            responses={
                     status.HTTP_401_UNAUTHORIZED: {
                         "descriprion": "Non authorized"
                     }
                 })
async def get_question_debug(session: Annotated[AsyncSession, Depends(get_session)]) -> list[QuestionDebug]:
    return await get_all_question(session)