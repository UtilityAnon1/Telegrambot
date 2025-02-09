git clone https://github.com/UtilityAnon1/Telegrambot.git
cd Telegrambot
```

2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your Telegram bot token and other settings
```bash
cp .env.example .env
```

5. Start the bot:
```bash
python launcher.py
```

## Environment Variables

Create a `.env` file with these variables:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
OWNER_TELEGRAM_ID=your_telegram_id
GITHUB_TOKEN=your_github_token (optional, only for auto-sync)
REPO_URL=your_repo_url (optional, only for auto-sync)