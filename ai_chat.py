import httpx

from config import BASE_URL, MODEL


async def ask_ai(text: str) -> str:
    response_url = f"{BASE_URL}/chat/completions"

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are PsycedelicAI's local AI partner. "
                    "Always answer in English. "
                    "Be clear, honest, concise, and helpful."
                ),
            },
            {
                "role": "user",
                "content": text,
            },
        ],
        "temperature": 0.7,
        "max_tokens": 500,
    }

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            response_url,
            json=payload,
        )
        response.raise_for_status()

        data = response.json()

    return data["choices"][0]["message"]["content"].strip()

