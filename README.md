git clone https://github.com/UtilityAnon1/Telegrambot.git
cd Telegrambot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
```
Then edit `.env` with your:
- Telegram Bot Token (from @BotFather)
- Your Telegram ID (from @userinfobot)
- GitHub credentials (if using auto-sync)

4. Start the bot:
```bash
python launcher.py