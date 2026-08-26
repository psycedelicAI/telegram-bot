import logging
import re
from html import escape
from urllib.parse import urlparse

from telegram import Update
from telegram.error import TelegramError

from config import LOG_CHAT_ID
from project2501 import (
    BLOCKED_ALIASES,
    BLOCKED_DOMAINS,
    BLOCKED_TELEGRAM_PATTERNS,
    HIGH_CONFIDENCE_TERMS,
)

logger = logging.getLogger(__name__)


def normalize(text: str) -> str:
    replacements = {
        "hxxp://": "http://",
        "hxxps://": "https://",
        "[.]": ".",
        "(.)": ".",
        "{.}": ".",
        " dot ": ".",
        "[:]": ":",
        "[://]": "://",
    }

    value = text.lower()

    for old, new in replacements.items():
        value = value.replace(old, new)

    value = re.sub(
        r"[\u200b-\u200f\u2060\ufeff]",
        "",
        value,
    )

    return re.sub(r"\s+", " ", value).strip()


def extract_urls(text: str) -> list[str]:
    return re.findall(
        r"(?:https?://|www\.)[^\s<>'\"()\[\]{}]+",
        text,
        re.IGNORECASE,
    )


def get_domain(url: str) -> str:
    if url.lower().startswith("www."):
        url = "https://" + url

    if "://" not in url:
        url = "https://" + url

    try:
        return (urlparse(url).hostname or "").lower().rstrip(".")
    except ValueError:
        return ""


def domain_blocked(domain: str) -> bool:
    return any(
        domain == blocked
        or domain.endswith("." + blocked)
        for blocked in BLOCKED_DOMAINS
    )


def alias_blocked(text: str) -> bool:
    return any(
        alias.lower() in text
        for alias in BLOCKED_ALIASES
    )


def telegram_pattern_blocked(text: str) -> bool:
    return any(
        pattern.lower() in text
        for pattern in BLOCKED_TELEGRAM_PATTERNS
    )


def classify(message) -> tuple[bool, list[str]]:
    source = normalize(
        (message.text or "")
        + "\n"
        + (message.caption or "")
    )

    urls = extract_urls(source)
    domains = [get_domain(url) for url in urls]
    reasons = []

    if any(domain_blocked(domain) for domain in domains):
        reasons.append("blocked domain")

    if alias_blocked(source):
        reasons.append("blocked alias")

    if telegram_pattern_blocked(source):
        reasons.append("blocked Telegram pattern")

    if urls and any(
        term.lower() in source
        for term in HIGH_CONFIDENCE_TERMS
    ):
        reasons.append("high-confidence indicator")

    return bool(reasons), reasons


def get_message_link(message) -> str:
    if getattr(message.chat, "username", None):
        return (
            f"https://t.me/{message.chat.username}/"
            f"{message.message_id}"
        )

    chat_id = str(message.chat.id)

    if chat_id.startswith("-100"):
        return (
            f"https://t.me/c/{chat_id[4:]}/"
            f"{message.message_id}"
        )

    return "Unavailable"


async def send_report(
    context,
    message,
    reasons: list[str],
    actions: list[str],
) -> None:
    if not LOG_CHAT_ID:
        return

    user = message.from_user
    user_name = escape(
        user.full_name if user else "Unknown user"
    )

    report = (
        "⚠️ <b>Moderation report</b>\n\n"
        f"<b>Chat:</b> "
        f"{escape(message.chat.title or '(unnamed)')}\n"
        f"<b>User:</b> {user_name}\n"
        f"<b>User ID:</b> "
        f"<code>{user.id if user else 'unknown'}</code>\n"
        f"<b>Message ID:</b> "
        f"<code>{message.message_id}</code>\n"
        f"<b>Reason:</b> "
        f"{escape(', '.join(reasons))}\n"
        f"<b>Action:</b> "
        f"{escape(', '.join(actions))}\n"
        f"<b>Message link:</b> "
        f"{escape(get_message_link(message))}"
    )

    try:
        await context.bot.send_message(
            chat_id=LOG_CHAT_ID,
            text=report,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except TelegramError:
        logger.exception("Failed to send moderation report")


async def automatic_moderation(
    update: Update,
    context,
) -> None:
    message = update.effective_message

    if not message or not message.chat:
        return

    if not message.from_user:
        return

    if message.from_user.is_bot:
        return

    should_act, reasons = classify(message)

    if not should_act:
        return

    actions = []

    try:
        await context.bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id,
        )
        actions.append("message deleted")
    except TelegramError:
        actions.append("message deletion failed")

    try:
        await context.bot.ban_chat_member(
            chat_id=message.chat.id,
            user_id=message.from_user.id,
            revoke_messages=True,
        )
        actions.append("user banned")
    except TelegramError:
        actions.append("ban failed")

    await send_report(
        context,
        message,
        reasons,
        actions,
    )

