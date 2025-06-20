from sqlalchemy.ext.asyncio import AsyncSession
import aiohttp
import json
from sqlalchemy.future import select 
from uuid import UUID


from app.database.models import AIQuestion
from app.utils.ai_config import (
    ai_url,
    get_headers,
    payload_check_ai_question,
)


async def check_ai_question_utils(question_id: UUID,
                                  user_answer: str,
                                  session: AsyncSession,
                                  api_key: str):
    url = ai_url
    headers = await get_headers(api_key)

    query = select(AIQuestion.description, AIQuestion.explanation).where(AIQuestion.id == question_id)
    res = await session.execute(query)
    question = res.one_or_none()
    question_description, question_explanation = question

    payload = await payload_check_ai_question(question_description, question_explanation, user_answer)

    async with aiohttp.ClientSession() as client:
        async with client.post(url, json=payload, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()

                ai_response_text = data["choices"][0]["message"]["content"]
                if ai_response_text.startswith("```json"):
                    ai_response_text = ai_response_text[7:-3].strip()
                ai_response = json.loads(ai_response_text)

                return {
                    "score": int(ai_response["score"]),
                    "feedback": ai_response["feedback"]
                }