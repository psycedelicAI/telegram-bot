import importlib
import logging
import re
from html import escape
from urllib.parse import urlparse

from telegram.error import TelegramError

import project2501
from config import LOG_CHAT_ID

logger = logging.getLogger(__name__)


BLOCKED_DOMAINS = set(project2501.BLOCKED_DOMAINS)
BLOCKED_ALIASES = set(project2501.BLOCKED_ALIASES)
BLOCKED_TELEGRAM_PATTERNS = set(
    project2501.BLOCKED_TELEGRAM_PATTERNS
)
HIGH_CONFIDENCE_TERMS = set(
    project2501.HIGH_CONFIDENCE_TERMS
)


def reload_rules() -> None:
    global BLOCKED_DOMAINS
    global BLOCKED_ALIASES
    global BLOCKED_TELEGRAM_PATTERNS
    global HIGH_CONFIDENCE_TERMS

    importlib.reload(project2501)

    BLOCKED_DOMAINS = set(project2501.BLOCKED_DOMAINS)
    BLOCKED_ALIASES = set(project2501.BLOCKED_ALIASES)
    BLOCKED_TELEGRAM_PATTERNS = set(
        project2501.BLOCKED_TELEGRAM_PATTERNS
    )
    HIGH_CONFIDENCE_TERMS = set(
        project2501.HIGH_CONFIDENCE_TERMS
    )


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


def classify(message) -> tuple[bool, list[str]]:
    text = normalize(
        (message.text or "")
        + "\n"
        + (message.caption or "")
    )

    urls = extract_urls(text)
    domains = [get_domain(url) for url in urls]
    reasons = []

    if any(domain_blocked(domain) for domain in domains):
        reasons.append("blocked domain")

    if any(
        alias.lower() in text
        for alias in BLOCKED_ALIASES
    ):
        reasons.append("blocked alias")

    if any(
        pattern.lower() in text
        for pattern in BLOCKED_TELEGRAM_PATTERNS
    ):
        reasons.append("blocked Telegram pattern")

    if urls and any(
        term.lower() in text
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

    report = (
        "Moderation report\n"
        f"Chat: {message.chat.title}\n"
        f"User: {user.full_name if user else 'Unknown'}\n"
        f"User ID: {user.id if user else 'Unknown'}\n"
        f"Message ID: {message.message_id}\n"
        f"Reason: {', '.join(reasons)}\n"
        f"Action: {', '.join(actions)}\n"
        f"Message link: {get_message_link(message)}"
    )

    try:
        await context.bot.send_message(
            chat_id=LOG_CHAT_ID,
            text=report,
            disable_web_page_preview=True,
        )
    except TelegramError:
        logger.exception(
            "Could not send moderation report"
        )


async def automatic_moderation(
    update,
    context,
) -> None:
    message = update.effective_message

    if not message:
        return

    if not message.chat:
        return

    if message.chat.type not in (
        "group",
        "supergroup",
    ):
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
