from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, func
from sqlalchemy.orm import selectinload
from collections import defaultdict
from typing import List
from uuid import UUID


from app.database.models import Question, User, Answer, AIQuestion, Topic
from app.schemas import QuestionCreateForm, AnswerCreateForm, \
    AnswerOptionsToQuestion, UserAnswerForm, CorrectAnswers, \
    QuestionUpdateForm, QuestionID, AnswerUpdateForm, AnswerID, \
    QuizResponse, AIQuestionCreateForm, QuestionQuizResponse, AnswerQuizResponse


async def add_question(question: QuestionCreateForm, answers: list[AnswerCreateForm], current_user: User, session: AsyncSession):
    question = question.model_dump()
    question["author_id"] = current_user.id
    question = Question(**question)
    session.add(question)
    await session.flush()
    
    for answer in answers:
        answer_data = answer.model_dump()
        answer_data["question_id"] = question.id
        db_answer = Answer(**answer_data)

        session.add(db_answer)

    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    return True


async def add_ai_question(question: AIQuestionCreateForm, current_user: User, session: AsyncSession):
    question = question.model_dump()
    question["author_id"] = current_user.id
    question = AIQuestion(**question)
    session.add(question)

    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    return True


async def get_all_questions(session: AsyncSession):
    query = select(Question)
    result = await session.scalars(query)
    return result.all()


async def get_all_answers(session: AsyncSession):
    query = select(Answer)
    result = await session.scalars(query)
    return result.all()


async def get_answers_to_question(response: AnswerOptionsToQuestion, 
                                  current_user: User, 
                                  session: AsyncSession):
    query = select(Answer).where(Answer.question_id == response.question_id)
    result = await session.scalars(query)
    return result.all()


async def user_answers(response: UserAnswerForm,
                       current_user: User,
                       session: AsyncSession) -> CorrectAnswers:
    question = await session.get(Question, response.question_id)
    
    result = await session.execute(
        select(Answer.id).where(
            Answer.question_id == question.id,
            Answer.is_correct == True
        )
    )

    correct_ids = {row[0] for row in result.all()}
    user_ids = set(response.selected_answer_id or [])
    
    if question.type == 0:
        is_right = (len(user_ids) == 1 and next(iter(user_ids)) in correct_ids)
    else:
        is_right = (user_ids == correct_ids)

    return CorrectAnswers(
        is_correct=is_right,
        correct_answer_id=list(correct_ids),
    )


async def edit_question(updated_question: QuestionUpdateForm, session: AsyncSession):
    query = select(Question).where(Question.id == updated_question.id)
    question = await session.scalar(query)

    if not question:
        return False
    
    for key, value in updated_question.model_dump(exclude_none=True).items():
        setattr(question, key, value)
    
    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    return True


async def remove_question(question: QuestionID, session: AsyncSession):
    query_answers = delete(Answer).where(Answer.question_id == question.id)
    await session.execute(query_answers)

    query_questions = delete(Question).where(Question.id == question.id)
    await session.execute(query_questions)

    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    return True


async def edit_answer(updated_answer: AnswerUpdateForm, session: AsyncSession):
    query = select(Answer).where(Answer.id == updated_answer.id)
    answer = await session.scalar(query)

    for key, value in updated_answer.model_dump().items():
        setattr(answer, key, value)
    
    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    return True


async def remove_answer(answer: AnswerID, session: AsyncSession):
    query = delete(Answer).where(Answer.id == answer.id)
    await session.execute(query)

    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    return True


async def get_quiz_utils(session: AsyncSession, count: int, ai_count: int, topic_id: UUID, chapter_id: UUID) -> QuizResponse:
    if (topic_id is None and chapter_id is None) or (
        topic_id is not None and chapter_id is not None
        ):
        raise HTTPException(
            404,
            detail="Укажите либо topic_id, либо chapter_id, но не оба сразу"
        )
    
    q1 = select(Question).options(selectinload(Question.answers))
    q2 = select(AIQuestion)

    if topic_id:
        q1 = q1.where(Question.topic_id == topic_id)
        q2 = q2.where(AIQuestion.topic_id == topic_id)
    else:
        q1 = q1.join(Question.topic).where(Topic.chapter_id == chapter_id)
        q2 = q2.join(AIQuestion.topic).where(Topic.chapter_id == chapter_id)

    q1 = q1.order_by(func.random()).limit(count)
    res1 = await session.execute(q1)
    questions = res1.scalars().all()
    if len(questions) < count:
        raise HTTPException(404, detail="Недостаточно обычных вопросов")

    q2 = q2.order_by(func.random()).limit(ai_count)
    res2 = await session.execute(q1)
    ai_questions = res2.scalars().all()
    if len(ai_questions) < ai_count:
        raise HTTPException(404, detail="Недостаточно AI-вопросов")
    
    return QuizResponse(questions=questions, ai_questions=ai_questions)
    

