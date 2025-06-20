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


def final_feedback(description):
    return {
        "model": ai_model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Не задавай вопросов, не используй markdown, пиши обычным текстом. "
                    "Не проси что-то добавить или отправить дополнительную информацию. "
                    "Пользователь только получит этот единственный ответ, он не сможет что-то еще отправить и получить."
                )
            },
            {
                "role": "user",
                "content": (
                    "По каким темам мне надо подтянуть знания, если на тесте я ответил так:\n" + 
                    str(description) +
                    "\nтут question оначает вопрос, а is_user_right правильно ли я на него ответил\n"
                )
            },
        ],
    }
