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
   - Fill in your Telegram bot token and GitHub credentials
```bash
cp .env.example .env