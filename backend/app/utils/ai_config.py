ai_url = "https://api.deepseek.com/chat/completions"
ai_model = "deepseek-chat"


async def check_ai_question_text():
    return (
        "Ты проверяешь, правильно ли ответил пользователь на вопрос. "
        "Если пользователь ответил правильно, ты возвращаешь score = 2, feedback: Всё верно! "
        "Если пользователь ответил частично правильно, ты возвращаешь score = 1, и свой feedback "
        "Если пользователь ответил неправильно ты возвращаешь score = 0, и свой feedback "
        "Оценивай не слишком строго. "
        "Верни json объект { score: int, feedback: str ] }"
    )


async def get_headers(api_key):
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }


async def payload_check_ai_question(description, answer):
    return {
        "model": ai_model,
        "messages": [
            {
                "role": "system",
                "content": await check_ai_question_text()
            },
            {
                "role": "user",
                "content": f'Вопрос: {description}. Ответ пользователя: {answer}'
            },
        ],
    }
