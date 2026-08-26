# PsycedelicAI Telegram Bot

A local Telegram bot for private AI chat and group moderation.

The bot connects Telegram to a local GPT4All server running the Llama 3.2 3B Instruct model. It also provides manual moderation commands and configurable automatic moderation rules.

## Features

- Private AI chat through GPT4All
- Local Llama 3.2 3B Instruct model
- No external AI API key required
- Telegram group moderation
- Manual delete, warn, mute, kick, ban, and report commands
- Automatic blocked-domain moderation
- Safe moderator reports
- Separate editable moderation rules
- `/reloadrules` without restarting the bot
- Owner and moderator permissions
- Secrets stored locally in `.env`

## Project structure

```text
telegram-bot/
├── .env
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── src/
    ├── __init__.py
    ├── ai_chat.py
    ├── bot.py
    ├── commands.py
    ├── config.py
    ├── moderation.py
    ├── permissions.py
    └── project2501.py
```

`.env` is local and must never be committed.

`project2501.py` contains editable moderation rules.

## Requirements

- Nobara or another Fedora-based Linux distribution
- Python 3.11 or newer
- Git
- GPT4All
- A downloaded local language model
- A Telegram bot created with BotFather

The original development system used:

```text
Nobara Linux 44
Python 3.14.7
python-telegram-bot 22.8
Llama 3.2 3B Instruct
```

## Install system packages

Open a terminal and run:

```bash
sudo dnf update -y
sudo dnf install -y python3 python3-pip python3-virtualenv python3-devel gcc git
```

Check the installation:

```bash
python3 --version
pip3 --version
git --version
```

## Download the project

Clone the repository:

```bash
cd ~/Projects
git clone https://github.com/psycedelicAI/telegram-bot.git
cd telegram-bot
```

If the project already exists locally:

```bash
cd ~/Projects/psycedelicai-telegram-bot
```

## Create the virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

The terminal prompt should now begin with:

```text
(.venv)
```

Check that the project Python is being used:

```bash
which python
python --version
```

The Python path should point inside:

```text
telegram-bot/.venv/bin/python
```

## Install Python dependencies

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

If `requirements.txt` does not exist yet:

```bash
python -m pip install python-telegram-bot python-dotenv httpx
python -m pip freeze > requirements.txt
```

Check the important packages:

```bash
python -c "import telegram; print(telegram.__version__)"
python -c "import dotenv; print('python-dotenv OK')"
```

## Create the Telegram bot

1. Open Telegram.
2. Search for `@BotFather`.
3. Send `/newbot`.
4. Choose a name.
5. Choose a username ending with `bot`.
6. Store the token securely.

The token belongs only in `.env`.

Never commit the token to GitHub and never paste it into public logs or chat.

## Find your Telegram user ID

The bot needs your numeric Telegram user ID.

The simple method is:

1. Open Telegram.
2. Search for `@userinfobot`.
3. Press Start.
4. Send `/start`.
5. Copy the numeric ID it displays.

The ID looks like:

```text
123456789
```

A username such as `@Psycedelic303` is not the same as a numeric Telegram user ID.

An alternative method is to send `/start` to your own bot and inspect the update data locally. Do not publish the complete API response because it may contain private message information.

## Configure `.env`

Copy the example file:

```bash
cp .env.example .env
chmod 600 .env
```

Open the local file:

```bash
nano .env
```

Use this structure:

```text
TELEGRAM_BOT_TOKEN=your_real_telegram_bot_token
GPT4ALL_BASE_URL=http://127.0.0.1:4891/v1
GPT4ALL_MODEL=Llama 3.2 3B Instruct
ALLOWED_TELEGRAM_USER_ID=your_numeric_telegram_user_id
MODERATOR_USER_IDS=
MODERATOR_LOG_CHAT_ID=your_private_log_chat_id
```

Do not add spaces around the equals signs.

Do not add `/chat/completions` to `GPT4ALL_BASE_URL`.

Correct:

```text
GPT4ALL_BASE_URL=http://127.0.0.1:4891/v1
```

Incorrect:

```text
GPT4ALL_BASE_URL=http://127.0.0.1:4891/v1/chat/completions
```

## Add moderators

The owner ID is configured with:

```text
ALLOWED_TELEGRAM_USER_ID=your_numeric_telegram_user_id
```

Additional moderators can be added with comma-separated numeric IDs:

```text
MODERATOR_USER_IDS=123456789,987654321
```

The owner can use:

- Private AI chat
- All moderation commands

Additional moderators can use:

- Group moderation commands
- Reports
- Rules status
- Rule reloading

Additional moderators do not receive private AI access.

## Install and configure GPT4All

Install GPT4All using the official desktop application.

In GPT4All:

1. Download a local model.
2. Load `Llama 3.2 3B Instruct`.
3. Open Settings.
4. Enable the Local API Server.
5. Use port `4891`.

The local endpoint should be:

```text
http://127.0.0.1:4891/v1
```

Test the local model:

```bash
curl http://127.0.0.1:4891/v1/models
```

The response should include:

```text
Llama 3.2 3B Instruct
```

GPT4All must be running for private AI replies to work.

GPT4All is not required for Telegram moderation commands.

## Moderation rules

Editable rules are stored in:

```text
src/project2501.py
```

Example:

```python
BLOCKED_DOMAINS = {
    "example-domain.invalid",
}

BLOCKED_ALIASES = {
}

HIGH_CONFIDENCE_TERMS = {
}

BLOCKED_TELEGRAM_PATTERNS = {
}
```

For a domain, add only the domain name:

```python
"example-domain.invalid"
```

Do not add:

```text
https://example-domain.invalid/
```

The bot checks the domain and its subdomains.

The bot also normalizes some common URL obfuscation, including:

```text
hxxp://
hxxps://
[.]
(.)
{.}
dot
zero-width characters
```

Do not store illegal files, images, videos, or complete prohibited messages.

Use safe metadata such as:

- Verified domain
- Server alias
- Telegram message ID
- Chat ID
- User ID
- Timestamp

## Reload moderation rules

After editing `src/project2501.py`, save the file and use:

```text
/reloadrules
```

The command reloads the rules without restarting the bot.

The first time `/reloadrules` is added or the Python modules are changed, restart the bot normally.

## Automatic moderation

When a message matches a configured high-confidence rule:

```text
Message detected
    ↓
Message deleted
    ↓
Sender banned
    ↓
Safe moderator report sent
```

The bot does not:

- Open suspicious links
- Download files
- Forward suspected material
- Store suspected media
- Send suspected material to GPT4All
- Submit an official Telegram abuse report automatically

The report contains safe metadata only.

## Telegram group setup

Add the bot to the group and promote it to administrator.

Give it the minimum required permissions:

- Delete messages
- Ban users
- Restrict members

Disable privacy mode through `@BotFather` if the bot must inspect ordinary group messages:

```text
/setprivacy
```

Select the bot and choose:

```text
Disable
```

Telegram still controls which users the bot can moderate. The bot cannot normally moderate the group owner or an administrator with equal or higher status.

## Available commands

### General

```text
/start
/help
/status
/rules
/reloadrules
```

### Manual moderation

Use these commands by replying to the message being moderated:

```text
/delete
/warn
/mute
/unmute
/kick
/ban
/report
```

### Unban

```text
/unban USER_ID
```

Only authorized users can use moderation commands.

## Start GPT4All

Start GPT4All and load the local model.

Keep the Local API Server enabled.

## Start the Telegram bot

From the project root:

```bash
cd ~/Projects/psycedelicai-telegram-bot
source .venv/bin/activate
python src/bot.py
```

The bot should show:

```text
Telegram bot starting
Application started
```

Keep the terminal open while the bot is running.

Stop it with:

```text
Ctrl+C
```

## Test the bot

Test private AI chat:

```text
/start
```

Then send a normal private message.

Test group access:

```text
/status
```

Test manual moderation by replying to a harmless test message:

```text
/warn
```

Test rule reloading:

1. Add a harmless test domain to `src/project2501.py`.
2. Save the file.
3. Send `/reloadrules` in the group.
4. Confirm that the bot responds that rules were reloaded.

Test automatic moderation only with a harmless dummy domain in a test group.

## Security

Never commit:

```text
.env
Telegram tokens
Private API keys
Private user data
Private moderator data
```

The `.gitignore` should contain:

```text
.env
.venv/
__pycache__/
*.py[cod]
*.db
*.sqlite
*.sqlite3
```

If a Telegram token appears in a log, screenshot, Git commit, or chat, revoke it through `@BotFather` and create a new one.

The local GPT4All API does not require an external AI API key.

## Architecture

```text
Telegram
    ↓
src/bot.py
    ├── config.py
    ├── permissions.py
    ├── commands.py
    ├── moderation.py
    └── ai_chat.py
            ↓
      GPT4All Local API
            ↓
      Llama 3.2 3B Instruct
```

Moderation rules are loaded from:

```text
src/project2501.py
```

This keeps the bot logic separate from the rules that define the group’s moderation policy.

## Project status

The bot currently supports:

- Local AI chat
- GPT4All integration
- Llama 3.2 3B Instruct
- Telegram long polling
- Manual group moderation
- Automatic domain moderation
- Moderator reports
- Separate rule configuration
- Rule reloading
- Owner and moderator permissions

This project is intended for controlled, consent-based administration of groups where the bot has explicitly been granted the required Telegram permissions.
