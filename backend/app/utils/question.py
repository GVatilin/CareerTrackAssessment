from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Question, User, Answer
from app.schemas import QuestionCreateForm, AnswerCreateForm, AnswerOptionsToQuestion, UserAnswerForm, CorrectAnswers
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