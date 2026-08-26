import logging

from telegram import ChatPermissions, Update
from telegram.error import TelegramError
from telegram.ext import CommandHandler, ContextTypes

from config import LOG_CHAT_ID, OWNER_ID
from permissions import (
    can_use_ai,
    can_use_moderation,
    deny,
    is_group,
)
from moderation import get_message_link

logger = logging.getLogger(__name__)


async def get_target(update: Update):
    if not can_use_moderation(update):
        await deny(update)
        return None

    if not is_group(update):
        await update.effective_message.reply_text(
            "This command only works in a group."
        )
        return None

    target = update.effective_message.reply_to_message

    if not target or not target.from_user:
        await update.effective_message.reply_text(
            "Reply to the message you want to moderate."
        )
        return None

    if target.from_user.id == OWNER_ID:
        await update.effective_message.reply_text(
            "The bot owner cannot be moderated."
        )
        return None

    return target


async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not can_use_ai(update):
        await deny(update)
        return

    await update.effective_message.reply_text(
        "PsycedelicAI bot is online."
    )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not can_use_moderation(update):
        await deny(update)
        return

    await update.effective_message.reply_text(
        "Private AI chat is available to the owner.\n\n"
        "Moderation commands:\n"
        "/delete\n"
        "/warn\n"
        "/mute\n"
        "/unmute\n"
        "/kick\n"
        "/ban\n"
        "/report\n"
        "/status\n"
        "/rules\n"
        "/unban USER_ID"
    )


async def delete_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    target = await get_target(update)

    if not target:
        return

    try:
        await target.delete()
        await update.effective_message.reply_text(
            "Message deleted."
        )
    except TelegramError:
        await update.effective_message.reply_text(
            "Could not delete the message."
        )


async def warn_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    target = await get_target(update)

    if not target:
        return

    await update.effective_message.reply_text(
        f"Warning issued to "
        f"{target.from_user.full_name}."
    )


async def mute_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    target = await get_target(update)

    if not target:
        return

    await update.effective_chat.restrict_member(
        user_id=target.from_user.id,
        permissions=ChatPermissions(
            can_send_messages=False
        ),
    )

    await update.effective_message.reply_text(
        f"{target.from_user.full_name} has been muted."
    )


async def unmute_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    target = await get_target(update)

    if not target:
        return

    permissions = ChatPermissions(
        can_send_messages=True,
        can_send_audios=True,
        can_send_documents=True,
        can_send_photos=True,
        can_send_videos=True,
        can_send_video_notes=True,
        can_send_voice_notes=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
    )

    await update.effective_chat.restrict_member(
        user_id=target.from_user.id,
        permissions=permissions,
    )

    await update.effective_message.reply_text(
        f"{target.from_user.full_name} has been unmuted."
    )


async def kick_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    target = await get_target(update)

    if not target:
        return

    await update.effective_chat.ban_member(
        user_id=target.from_user.id
    )

    await update.effective_chat.unban_member(
        user_id=target.from_user.id
    )

    await update.effective_message.reply_text(
        f"{target.from_user.full_name} was removed."
    )


async def ban_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    target = await get_target(update)

    if not target:
        return

    await update.effective_chat.ban_member(
        user_id=target.from_user.id
    )

    await update.effective_message.reply_text(
        f"{target.from_user.full_name} was banned."
    )


async def report_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    target = await get_target(update)

    if not target:
        return

    report = (
        "Manual moderation report\n"
        f"Group: {update.effective_chat.title}\n"
        f"User: {target.from_user.full_name}\n"
        f"User ID: {target.from_user.id}\n"
        f"Message ID: {target.message_id}\n"
        f"Message link: {get_message_link(target)}"
    )

    await context.bot.send_message(
        chat_id=LOG_CHAT_ID,
        text=report,
        disable_web_page_preview=True,
    )

    await update.effective_message.reply_text(
        "Report sent."
    )


async def status_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not can_use_moderation(update):
        await deny(update)
        return

    await update.effective_message.reply_text(
        "PsycedelicAI moderation bot is online."
    )


async def rules_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not can_use_moderation(update):
        await deny(update)
        return

    await update.effective_message.reply_text(
        "Reply to a message before using a moderation command."
    )


async def unban_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not can_use_moderation(update):
        await deny(update)
        return

    if not context.args:
        await update.effective_message.reply_text(
            "Usage: /unban USER_ID"
        )
        return

    try:
        user_id = int(context.args[0])

        await update.effective_chat.unban_member(
            user_id=user_id,
            only_if_banned=True,
        )

        await update.effective_message.reply_text(
            "User unbanned."
        )

    except (ValueError, TelegramError):
        await update.effective_message.reply_text(
            "Unban failed."
        )


def register_commands(application) -> None:
    application.add_handler(
        CommandHandler("start", start_command)
    )
    application.add_handler(
        CommandHandler("help", help_command)
    )
    application.add_handler(
        CommandHandler("delete", delete_command)
    )
    application.add_handler(
        CommandHandler("warn", warn_command)
    )
    application.add_handler(
        CommandHandler("mute", mute_command)
    )
    application.add_handler(
        CommandHandler("unmute", unmute_command)
    )
    application.add_handler(
        CommandHandler("kick", kick_command)
    )
    application.add_handler(
        CommandHandler("ban", ban_command)
    )
    application.add_handler(
        CommandHandler("report", report_command)
    )
    application.add_handler(
        CommandHandler("status", status_command)
    )
    application.add_handler(
        CommandHandler("rules", rules_command)
    )
    application.add_handler(
        CommandHandler("unban", unban_command)
    )
