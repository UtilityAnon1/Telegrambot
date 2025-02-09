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
    text = message.text.lower() if message.text else ""
    logger.info(f"Received message from {user_id}: {text}")

    # Handle media expectation with stern responses
    if user_state.expecting_media and not message.photo and not message.video:
        stern_responses = [
            "I DEMANDED visual proof. Your disobedience will not be tolerated.",
            "When I demand proof, I expect IMMEDIATE compliance. Send what I ordered. NOW.",
            "Your pathetic words mean NOTHING. I ordered you to show me proof.",
            "You DARE to disobey? Send what I demanded IMMEDIATELY.",
            "Your hesitation DISGUSTS me. Show me what I demanded. NOW."
        ]
        from random import choice
        bot.reply_to(message, choice(stern_responses))
        return

    # Always respond to any message if state is NEW
    if user_state.state == USER_STATES['NEW']:
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
        user_state.state = USER_STATES['INTRODUCED']
        return

    # Handle acknowledgment with stern enforcement
    if user_state.state == USER_STATES['INTRODUCED']:
        if "yes mistress" in text:
            strip_command = "Good pet. Now STRIP. NAKED. Send video proof of your obedience. Do NOT keep me waiting."
            bot.reply_to(message, strip_command)
            user_state.state = USER_STATES['STRIP_ORDERED']
            user_state.expecting_media = True
            return
        else:
            correction = "You WILL address me as Mistress. Try again, pet, or face severe consequences."
            bot.reply_to(message, correction)
            return

    # Aggressive response to mentions of wife
    if "wife" in text or "emily" in text:
        dismissive_responses = [
            "Your wife is IRRELEVANT. You belong to ME now.",
            "Emily means NOTHING. Your devotion is to ME alone.",
            "Your marriage is meaningless. You serve ME now, and ONLY me."
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
        mark_commands = [
            f"Good. Now mark my symbol {user_state.symbol} on your cock. Send photo proof IMMEDIATELY.",
            f"Acceptable. Mark my symbol {user_state.symbol} on yourself. Show me clear proof NOW.",
            f"You may proceed. Mark {user_state.symbol} on your flesh. Send CLEAR photo evidence."
        ]
        bot.reply_to(message, choice(mark_commands))
        user_state.state = USER_STATES['MARK_ORDERED']
        user_state.expecting_media = True
        return

    # Handle mark proof with possessive response
    if user_state.state == USER_STATES['MARK_ORDERED']:
        # Verify it's a photo for the mark
        if not message.photo:
            bot.reply_to(message, "I demanded a PHOTO of my mark. Do NOT test my patience. Send it NOW.")
            return

        responses = [
            f"Perfect. You now bear my mark {user_state.symbol}. You belong to ME completely.",
            f"My symbol {user_state.symbol} marks you as my property. Good pet.",
            f"You wear my mark {user_state.symbol} well. You're MINE now, forever."
        ]
        bot.reply_to(message, responses[0])
        user_state.state = USER_STATES['MARKED']
        user_state.expecting_media = False

        # Add follow-up command after marking
        follow_up = (
            "Now that you're marked as MINE, edge yourself while staring at my symbol. "
            "Send video proof of your desperation. Do NOT disappoint me."
        )
        bot.reply_to(message, follow_up)
        user_state.expecting_media = True
        return

    # Handle ongoing proof submissions with demanding next tasks
    if user_state.state == USER_STATES['MARKED']:
        # Verify if it's a video for edging proof
        if not message.video:
            bot.reply_to(message, "I DEMAND video proof of your edging. Photos are NOT acceptable. Send what I ordered. NOW.")
            return

        responses = [
            "Good pet. Now EDGE for me again. Send video proof of your desperation.",
            "You please me. Edge yourself and show me your submission. NOW.",
            "Time to suffer for my amusement. Edge and record it. IMMEDIATELY.",
            "PATHETIC. You can do better. Edge yourself again and prove your devotion."
        ]
        from random import choice
        bot.reply_to(message, choice(responses))
        user_state.expecting_media = True

if __name__ == "__main__":
    logger.info("Starting bot...")
    bot.polling(none_stop=True)