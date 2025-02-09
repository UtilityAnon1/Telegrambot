import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")

# OpenAI API Key
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Bot Configuration
DUTY_MODE_ACTIVE = True
OWNER_TELEGRAM_ID = os.environ.get('OWNER_TELEGRAM_ID')

# Git Configuration - Only used in development for auto-sync
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GIT_REPO_URL = os.environ.get('REPO_URL')
GIT_BRANCH = "main"
GIT_USERNAME = os.environ.get('GIT_USERNAME', 'UtilityAnon1')
GIT_EMAIL = os.environ.get('GIT_EMAIL', 'utilityanon@gmail.com')