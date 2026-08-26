import os
from dotenv import load_dotenv

PROJECT_ROOT = "/home/psycedelic/Projects/psycedelicai-telegram-bot"

load_dotenv(
    os.path.join(PROJECT_ROOT, ".env")
)

TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    ""
).strip()

BASE_URL = os.getenv(
    "GPT4ALL_BASE_URL",
    "http://127.0.0.1:4891/v1"
).rstrip("/")

MODEL = os.getenv(
    "GPT4ALL_MODEL",
    "Llama 3.2 3B Instruct"
).strip()

OWNER_ID_TEXT = os.getenv(
    "ALLOWED_TELEGRAM_USER_ID",
    "0"
).strip()

try:
    OWNER_ID = int(OWNER_ID_TEXT)
except ValueError:
    raise RuntimeError(
        "ALLOWED_TELEGRAM_USER_ID must be a number"
    )

LOG_CHAT_ID = os.getenv(
    "MODERATOR_LOG_CHAT_ID",
    str(OWNER_ID)
).strip()

MODERATOR_IDS = set()

for value in os.getenv(
    "MODERATOR_USER_IDS",
    ""
).split(","):
    value = value.strip()

    if value.isdigit():
        MODERATOR_IDS.add(int(value))

AUTHORIZED_IDS = MODERATOR_IDS | {OWNER_ID}


def validate_config():
    if not TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is missing from .env"
        )

    if not OWNER_ID:
        raise RuntimeError(
            "ALLOWED_TELEGRAM_USER_ID is missing from .env"
        )


validate_config()
