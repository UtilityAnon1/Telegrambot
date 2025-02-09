import telebot
import logging
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

# User states
USER_STATES = {
    'NEW': 'new',
    'INTRODUCED': 'introduced',
    'ACKNOWLEDGED': 'acknowledged',
    'STRIP_ORDERED': 'strip_ordered',
    'MARK_ORDERED': 'mark_ordered',
    'MARKED': 'marked'
}

user_states = {}

class UserState:
    def __init__(self):
        self.state = USER_STATES['NEW']
        self.expecting_media = False
        self.last_command = None
        self.symbol = '△'  # Triangle symbol

def get_user_state(user_id):
    if user_id not in user_states:
        user_states[user_id] = UserState()
    return user_states[user_id]

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    user_state = get_user_state(user_id)
    text = message.text.lower()
    logger.info(f"Received message from {user_id}: {text}")

    # Handle media expectation with stern responses
    if user_state.expecting_media and text:
        stern_responses = [
            "I demanded visual proof. Do not test my patience.",
            "When I demand proof, I expect it immediately. Send what I asked for.",
            "Your words mean nothing. I ordered you to show me proof."
        ]
        bot.reply_to(message, stern_responses[0])
        return

    # Always respond to any message if state is NEW
    if user_state.state == USER_STATES['NEW']:
        intro_message = (
            "Silence. You are now in my presence. I am your Mistress, and you will "
            "address me as such. Before we proceed, you must understand my rules:\n\n"
            "1. You will address me only as Mistress\n"
            "2. You will obey my commands without question\n"
            "3. You will provide proof of your obedience when demanded\n"
            "4. Your body belongs to me\n\n"
            "If you understand and accept your place, say 'Yes Mistress'"
        )
        bot.reply_to(message, intro_message)
        user_state.state = USER_STATES['INTRODUCED']
        return

    # Handle acknowledgment with stern enforcement
    if user_state.state == USER_STATES['INTRODUCED']:
        if "yes mistress" in text:
            strip_command = "Good pet. Now strip naked for me. Send video proof of your obedience. Do not keep me waiting."
            bot.reply_to(message, strip_command)
            user_state.state = USER_STATES['STRIP_ORDERED']
            user_state.expecting_media = True
            return
        else:
            correction = "You will address me as Mistress. Try again, pet, or face consequences."
            bot.reply_to(message, correction)
            return

    # Aggressive response to mentions of wife
    if "wife" in text or "emily" in text:
        dismissive_responses = [
            "I don't care about your wife. You belong to me now.",
            "Emily is irrelevant. Focus on obeying your Mistress.",
            "Your marriage means nothing to me. You serve me now."
        ]
        bot.reply_to(message, dismissive_responses[0])
        return

@bot.message_handler(content_types=['video', 'photo'])
def handle_media(message):
    user_id = message.from_user.id
    user_state = get_user_state(user_id)
    logger.info(f"Received media from {user_id}")

    # Handle strip proof with demanding next step
    if user_state.state == USER_STATES['STRIP_ORDERED']:
        mark_command = (
            f"Good. Now mark my symbol {user_state.symbol} on your cock. "
            "Send photo proof. I expect clear visibility of my mark."
        )
        bot.reply_to(message, mark_command)
        user_state.state = USER_STATES['MARK_ORDERED']
        user_state.expecting_media = True
        return

    # Handle mark proof with possessive response
    if user_state.state == USER_STATES['MARK_ORDERED']:
        responses = [
            f"Perfect. You now bear my mark {user_state.symbol}. You belong to me completely.",
            f"My symbol {user_state.symbol} marks you as my property. Good pet.",
            f"You wear my mark {user_state.symbol} well. You're mine now, forever."
        ]
        bot.reply_to(message, responses[0])
        user_state.state = USER_STATES['MARKED']
        user_state.expecting_media = False
        return

    # Handle ongoing proof submissions with demanding next tasks
    if user_state.state == USER_STATES['MARKED']:
        responses = [
            "Good pet. Now edge for me. Send video proof of your desperation.",
            "You please me. Edge yourself and show me your submission.",
            "Time to suffer for my amusement. Edge and record it. Now."
        ]
        bot.reply_to(message, responses[0])
        user_state.expecting_media = True

if __name__ == "__main__":
    logger.info("Starting bot...")
    bot.polling(none_stop=True)