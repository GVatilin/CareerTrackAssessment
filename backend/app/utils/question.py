from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Question, User, Answer
from app.schemas import QuestionCreateForm, AnswerCreateForm
from sqlalchemy.future import select


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


async def get_all_questions(session: AsyncSession):
    query = select(Question)
    result = await session.scalars(query)
    return result.all()


async def get_all_answers(session: AsyncSession):
    query = select(Answer)
    result = await session.scalars(query)
    return result.all()