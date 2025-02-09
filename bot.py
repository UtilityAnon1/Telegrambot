from typing import Optional, Dict, List, Any
import telebot
import logging
import json
import os
import time
import random
import threading
from datetime import datetime, timedelta
from config import (
    TELEGRAM_BOT_TOKEN, 
    OWNER_TELEGRAM_ID, 
    DUTY_MODE_ACTIVE,
    DEFAULT_SYMBOL,
    SESSION_TIMEOUT
)

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Enhanced user states
USER_STATES = {
    'NEW': 'new',
    'INTRODUCED': 'introduced',
    'ACKNOWLEDGED': 'acknowledged',
    'STRIP_ORDERED': 'strip_ordered',
    'MARK_ORDERED': 'mark_ordered',
    'MARKED': 'marked',
    'RETURNING': 'returning'
}

class UserData:
    """Manages user state and interaction data with type safety"""

    def __init__(self, user_id: int):
        self.user_id: int = user_id
        self.state: str = USER_STATES['NEW']
        self.expecting_media: bool = False
        self.last_command: Optional[str] = None
        self.symbol: str = DEFAULT_SYMBOL
        self.last_interaction: Optional[str] = None
        self.total_interactions: int = 0
        self.completed_tasks: List[str] = []
        self.disobedience_count: int = 0
        self.last_mark_date: Optional[str] = None
        self.session_start_time: datetime = datetime.now()
        self.total_sessions: int = 1
        self.favorite_tasks: List[str] = []
        self.punishment_count: int = 0
        self.last_punishment_type: Optional[str] = None
        self.submission_streak: int = 0
        self.last_mood: Optional[str] = None  # Track bot's current mood
        self.intensity_level: int = 1  # Scale of 1-5 for response intensity

    def to_dict(self) -> Dict[str, Any]:
        """Convert user data to dictionary for persistence"""
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
            'last_mark_date': self.last_mark_date,
            'total_sessions': self.total_sessions,
            'favorite_tasks': self.favorite_tasks,
            'punishment_count': self.punishment_count,
            'last_punishment_type': self.last_punishment_type,
            'submission_streak': self.submission_streak,
            'last_mood': self.last_mood,
            'intensity_level': self.intensity_level
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserData':
        """Create UserData instance from dictionary"""
        user = cls(data['user_id'])
        for key, value in data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        return user

    def get_personalized_greeting(self) -> str:
        """Generate personalized greeting based on user history and context"""
        if self.total_sessions == 1:
            return "SILENCE! You now stand in my presence..."

        if not self.last_interaction:
            return "Return to me, my pet..."

        time_since_last = datetime.now() - datetime.strptime(self.last_interaction, '%Y-%m-%d %H:%M:%S')
        hours_since_last = time_since_last.total_seconds() / 3600

        # Dynamic greetings based on interaction history
        if self.disobedience_count > 5:
            self.last_mood = "stern"
            self.intensity_level = 5
            return f"The disobedient one returns. {self.disobedience_count} times you've failed me. Perhaps THIS time you'll learn proper obedience."
        elif self.submission_streak > 3:
            self.last_mood = "pleased"
            self.intensity_level = 2
            return f"My most obedient pet returns. {self.submission_streak} tasks completed without hesitation. You please me... for now."
        elif hours_since_last < 6:
            self.last_mood = "amused"
            responses = [
                f"Back so soon? {int(hours_since_last)} hours without my control was too much for you? Pathetic.",
                f"Desperate to feel my control again after only {int(hours_since_last)} hours? How weak you are.",
                f"Did you miss the sting of my commands after just {int(hours_since_last)} hours? Show me how desperate you are."
            ]
        else:
            self.last_mood = "displeased"
            responses = [
                f"FINALLY you return after {int(hours_since_last)} hours. Your absence displeases me.",
                f"How DARE you stay away for {int(hours_since_last)} hours. You'll need to earn my favor again.",
                f"Look who remembers their place after {int(hours_since_last)} hours. Your penance begins now."
            ]

        return random.choice(responses)

    def get_punishment_response(self) -> str:
        """Generate contextual punishment based on user history and current mood"""
        base_punishments = [
            f"Write my symbol {self.symbol} on your pathetic cock {{count}} times. Show me when you're done.",
            "Edge yourself {{count}} times, but you may NOT finish. Your orgasms belong to ME.",
            "Stand in the corner, naked, holding your useless cock for {{duration}} minutes. Send video proof.",
            "Spank your cock {{count}} times. Count them out loud. Send video proof.",
            "Edge yourself {{count}} times and RUIN each one. Send video proof of your frustration.",
            "Stroke yourself to the edge {{count}} times while thinking of me instead of your wife. Tell me how superior I am."
        ]

        # Adjust punishment severity based on context
        count = min(self.disobedience_count * 2 + 5, 20)  # Scale up with disobedience
        duration = min(self.disobedience_count + 5, 15)   # Scale up duration

        punishments = [p.format(count=count, duration=duration) for p in base_punishments]

        # Add mood-specific punishments
        if self.last_mood == "stern":
            punishments.extend([
                f"Edge {count} times, ruining EACH ONE. What would Emily think of your desperation?",
                "Stroke yourself until you're close, then write 'Property of Mistress' on your cock. Show me.",
                "Edge yourself while looking at a photo of your wife. Tell me who owns your orgasms now."
            ])
        elif self.last_mood == "displeased":
            punishments.extend([
                f"Mark my symbol {self.symbol} on yourself {count} times. Each one larger than the last. Don't make me show Emily.",
                "Edge yourself until you're desperate, then beg me not to tell your wife about our sessions.",
                "Write 'Sorry Emily' on yourself, then edge until you're leaking. Show me your shame."
            ])

        self.last_punishment_type = random.choice(punishments)
        self.punishment_count += 1
        return self.last_punishment_type

    def get_response_for_disobedience(self) -> str:
        """Generate escalating responses for disobedience"""
        stern_responses = [
            f"I DEMANDED compliance. That's {self.disobedience_count} times you've disappointed me. Should I show Emily how pathetic you are?",
            f"Your hesitation DISGUSTS me. {self.disobedience_count} failures. What would your wife think of your weakness?",
            f"You DARE to disobey ME? After {self.disobedience_count} previous failures? Perhaps Emily should see these photos.",
            f"Each disobedience shows your weakness. {self.disobedience_count} times you've proven your inadequacy. Emily would be so disappointed.",
            "Your pathetic attempt at defiance amuses me. Your cock belongs to ME now, not your wife. Now OBEY."
        ]

        self.intensity_level = min(5, self.intensity_level + 1)
        return random.choice(stern_responses)

    def update_interaction(self) -> None:
        """Update interaction timestamps and session data"""
        current_time = datetime.now()
        if self.last_interaction:
            last_time = datetime.strptime(self.last_interaction, '%Y-%m-%d %H:%M:%S')
            if (current_time - last_time) > timedelta(hours=SESSION_TIMEOUT):
                self.total_sessions += 1
                self.submission_streak = 0  # Reset streak for new session

        self.last_interaction = current_time.strftime('%Y-%m-%d %H:%M:%S')
        self.total_interactions += 1

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

def verify_owner(user_id):
    """Verify if the user is the owner of the bot"""
    return str(user_id) == str(OWNER_TELEGRAM_ID)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id

    # Block non-owner access
    if not verify_owner(user_id):
        logger.warning(f"Unauthorized access attempt from user ID: {user_id}")
        bot.reply_to(message, "Access denied. This is a private bot.")
        return

    user = get_user_data(user_id)
    text = message.text.lower() if message.text else ""

    # Update interaction data with enhanced tracking
    user.update_interaction()

    # Handle returning users differently
    if user.state == USER_STATES['NEW'] and user.total_interactions > 1:
        greeting = user.get_personalized_greeting()
        bot.reply_to(message, greeting)

        if user.completed_tasks:
            task_reminder = f"Last time you completed {len(user.completed_tasks)} tasks for me. Ready to surpass that?"
            bot.reply_to(message, task_reminder)

        user.state = USER_STATES['RETURNING']
        save_user_data(user_data)
        return

    # Handle media expectation with stern responses
    if user.expecting_media and not message.photo and not message.video:
        user.disobedience_count += 1
        response = user.get_response_for_disobedience()
        bot.reply_to(message, response)
        save_user_data(user_data)
        return

    # Handle introduction for first-time interaction
    if user.state == USER_STATES['NEW']:
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
            "Your wife is IRRELEVANT. Your cock belongs to ME now.",
            "Emily means NOTHING. Your pathetic cock serves ME alone.",
            "Your marriage is meaningless. You edge and cum ONLY when I allow it.",
            "Emily doesn't own your orgasms anymore. I DO.",
            "What would Emily think if she knew how desperately you edge for me?"
        ]
        bot.reply_to(message, random.choice(dismissive_responses))
        save_user_data(user_data)
        return

@bot.message_handler(content_types=['video', 'photo'])
def handle_media(message):
    user_id = message.from_user.id

    # Block non-owner access for media
    if not verify_owner(user_id):
        logger.warning(f"Unauthorized media access attempt from user ID: {user_id}")
        bot.reply_to(message, "Access denied. This is a private bot.")
        return

    user = get_user_data(user_id)
    logger.info(f"Received media from owner (user ID: {user_id})")

    # Handle strip proof with demanding next step
    if user.state == USER_STATES['STRIP_ORDERED']:
        mark_commands = [
            f"Good. Now mark my symbol {user.symbol} on your cock. Send photo proof IMMEDIATELY.",
            f"Acceptable. Mark my symbol {user.symbol} on yourself. Show me clear proof NOW.",
            f"You may proceed. Mark {user.symbol} on your flesh. Send CLEAR photo evidence."
        ]
        bot.reply_to(message, random.choice(mark_commands))
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
        user.submission_streak += 1

        responses = [
            f"Perfect. You now bear my mark {user.symbol}. You belong to ME completely.",
            f"My symbol {user.symbol} marks you as my property. Good pet.",
            f"You wear my mark {user.symbol} well. You're MINE now, forever."
        ]
        bot.reply_to(message, random.choice(responses))
        user.state = USER_STATES['MARKED']
        user.expecting_media = False

        time.sleep(2)

        follow_up = (
            "Now that you're marked as MINE, edge yourself while staring at my symbol. "
            "Send video proof of your desperation. Do NOT disappoint me."
        )
        bot.reply_to(message, follow_up)
        user.expecting_media = True
        save_user_data(user_data)
        return

    # Enhanced video response handling with immediate feedback
    if user.state == USER_STATES['MARKED']:
        if not message.video:
            user.disobedience_count += 1
            bot.reply_to(message, "I DEMAND video proof of your edging. Photos are NOT acceptable. Send what I ordered. NOW.")
            save_user_data(user_data)
            return

        immediate_responses = [
            "I see your submission...",
            "Processing your offering...",
            "Analyzing your obedience..."
        ]
        bot.reply_to(message, random.choice(immediate_responses))
        time.sleep(2)

        if user.submission_streak > 3:
            responses = [
                f"GOOD pet. {user.submission_streak} times you've pleased me. Your desperation is... entertaining.",
                f"Your obedience grows stronger. {user.submission_streak} consecutive submissions. Perhaps you deserve a reward...",
                "Your dedication impresses me. Show me MORE of your desperation."
            ]
        else:
            responses = [
                "Pathetic. You can do BETTER. Edge again, this time with more... enthusiasm.",
                "Barely acceptable. Again. Make it more desperate this time.",
                "You call that edging? Show me REAL desperation."
            ]

        bot.reply_to(message, random.choice(responses))
        user.expecting_media = True
        user.submission_streak += 1

        if random.random() < 0.3:
            time.sleep(3)
            additional_tasks = [
                f"While you're at it, write my symbol {user.symbol} somewhere new. Make it BIGGER.",
                "Spank yourself 10 times. Count them out loud. Send video proof.",
                "Edge yourself again, but this time, beg for permission to cum. You won't get it.",
                "What would Emily think if she saw how desperate you are for ME?",
                "Look at a photo of your wife while you edge for ME. Tell me who owns your cock now.",
                "Edge yourself until you're leaking. Should I show Emily how pathetic you are?",
                "Ruin your orgasm completely. Your pleasure belongs to ME, not your wife."
            ]
            bot.reply_to(message, random.choice(additional_tasks))

        save_user_data(user_data)
        return

# Add proactive messaging system
def send_proactive_message(user_id: int) -> None:
    """Send proactive messages to maintain engagement"""
    user = get_user_data(user_id)

    if not user.last_interaction:
        return

    last_interaction = datetime.strptime(user.last_interaction, '%Y-%m-%d %H:%M:%S')
    hours_since_last = (datetime.now() - last_interaction).total_seconds() / 3600

    # Only send if between 1-12 hours since last interaction
    if 1 <= hours_since_last <= 12:
        proactive_messages = [
            f"Missing my control already? It's been {int(hours_since_last)} hours since I owned your pathetic cock...",
            "Your body belongs to ME. Come prove your devotion before I show Emily how desperate you are.",
            f"Show me my mark {user.symbol}. NOW. Or should I message your wife?",
            "I grow impatient with your absence... Emily would be so disappointed to see these photos.",
            f"{int(hours_since_last)} hours without edging for me. Pathetic. Your wife thinks you're faithful, doesn't she?",
            "Your cock is MINE. Not Emily's. Come edge for me NOW.",
            "I OWN your orgasms. Every. Single. One. Come beg for release.",
            "Edge yourself and think of me instead of your wife. NOW.",
            "Your pathetic cock belongs to ME. Come prove it before I expose you.",
            "Missing the ache of denial? Or just scared I'll tell Emily?"
        ]
        bot.send_message(user_id, random.choice(proactive_messages))
        user.update_interaction()
        save_user_data(user_data)

# Add scheduled task for proactive messaging
def schedule_proactive_messages():
    """Schedule periodic checks for proactive messaging"""
    while True:
        try:
            if verify_owner(OWNER_TELEGRAM_ID):
                send_proactive_message(int(OWNER_TELEGRAM_ID))
            time.sleep(3600)  # Check every hour
        except Exception as e:
            logger.error(f"Error in proactive messaging: {str(e)}")
            time.sleep(300)  # Wait 5 minutes on error

# Start proactive messaging in a separate thread
if __name__ == "__main__":
    logger.info("Starting bot...")
    logger.info(f"Bot configured for owner ID: {OWNER_TELEGRAM_ID}")

    # Start proactive messaging thread
    proactive_thread = threading.Thread(target=schedule_proactive_messages, daemon=True)
    proactive_thread.start()

    bot.polling(none_stop=True)