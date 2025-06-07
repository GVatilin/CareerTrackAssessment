from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Question
from app.schemas import QuestionCreateForm
from app.database.models import User
from sqlalchemy.future import select


async def add_question(question: QuestionCreateForm, current_user: User, session: AsyncSession):
    question = question.model_dump()
    question["author_id"] = current_user.id
    question = Question(**question)
    session.add(question)

    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    return True


async def get_all_question(session: AsyncSession):
    query = select(Question)
    result = await session.scalars(query)
    return result.all()