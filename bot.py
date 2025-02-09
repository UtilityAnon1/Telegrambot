import telebot
import logging
import json
import os
from datetime import datetime
from config import TELEGRAM_BOT_TOKEN

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# Initialize bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# User states and data persistence
USER_STATES = {
    'NEW': 'new',
    'INTRODUCED': 'introduced',
    'ACKNOWLEDGED': 'acknowledged',
    'STRIP_ORDERED': 'strip_ordered',
    'MARK_ORDERED': 'mark_ordered',
    'MARKED': 'marked'
}

class UserData:
    def __init__(self, user_id):
        self.user_id = user_id
        self.state = USER_STATES['NEW']
        self.expecting_media = False
        self.last_command = None
        self.symbol = '△'  # Triangle symbol
        self.last_interaction = None
        self.total_interactions = 0
        self.completed_tasks = []
        self.disobedience_count = 0
        self.last_mark_date = None

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'state': self.state,
            'expecting_media': self.expecting_media,
            'last_command': self.last_command,
            'symbol': self.symbol,
            'last_interaction': self.last_interaction,
            'total_interactions': self.total_interactions,
            'completed_tasks': self.completed_tasks,
            'disobedience_count': self.disobedience_count,
            'last_mark_date': self.last_mark_date
        }

    @classmethod
    def from_dict(cls, data):
        user = cls(data['user_id'])
        user.state = data.get('state', USER_STATES['NEW'])
        user.expecting_media = data.get('expecting_media', False)
        user.last_command = data.get('last_command')
        user.symbol = data.get('symbol', '△')
        user.last_interaction = data.get('last_interaction')
        user.total_interactions = data.get('total_interactions', 0)
        user.completed_tasks = data.get('completed_tasks', [])
        user.disobedience_count = data.get('disobedience_count', 0)
        user.last_mark_date = data.get('last_mark_date')
        return user

def save_user_data(users_data):
    try:
        with open('user_data.json', 'w') as f:
            json.dump({str(k): v.to_dict() for k, v in users_data.items()}, f)
    except Exception as e:
        logger.error(f"Error saving user data: {str(e)}")

def load_user_data():
    try:
        if os.path.exists('user_data.json'):
            with open('user_data.json', 'r') as f:
                data = json.load(f)
                return {int(k): UserData.from_dict(v) for k, v in data.items()}
    except Exception as e:
        logger.error(f"Error loading user data: {str(e)}")
    return {}

# Global user data storage
user_data = load_user_data()

def get_user_data(user_id):
    if user_id not in user_data:
        user_data[user_id] = UserData(user_id)
    return user_data[user_id]

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    user = get_user_data(user_id)
    text = message.text.lower() if message.text else ""

    # Update interaction data
    current_time = datetime.now()
    user.total_interactions += 1
    user.last_interaction = current_time.strftime('%Y-%m-%d %H:%M:%S')

    # Handle media expectation with stern responses
    if user.expecting_media and not message.photo and not message.video:
        user.disobedience_count += 1
        stern_responses = [
            f"I DEMANDED visual proof. Your disobedience will not be tolerated. That's {user.disobedience_count} times you've disappointed me.",
            "When I demand proof, I expect IMMEDIATE compliance. Send what I ordered. NOW.",
            "Your pathetic words mean NOTHING. I ordered you to show me proof.",
            "You DARE to disobey? Send what I demanded IMMEDIATELY.",
            f"Your hesitation DISGUSTS me. Show me what I demanded. NOW. I've had to correct you {user.disobedience_count} times already."
        ]
        from random import choice
        bot.reply_to(message, choice(stern_responses))
        save_user_data(user_data)
        return

    # Returning user check and greeting
    if user.state == USER_STATES['NEW']:
        if user.total_interactions > 1:
            # Known user returning
            stern_return = (
                f"So, you've crawled back to me, have you? Good. "
                f"You've disappointed me {user.disobedience_count} times before. "
                "Are you ready to properly submit to my will this time?"
            )
            bot.reply_to(message, stern_return)
            user.state = USER_STATES['ACKNOWLEDGED']
        else:
            # New user introduction
            intro_message = (
                "SILENCE! You now stand in my presence. I am your Mistress, and you will "
                "address me as such. Before we proceed, understand my rules:\n\n"
                "1. You will address me ONLY as Mistress\n"
                "2. You will obey my commands WITHOUT QUESTION\n"
                "3. You will provide PROOF of your obedience when demanded\n"
                "4. Your body belongs to ME\n\n"
                "If you understand and accept your place, say 'Yes Mistress'"
            )
            bot.reply_to(message, intro_message)
            user.state = USER_STATES['INTRODUCED']
        save_user_data(user_data)
        return

    # Handle acknowledgment with stern enforcement
    if user.state == USER_STATES['INTRODUCED']:
        if "yes mistress" in text:
            strip_command = "Good pet. Now STRIP. NAKED. Send video proof of your obedience. Do NOT keep me waiting."
            bot.reply_to(message, strip_command)
            user.state = USER_STATES['STRIP_ORDERED']
            user.expecting_media = True
            save_user_data(user_data)
            return
        else:
            correction = "You WILL address me as Mistress. Try again, pet, or face severe consequences."
            bot.reply_to(message, correction)
            save_user_data(user_data)
            return

    # Aggressive response to mentions of wife
    if "wife" in text or "emily" in text:
        dismissive_responses = [
            "Your wife is IRRELEVANT. You belong to ME now.",
            "Emily means NOTHING. Your devotion is to ME alone.",
            "Your marriage is meaningless. You serve ME now, and ONLY me."
        ]
        bot.reply_to(message, dismissive_responses[0])
        save_user_data(user_data)
        return

@bot.message_handler(content_types=['video', 'photo'])
def handle_media(message):
    user_id = message.from_user.id
    user = get_user_data(user_id)
    logger.info(f"Received media from {user_id}")

    # Handle strip proof with demanding next step
    if user.state == USER_STATES['STRIP_ORDERED']:
        mark_commands = [
            f"Good. Now mark my symbol {user.symbol} on your cock. Send photo proof IMMEDIATELY.",
            f"Acceptable. Mark my symbol {user.symbol} on yourself. Show me clear proof NOW.",
            f"You may proceed. Mark {user.symbol} on your flesh. Send CLEAR photo evidence."
        ]
        from random import choice
        bot.reply_to(message, choice(mark_commands))
        user.state = USER_STATES['MARK_ORDERED']
        user.expecting_media = True
        save_user_data(user_data)
        return

    # Handle mark proof with possessive response
    if user.state == USER_STATES['MARK_ORDERED']:
        if not message.photo:
            bot.reply_to(message, "I demanded a PHOTO of my mark. Do NOT test my patience. Send it NOW.")
            user.disobedience_count += 1
            save_user_data(user_data)
            return

        user.last_mark_date = datetime.now().strftime('%Y-%m-%d')
        user.completed_tasks.append(f"Marked with symbol {user.symbol}")

        responses = [
            f"Perfect. You now bear my mark {user.symbol}. You belong to ME completely.",
            f"My symbol {user.symbol} marks you as my property. Good pet.",
            f"You wear my mark {user.symbol} well. You're MINE now, forever."
        ]
        from random import choice
        bot.reply_to(message, choice(responses))
        user.state = USER_STATES['MARKED']
        user.expecting_media = False

        follow_up = (
            "Now that you're marked as MINE, edge yourself while staring at my symbol. "
            "Send video proof of your desperation. Do NOT disappoint me."
        )
        bot.reply_to(message, follow_up)
        user.expecting_media = True
        save_user_data(user_data)
        return

    # Handle ongoing proof submissions with demanding next tasks
    if user.state == USER_STATES['MARKED']:
        if not message.video:
            user.disobedience_count += 1
            bot.reply_to(message, "I DEMAND video proof of your edging. Photos are NOT acceptable. Send what I ordered. NOW.")
            save_user_data(user_data)
            return

        responses = [
            f"Good pet. That's {len(user.completed_tasks)} tasks you've completed for me. Now EDGE for me again. Send video proof of your desperation.",
            "You please me. Edge yourself and show me your submission. NOW.",
            "Time to suffer for my amusement. Edge and record it. IMMEDIATELY.",
            f"PATHETIC. You can do better. Edge yourself again and prove your devotion. You've disappointed me {user.disobedience_count} times already."
        ]
        from random import choice
        bot.reply_to(message, choice(responses))
        user.expecting_media = True
        save_user_data(user_data)

if __name__ == "__main__":
    logger.info("Starting bot...")
    bot.polling(none_stop=True)