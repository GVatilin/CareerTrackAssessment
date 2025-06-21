from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, func
from sqlalchemy.orm import selectinload
from uuid import UUID


from app.database.models import Question, User, Answer, AIQuestion, \
    Topic, Chapter
from app.config import get_settings
from app.schemas import QuestionCreateForm, AnswerCreateForm, \
    UserAnswerForm, CorrectAnswers, \
    QuestionUpdateForm, AnswerUpdateForm, QuizResponse, \
    AIQuestionCreateForm, QuizSubmission
from app.utils.ai_generation import check_ai_question_utils, get_ai_feedback, \
    generate_ai_question, ai_check

settings = get_settings()


async def add_question(question: QuestionCreateForm, answers: list[AnswerCreateForm], 
                       current_user: User, session: AsyncSession):
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


async def add_ai_question(question: AIQuestionCreateForm, current_user: User, 
                          session: AsyncSession):
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


async def get_all_ai_questions(session: AsyncSession):
    query = select(AIQuestion)
    result = await session.scalars(query)
    return result.all()


async def get_answers_to_question(question_id: UUID, 
                                  current_user: User, 
                                  session: AsyncSession):
    query = select(Answer).where(Answer.question_id == question_id)
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
        is_user_right=is_right,
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


async def remove_question(question_id: UUID, session: AsyncSession):
    query_answers = delete(Answer).where(Answer.question_id == question_id)
    await session.execute(query_answers)

    query_questions = delete(Question).where(Question.id == question_id)
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


async def remove_answer(answer_id: UUID, session: AsyncSession):
    query = delete(Answer).where(Answer.id == answer_id)
    await session.execute(query)

    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    return True


async def get_quiz_utils(session: AsyncSession, count: int, ai_count: int, 
                         gen_count: int, topic_id: UUID, chapter_id: UUID) -> QuizResponse:
    if (topic_id is None and chapter_id is None):
        raise HTTPException(
            404,
            detail="Укажите либо chapter_id и topic_id, либо chapter_id"
        )
    
    q1 = select(Question).options(selectinload(Question.answers))
    q2 = select(AIQuestion)

    if topic_id:
        q1 = q1.where(Question.topic_id == topic_id)
        q2 = q2.where(AIQuestion.topic_id == topic_id)
        q3 = select(Topic).where(Topic.id == topic_id)
    else:
        q1 = q1.join(Question.topic).where(Topic.chapter_id == chapter_id)
        q2 = q2.join(AIQuestion.topic).where(Topic.chapter_id == chapter_id)
        q3 = select(Chapter).where(Chapter.id == chapter_id)

    q1 = q1.order_by(func.random()).limit(count)
    res1 = await session.execute(q1)
    questions = res1.scalars().all()
    if len(questions) < count:
        raise HTTPException(404, detail="Недостаточно обычных вопросов")

    q2 = q2.order_by(func.random()).limit(ai_count)
    res2 = await session.execute(q2)
    ai_questions = res2.scalars().all()
    if len(ai_questions) < ai_count:
        raise HTTPException(404, detail="Недостаточно AI-вопросов")
    
    res3 = await session.execute(q3)
    gen_topic = res3.scalar_one_or_none().name
    gen_questions = await generate_ai_question(gen_topic, gen_count)
    
    return QuizResponse(questions=questions, ai_questions=ai_questions, gen_question=gen_questions)


async def submit_quiz_utils(submission: QuizSubmission, session: AsyncSession):
    correct_count = 0
    correct_answers = []
    for_feedback = []

    for qa in submission.answers:
        ans = {
            'question_id': qa.question_id,
            'correct_answer_id': [],
            'is_user_right': False,
        }
        result = await session.execute(
            select(Answer.id).where(
                Answer.question_id == qa.question_id,
                Answer.is_correct == True
            )
        )

        correct_ids = {row[0] for row in result.all()}
        user_ids = set(qa.selected_answer_id or [])
        question = await session.get(Question, qa.question_id)

        tmp = correct_count
        if question.type == 0:
            correct_count += (len(user_ids) == 1 and next(iter(user_ids)) in correct_ids)
        else:
            correct_count += (user_ids == correct_ids)
        if tmp < correct_count:
            ans['is_user_right'] = True
        ans['correct_answer_id'] = correct_ids
        ans["explanation"] = question.explanation
        correct_answers.append(ans)
        for_feedback.append({
            'question': f'{question.description}',
            'is_user_answer_right': ans['is_user_right']
        })

    ai_feedback = []
    for qa in submission.ai_answers:
        question = await session.get(AIQuestion, qa.question_id)
        ans = {"question_id": qa.question_id}
        res = await check_ai_question_utils(qa.question_id, qa.text, session)
        ans["text"] = qa.text
        ans["explanation"] = res["feedback"]
        ans["is_user_right"] = (res["score"] > 0)
        correct_count += (res["score"] > 0)
        ai_feedback.append(ans)
        correct_answers.append(ans)
        for_feedback.append({
            'question': f'{question.description}',
            'is_user_answer_right': ans['is_user_right']
        })

    gen_feedback = []
    for qa in submission.gen_answers:
        res = await ai_check(qa.description, qa.answer)
        ans = {"question_id": qa.question_id}
        ans["text"] = qa.answer
        ans["explanation"] = res["feedback"]
        ans["is_user_right"] = (res["score"] > 0)
        correct_count += (res["score"] > 0)
        gen_feedback.append(ans)
        correct_answers.append(ans)
        for_feedback.append({
            'question': qa.description,
            'is_user_answer_right': ans['is_user_right']
        })

    feedback_res = await get_ai_feedback(for_feedback)


    total_mc = len(submission.answers) + len(submission.ai_answers) + len(submission.gen_answers)
    return {
        "answers": correct_answers,
        "total_mc": total_mc,
        "correct_mc": correct_count,
        "score_percent": round(correct_count / total_mc * 100, 2) if total_mc else 0.0,
        "ai_answers_received": feedback_res,
        "ai_review_required": len(ai_feedback),
    }


async def get_question_count_utils(topic_id: UUID, chapter_id: UUID, session: AsyncSession):
    if topic_id:
        q1 = select(func.count(Question.id)).where(Question.topic_id == topic_id)
        count = await session.scalar(q1)

        q2 = select(func.count(AIQuestion.id)).where(AIQuestion.topic_id == topic_id)
        ai_count = await session.scalar(q2)

        return {
            "count": count,
            "ai_count": ai_count
        }

    q1 = (
        select(func.count(Question.id))
        .select_from(Question)
        .join(Question.topic)
        .where(Topic.chapter_id == chapter_id)
    )
    count = await session.scalar(q1)

    q2 = (
        select(func.count(AIQuestion.id))
        .select_from(AIQuestion)
        .join(AIQuestion.topic)
        .where(Topic.chapter_id == chapter_id)
    )
    ai_count = await session.scalar(q2)

    return {
        "count": count,
        "ai_count": ai_count
    }
    