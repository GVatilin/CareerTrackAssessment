from sqlalchemy.ext.asyncio import AsyncSession
import aiohttp
import json
from sqlalchemy.future import select 
from uuid import UUID


from app.database.models import AIQuestion
from app.utils.ai_config import (
    ai_url,
    final_feedback,
    get_headers,
    payload_check_ai_question,
    payload_generate_ai_question,
)
from app.config import get_settings


async def check_ai_question_utils(question_id: UUID,
                                  user_answer: str,
                                  session: AsyncSession):
    query = select(AIQuestion.description).where(AIQuestion.id == question_id)
    res = await session.execute(query)
    question_description = res.one_or_none()

    return await ai_check(question_description, user_answer)
            

async def get_ai_feedback(questions):
    payload = final_feedback(questions)
    headers = await get_headers(get_settings().API_KEY)
    async with aiohttp.ClientSession() as client:
        async with client.post(ai_url, json=payload, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data["choices"][0]["message"]["content"]
            else:
                return f"check_error, status: {resp.status}"


async def generate_ai_question(topic: str, count: int):
    payload = await payload_generate_ai_question(topic, count)
    headers = await get_headers(get_settings().API_KEY)

    async with aiohttp.ClientSession() as client:
        async with client.post(ai_url, json=payload, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()

                ai_response_text = data["choices"][0]["message"]["content"]
                if ai_response_text.startswith("```json"):
                    ai_response_text = ai_response_text[7:-3].strip()
                ai_response = json.loads(ai_response_text)
                
                ans = []
                for question in ai_response["questions"]:
                    ans.append(question["description"])

                return ans
            else:
                return f"check_error, status: {resp.status}"


async def ai_check(description: str, answer: str):
    headers = await get_headers(get_settings().API_KEY)
    payload = await payload_check_ai_question(description, answer)

    async with aiohttp.ClientSession() as client:
        async with client.post(ai_url, json=payload, headers=headers) as resp:
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
            else:
                return {
                    "score": 0,
                    "feedback": f"check_error, status: {resp.status}"
                }