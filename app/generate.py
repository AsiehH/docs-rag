from openai import OpenAI
from app.settings import OPENAI_API_KEY, MODEL_NAME

client = OpenAI(api_key=OPENAI_API_KEY)


def ask(question: str) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You're a helpful assistant."},
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content
