from telegram import Update

from config import AUTHORIZED_IDS, OWNER_ID


def is_owner(update: Update) -> bool:
    user = update.effective_user
    return user is not None and user.id == OWNER_ID


def is_moderator(update: Update) -> bool:
    user = update.effective_user
    return user is not None and user.id in AUTHORIZED_IDS


def can_use_ai(update: Update) -> bool:
    return is_owner(update)


def can_use_moderation(update: Update) -> bool:
    return is_moderator(update)


def is_group(update: Update) -> bool:
    chat = update.effective_chat

    return chat is not None and chat.type in (
        "group",
        "supergroup",
    )


async def deny(update: Update) -> None:
    message = update.effective_message

    if message is not None:
        await message.reply_text("Access denied.")


def can_target_user(update: Update, target_user_id: int) -> bool:
    return target_user_id != OWNER_ID

