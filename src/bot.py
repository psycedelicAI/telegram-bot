import logging

import httpx
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    filters,
)

from ai_chat import ask_ai
from commands import register_commands
from config import TOKEN
from moderation import automatic_moderation
from permissions import can_use_ai, deny, is_group


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


async def text_message(
    update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    message = update.effective_message

    if message is None:
        return

    if is_group(update):
        await automatic_moderation(update, context)
        return

    if not can_use_ai(update):
        await deny(update)
        return

    if not message.text:
        return

    await update.effective_chat.send_action("typing")

    try:
        answer = await ask_ai(message.text)
        await message.reply_text(answer)

    except httpx.ConnectError:
        logger.exception("GPT4All connection failed")
        await message.reply_text(
            "Could not connect to the local AI model."
        )

    except Exception:
        logger.exception("AI request failed")
        await message.reply_text(
            "Something went wrong while contacting the local AI model."
        )


def main() -> None:
    application = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    register_commands(application)

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_message,
        )
    )

    logger.info("Telegram bot starting")

    application.run_polling()


if __name__ == "__main__":
    main()


bot.py
