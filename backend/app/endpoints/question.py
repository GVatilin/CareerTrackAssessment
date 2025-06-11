from fastapi import APIRouter, Depends, status, HTTPException, Body, Query, Path
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, Optional
from uuid import UUID


from app.utils.user import get_current_user, User
from app.database.connection import get_session
from app.schemas import QuestionCreateForm, QuestionResponse, \
    AnswerCreateForm, AnswerResponse, AnswerOptionsToQuestion, \
    UserAnswerForm, CorrectAnswers, QuestionUpdateForm, \
    AnswerUpdateForm, QuizResponse, AIQuestionCreateForm, \
    QuizSubmission, AIQuestionDebug

from app.utils.question import (
    add_question,
    get_all_questions,
    get_all_answers,
    get_answers_to_question,
    user_answers,
    edit_question,
    remove_question,
    edit_answer,
    remove_answer,
    get_quiz_utils,
    add_ai_question,
    submit_quiz_utils,
    get_all_ai_questions,
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
                          answers: Annotated[list[AnswerCreateForm], Body()],
                          current_user: Annotated[User, Depends(get_current_user)],
                          session: Annotated[AsyncSession, Depends(get_session)]) -> None:
    is_success = await add_question(question, answers, current_user, session)

    if is_success:
        return {"message": "Question created"}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, \
                        detail="Error creating question")


@api_router.post('/create_ai_question',
            status_code=status.HTTP_200_OK,
            responses={
                     status.HTTP_401_UNAUTHORIZED: {
                         "descriprion": "Non authorized"
                     }
                 })
async def create_ai_question(question: Annotated[AIQuestionCreateForm, Body()],
                          current_user: Annotated[User, Depends(get_current_user)],
                          session: Annotated[AsyncSession, Depends(get_session)]) -> None:
    is_success = await add_ai_question(question, current_user, session)

    if is_success:
        return {"message": "Question created"}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, \
                        detail="Error creating question")


@api_router.get('/get_questions',
            status_code=status.HTTP_200_OK,
            responses={
                     status.HTTP_401_UNAUTHORIZED: {
                         "descriprion": "Non authorized"
                     }
                 })
async def get_question(session: Annotated[AsyncSession, Depends(get_session)]) -> list[QuestionResponse]:
    return await get_all_questions(session)


@api_router.get('/debug/get_answers',
            status_code=status.HTTP_200_OK,
            responses={
                     status.HTTP_401_UNAUTHORIZED: {
                         "descriprion": "Non authorized"
                     }
                 })
async def get_answers_debug(session: Annotated[AsyncSession, Depends(get_session)]) -> list[AnswerResponse]:
    return await get_all_answers(session)


@api_router.get('/debug/get_ai_questions',
            status_code=status.HTTP_200_OK,
            responses={
                     status.HTTP_401_UNAUTHORIZED: {
                         "descriprion": "Non authorized"
                     }
                 })
async def get_ai_questions_debug(session: Annotated[AsyncSession, Depends(get_session)]) -> list[AIQuestionDebug]:
    return await get_all_ai_questions(session)


@api_router.post('/get_answers_to_question',
            status_code=status.HTTP_200_OK,
            responses={
                     status.HTTP_401_UNAUTHORIZED: {
                         "descriprion": "Non authorized"
                     }
                 })
async def get_answers(response: AnswerOptionsToQuestion,
                      current_user: Annotated[User, Depends(get_current_user)],
                      session: Annotated[AsyncSession, Depends(get_session)]) -> list[AnswerResponse]:
    return await get_answers_to_question(response, current_user, session)


@api_router.post('/check_user_answers',
            status_code=status.HTTP_200_OK,
            responses={
                     status.HTTP_401_UNAUTHORIZED: {
                         "descriprion": "Non authorized"
                     }
                 })
async def check_user_answers(response: UserAnswerForm,
                             current_user: Annotated[User, Depends(get_current_user)],
                             session: Annotated[AsyncSession, Depends(get_session)]) -> CorrectAnswers:
    return await user_answers(response, current_user, session)


@api_router.put('/update_question',
            status_code=status.HTTP_200_OK,
            responses={
                     status.HTTP_401_UNAUTHORIZED: {
                         "descriprion": "Non authorized"
                     }
                 })
async def update_question(updated_question: QuestionUpdateForm,
                          current_user: Annotated[User, Depends(get_current_user)],
                          session: Annotated[AsyncSession, Depends(get_session)]):
    is_success = await edit_question(updated_question, session)

    if is_success:
        return {"message": "Question updated"}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, \
                        detail="Error updating question")


@api_router.delete('/questions/{question_id}',
            status_code=status.HTTP_200_OK,
            responses={
                     status.HTTP_401_UNAUTHORIZED: {
                         "descriprion": "Non authorized"
                     },
                     status.HTTP_404_NOT_FOUND: {
                         "description": "Question not found"
                     },
                 })
async def delete_question(current_user: Annotated[User, Depends(get_current_user)],
                          session: Annotated[AsyncSession, Depends(get_session)],
                          question_id: UUID = Path(..., description="ID вопроса для удаления")):
    is_success = await remove_question(question_id, session)

    if is_success:
        return {"message": "Question deletead"}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, \
                        detail="Error delete question")


@api_router.put('/update_answer',
            status_code=status.HTTP_200_OK,
            responses={
                     status.HTTP_401_UNAUTHORIZED: {
                         "descriprion": "Non authorized"
                     }
                 })
async def update_answer(updated_answer: AnswerUpdateForm,
                        current_user: Annotated[User, Depends(get_current_user)],
                        session: Annotated[AsyncSession, Depends(get_session)]):
    is_success = await edit_answer(updated_answer, session)

    if is_success:
        return {"message": "Answer updated"}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, \
                        detail="Error updating answer")


@api_router.delete('/delete_answer/{answer_id}',
            status_code=status.HTTP_200_OK,
            responses={
                     status.HTTP_401_UNAUTHORIZED: {
                         "descriprion": "Non authorized"
                     }
                 })
async def delete_answer(current_user: Annotated[User, Depends(get_current_user)],
                        session: Annotated[AsyncSession, Depends(get_session)],
                        answer_id: UUID = Path(..., description="ID варианта ответа для удаления")):
    is_success = await remove_answer(answer_id, session)

    if is_success:
        return {"message": "Answer deletead"}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, \
                        detail="Error delete answer")


@api_router.get('/quiz/get',
            status_code=status.HTTP_200_OK,
            responses={
                     status.HTTP_401_UNAUTHORIZED: {
                         "descriprion": "Non authorized"
                     }
                 })
async def get_quiz(session: Annotated[AsyncSession, Depends(get_session)],
                   count: int = Query(..., alias="n", gt=0, le=100),
                   ai_count: int = Query(..., alias="k", gt=0, le=100),
                   topic_id: Optional[UUID] = Query(None, description="ID темы (Topic)"),
                   chapter_id: Optional[UUID] = Query(None, description="ID раздела (Chapter)"),) -> QuizResponse:
    return await get_quiz_utils(session, count, ai_count, topic_id, chapter_id)


@api_router.post('/quiz/submit',
            status_code=status.HTTP_200_OK,
            responses={
                     status.HTTP_401_UNAUTHORIZED: {
                         "descriprion": "Non authorized"
                     }
                 })
async def submit_quiz(submission: QuizSubmission,
                      current_user: Annotated[User, Depends(get_current_user)],
                      session: Annotated[AsyncSession, Depends(get_session)]):
    return await submit_quiz_utils(submission, session)