import os

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = "8067845782:AAHvpt4QMG2D2G3-KVMox7rHhRWEb9hfStg"

# OpenAI API Key
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Bot Configuration
DUTY_MODE_ACTIVE = True
OWNER_TELEGRAM_ID = "YOUR_TELEGRAM_USER_ID"  # Replace with your Telegram user ID

# Git Configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GIT_REPO_URL = f"https://{GITHUB_TOKEN}@github.com/UtilityAnon1/Telegrambot.git" if GITHUB_TOKEN else "https://github.com/UtilityAnon1/Telegrambot.git"
GIT_BRANCH = "main"
GIT_USERNAME = "UtilityAnon1"
GIT_EMAIL = "utilityanon@gmail.com"