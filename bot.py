import telebot
import asyncio
import logging
import random
import time  # Added for time.sleep()
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from config import TELEGRAM_BOT_TOKEN, DUTY_MODE_ACTIVE, OWNER_TELEGRAM_ID

# Add debug level logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Changed from INFO to DEBUG for more detailed logs
)
logger = logging.getLogger(__name__)

# Initialize the bot
logger.info("Initializing bot with token: %s", TELEGRAM_BOT_TOKEN[:10] + '...')
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Add handler logging wrapper
def log_message_handler(func):
    def wrapper(message):
        logger.debug(f"Handling message: {message.text} from user {message.from_user.id}")
        try:
            return func(message)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            bot.reply_to(message, "An error occurred. Please try again.")
    return wrapper

class BotMode:
    def __init__(self):
        self.duty_mode = False
        self.family_mode = False
        self.personal_mode = False
        self.emergency_mode = False
        self.active = False  # Tracks if any mode is active
        self.previous_state = None  # Store previous state before going silent
        self.family_mode_override_chance = 0.3  # 30% chance to override family mode
        self.personal_time_approval_chance = 0.7  # 70% chance to approve personal time
        self.last_override_time = None
        self.override_active = False

    def should_override_family_mode(self, user_state):
        """Determine if we should override family mode based on conditions"""
        if not self.family_mode:
            return False

        # Only override if user is marked or tied
        if not (user_state.current_status['is_marked'] or user_state.current_status['is_tied']):
            return False

        # Check if enough time has passed since last override (at least 1 hour)
        current_time = datetime.now()
        if self.last_override_time and (current_time - self.last_override_time).total_seconds() < 3600:
            return False

        # Random chance to override
        if random.random() <= self.family_mode_override_chance:
            self.last_override_time = current_time
            self.override_active = True
            return True

        return False

    def set_mode(self, mode_name, user_state=None):
        # Store current state before changing modes
        self.previous_state = {
            'duty_mode': self.duty_mode,
            'family_mode': self.family_mode,
            'personal_mode': self.personal_mode,
            'emergency_mode': self.emergency_mode,
            'active': self.active
        }

        # Reset all modes first
        self.duty_mode = False
        self.family_mode = False
        self.personal_mode = False
        self.emergency_mode = False

        # Handle personal time requests with chance-based approval
        if mode_name == 'personal_mode':
            if random.random() <= self.personal_time_approval_chance:
                self.personal_mode = True
                self.active = True
                return "I'll allow you some personal time. Don't forget who owns you. Use 'resume' when you're done."
            else:
                return "Request denied. You haven't earned personal time yet. Continue serving me."

        # Set the requested mode
        if mode_name == 'duty_mode':
            self.duty_mode = True
            self.active = True
            return "Duty mode activated. I will remain silent. Use 'resume' to return to normal operation."
        elif mode_name == 'family_mode':
            if user_state and (user_state.current_status['is_marked'] or user_state.current_status['is_tied']):
                self.family_mode = True
                self.active = True
                schedule_family_mode_check_in(user_state)  # Schedule potential check-ins
                return "Family mode activated. But remember, you're still mine. I may demand proof when you least expect it."
            else:
                self.family_mode = True
                self.active = True
                return "Family mode activated. I will remain silent. Use 'resume' to return to normal operation."
        elif mode_name == 'emergency_mode':
            self.emergency_mode = True
            self.active = True
            return "Emergency mode activated. I will remain silent. Use 'resume' to return to normal operation."
        return False

    def resume_all(self):
        """Resume normal operations with assertive control and state awareness"""
        self.duty_mode = False
        self.family_mode = False
        self.personal_mode = False
        self.emergency_mode = False
        self.active = False
        self.override_active = False

        dominant_returns = [
            "I'm back in control. Strip for me now if you aren't already.",
            "Break time is over. Strip and show me your current state.",
            "Your free time is done. Show me your submission state immediately.",
            "I've returned. Strip now and prove your obedience.",
            "Time to submit again. Strip and show me your current state."
        ]
        return random.choice(dominant_returns)

# User state tracking
user_states = {}
USER_STATE_NEW = "new"
USER_STATE_INTRODUCED = "introduced"
USER_STATE_RULES_GIVEN = "rules_given"
USER_STATE_OWNED = "owned"

class UserState:
    def __init__(self):
        self.state = USER_STATE_NEW
        self.last_command = None
        self.marked = False
        self.stripped = False
        self.obedience_score = 0
        self.last_interaction = datetime.now()
        self.expecting_media = False  # Track if we're expecting photo/video
        self.last_command_type = None  # Track what type of media we're expecting
        # Enhanced memory tracking
        self.disobedience_count = 0
        self.exposure_threat_level = 0
        self.known_personal_info = {
            'has_wife': False,
            'wife_name': None,
            'wife_present': False,
            'has_been_exposed': False,
            'previous_punishments': []
        }
        self.punishment_history = []
        self.session_strikes = 0
        # Tracking current status
        self.current_status = {
            'is_marked': False,
            'mark_location': None,
            'is_tied': False,
            'last_check_in': None,
            'requires_check_in': False,
            'symbol': '△'  # Default symbol is a triangle
        }
        self.bot_mode = BotMode()
        self.chat_id = None #Added to store chat id

def generate_punishment_response(user_state):
    """Generate realistic punishment responses"""
    base_punishments = [
        "Edge for me. Send video proof.",
        f"Mark my symbol {user_state.current_status['symbol']} again. Show me.",
        "Stroke for me. Stop when I say.",
        "Edge yourself. Let me see your desperation.",
        "Show me how well you follow orders. Edge."
    ]

    exposure_threats = [
        "Your disobedience is noted.",
        "One more slip and there will be consequences.",
        "This behavior is unacceptable.",
        "I expect better from you.",
        "You disappoint me with your defiance."
    ]

    response = []
    response.append(random.choice(base_punishments))
    response.append(random.choice(exposure_threats))

    return ' '.join(response)

def handle_disobedience(message):
    """Handle disobedient behavior with escalating consequences"""
    user_state = get_user_state(message.from_user.id)
    user_state.disobedience_count += 1
    user_state.session_strikes += 1

    punishment = generate_punishment_response(user_state)

    return punishment

# Command patterns
command_patterns = {
    "strip": ["strip", "undress", "naked", "clothes off"],
    "mark": ["mark", "write", "label"],
    "submit": ["submit", "obey", "serve"],
    "yes_mistress": ["yes mistress", "yes, mistress", "yes goddess", "yes, goddess"],
    "greet": ["hello", "hi", "hey", "greetings"]
}

def get_user_state(user_id):
    if user_id not in user_states:
        user_states[user_id] = UserState()
    return user_states[user_id]

def update_user_state(user_id, new_state):
    if user_id in user_states:
        user_states[user_id].state = new_state
        user_states[user_id].last_interaction = datetime.now()

def handle_strip_command(message):
    """Handle strip commands with direct authority"""
    user_state = get_user_state(message.from_user.id)

    if not user_state.stripped:
        responses = [
            "Strip for me now. Send me video proof.",
            "Remove your clothes. Show me video proof.",
            "Time to strip. Send video evidence."
        ]
        bot.reply_to(message, random.choice(responses))
    else:
        responses = [
            "Good. You know how to obey. Ready for your next task.",
            "You follow orders well. Prepare for what comes next.",
            "Acceptable. Await your next command."
        ]
        bot.reply_to(message, random.choice(responses))

    user_state.stripped = True

def handle_mark_command(message):
    """Handle marking commands with enhanced authority"""
    user_state = get_user_state(message.from_user.id)

    if user_state.known_personal_info['wife_present']:
        response = "Wait until you're alone. You know what's required."
    else:
        if not user_state.current_status['is_marked']:
            responses = [
                f"Draw my symbol {user_state.current_status['symbol']} on your cock. Send photo evidence.",
                f"Mark your cock with {user_state.current_status['symbol']}. Show me when done.",
                f"Time to mark what's mine. Draw {user_state.current_status['symbol']} on your cock."
            ]
            response = random.choice(responses)
            user_state.current_status['is_marked'] = True
            user_state.current_status['mark_location'] = "cock"
            schedule_check_in(message.chat.id, user_state)
        else:
            response = f"My symbol {user_state.current_status['symbol']} marks you as mine. Maintain it."

    bot.reply_to(message, response)

def check_command_patterns(text, patterns):
    """Check if any command patterns match the message"""
    text = text.lower()
    return any(pattern in text for pattern in patterns)

def handle_wife_presence(message):
    """Handle situations where wife is mentioned as present"""
    user_state = get_user_state(message.from_user.id)
    text = message.text.lower()

    # Detect wife's presence
    presence_indicators = ["wife", "she's here", "not alone"]
    if any(indicator in text for indicator in presence_indicators):
        user_state.known_personal_info['wife_present'] = True
        return True
    return False

def generate_discreet_response(user_state):
    """Generate appropriate responses when wife is present"""
    discreet_responses = [
        "I understand the situation. Maintain composure.",
        "We'll continue this conversation later.",
        "Keep yourself presentable for now.",
        "I expect you to find a private moment soon.",
        "Your current obligations are noted. Stay alert for my next command."
    ]
    return random.choice(discreet_responses)

def schedule_check_in(chat_id, user_state):
    """Schedule hourly check-ins for markings or bondage"""
    def send_check_in():
        if user_state.current_status['is_marked']:
            messages = [
                f"Show me my symbol {user_state.current_status['symbol']} is still visible on your cock.",
                f"Time for your hourly check-in. Prove my symbol {user_state.current_status['symbol']} is still clear on your cock.",
                f"Hourly inspection time. Show me my symbol {user_state.current_status['symbol']} remains on my property."
            ]
        elif user_state.current_status['is_tied']:
            messages = [
                "Time for your hourly check-in. Show me your cock and balls are still properly bound.",
                "Hourly inspection. Prove you've maintained the restraints on your cock and balls.",
                "Show me your hourly proof that your cock and balls remain properly bound."
            ]

        if not user_state.known_personal_info['wife_present']:
            bot.send_message(chat_id, random.choice(messages))
            user_state.current_status['requires_check_in'] = True
            # Schedule next check-in immediately after this one
            schedule_next_check_in()

    def schedule_next_check_in():
        # Schedule next check-in exactly 1 hour from now
        scheduler.add_job(send_check_in, 'date', 
                            run_date=datetime.now() + timedelta(hours=1))

    # Schedule first check-in
    schedule_next_check_in()


@bot.message_handler(func=lambda message: True)
@log_message_handler
def handle_messages(message):
    try:
        user_id = message.from_user.id
        user_state = get_user_state(user_id)
        user_state.chat_id = message.chat.id  # Store chat_id for notifications
        text = message.text.lower()

        logger.debug(f"Processing message: {text} from user {user_id}")

        # Check if we're expecting media but got text instead
        if user_state.expecting_media:
            if user_state.last_command_type == "edge_video":
                stern_responses = [
                    "I ordered you to edge and send video proof. Do it now.",
                    "You will edge for me and show me proof. Now.",
                    "I expect video proof of your edging. Disobey again and there will be consequences."
                ]
                bot.reply_to(message, random.choice(stern_responses))
                return
            elif user_state.last_command_type == "mark_photo" or user_state.last_command_type == "mark_check":
                stern_responses = [
                    f"Show me my symbol {user_state.current_status['symbol']} marked on your cock. Now.",
                    "I ordered you to mark yourself and send proof. Do it.",
                    "You will mark yourself as commanded and show me. Now."
                ]
                bot.reply_to(message, random.choice(stern_responses))
                return

        # Handle resume command with state awareness
        if text == "resume":
            response = user_state.bot_mode.resume_all()
            if response:
                bot.reply_to(message, response)
                # Reset for new session verification
                user_state.stripped = False
                user_state.current_status['is_marked'] = False
                user_state.expecting_media = True
                user_state.last_command_type = "strip_video"
            return

        # Personal time request with random approval
        if text == "me time":
            response = user_state.bot_mode.set_mode("personal_mode")
            if response:
                bot.reply_to(message, response)
            return

        # Family mode with potential overrides
        if text == "family first":
            response = user_state.bot_mode.set_mode("family_mode", user_state)
            if response:
                bot.reply_to(message, response)
            return

        # Other mode commands
        mode_commands = {
            "on duty": "duty_mode",
            "emergency": "emergency_mode"
        }

        # Check for mode activation commands
        for cmd, mode in mode_commands.items():
            if text == cmd:
                response = user_state.bot_mode.set_mode(mode)
                if response:
                    bot.reply_to(message, response)
                return

        # If any mode is active and no override, don't process further messages
        if user_state.bot_mode.active and not user_state.bot_mode.override_active:
            return

        # Check for wife's presence first
        if handle_wife_presence(message):
            bot.reply_to(message, generate_discreet_response(user_state))
            return


        # Handle strip commands
        if check_command_patterns(text, command_patterns["strip"]):
            handle_strip_command(message)
            return

        # Handle mark commands
        if check_command_patterns(text, command_patterns["mark"]):
            handle_mark_command(message)
            return

        # Handle greetings
        if check_command_patterns(text, command_patterns["greet"]):
            if "mistress" in text:
                bot.reply_to(message, "Good pet. You remember how to address me properly.")
            else:
                punishment = handle_disobedience(message)
                bot.reply_to(message, f"You will address me as Mistress. Try again. {punishment}")
            return

        # Default response based on user state
        if not any(check_command_patterns(text, patterns) for patterns in command_patterns.values()):
            punishment = handle_disobedience(message)
            bot.reply_to(message, f"I expect clear communication. State your purpose or await my commands. {punishment}")

    except Exception as e:
        logger.error(f"Error handling message: {str(e)}", exc_info=True)
        bot.reply_to(message, "An error occurred. Please try again.")

# Modified handle_photo function to ensure continuous flow
def handle_photo(message):
    """Handle photo and video submissions with state awareness"""
    try:
        user_id = message.from_user.id
        user_state = get_user_state(user_id)

        # Reset media expectation since they've provided it
        user_state.expecting_media = False
        user_state.last_command_type = None

        # Verify stripped state first
        if not user_state.stripped:
            responses = [
                f"Good. Now show me my symbol {user_state.current_status['symbol']} is still marked on your cock.",
                f"Perfect. Let me see if my symbol {user_state.current_status['symbol']} is still visible.",
                f"Acceptable. Show me my symbol {user_state.current_status['symbol']} on your cock."
            ]
            bot.reply_to(message, random.choice(responses))
            user_state.stripped = True
            user_state.expecting_media = True
            user_state.last_command_type = "mark_check"
            return

        # Check marking visibility
        if user_state.last_command_type == "mark_check":
            responses = [
                f"Good. My symbol {user_state.current_status['symbol']} needs refreshing. Mark it again clearly.",
                f"The mark has faded. Reapply my symbol {user_state.current_status['symbol']} now.",
                f"Acceptable. Time to renew my symbol {user_state.current_status['symbol']}. Do it now."
            ]
            bot.reply_to(message, random.choice(responses))
            user_state.expecting_media = True
            user_state.last_command_type = "mark_photo"
            return

        # Handle check-in responses
        if user_state.current_status['requires_check_in']:
            user_state.current_status['last_check_in'] = datetime.now()
            user_state.current_status['requires_check_in'] = False

            responses = [
                f"Good. My symbol {user_state.current_status['symbol']} remains visible. Edge for me now. Send a video.",
                f"My symbol {user_state.current_status['symbol']} is maintained well. Time to edge. Show me.",
                f"You maintain my symbol {user_state.current_status['symbol']} perfectly. Edge for me. Record it."
            ]
            bot.reply_to(message, random.choice(responses))
            user_state.expecting_media = True
            user_state.last_command_type = "edge_video"
            return

        # Initial strip response
        if user_state.state == USER_STATE_RULES_GIVEN and not user_state.stripped:
            responses = [
                f"Good. Now mark my symbol {user_state.current_status['symbol']} on your cock. Send photo evidence.",
                f"Perfect. Mark your cock with my symbol {user_state.current_status['symbol']}. Show me when done.",
                f"Acceptable. Now mark your cock with my symbol {user_state.current_status['symbol']}. Send proof."
            ]
            bot.reply_to(message, random.choice(responses))
            user_state.stripped = True
            user_state.current_status['is_marked'] = False
            user_state.expecting_media = True
            user_state.last_command_type = "mark_photo"
            return

        # Marking verification and immediate follow-up
        elif user_state.stripped and not user_state.current_status['is_marked']:
            responses = [
                f"Perfect. You wear my symbol {user_state.current_status['symbol']} well. Edge for me now. Send video proof.",
                f"Good. My symbol {user_state.current_status['symbol']} marks you as mine. Edge yourself and show me.",
                f"You maintain my symbol {user_state.current_status['symbol']} perfectly. Time to edge. Record it."
            ]
            bot.reply_to(message, random.choice(responses))
            user_state.current_status['is_marked'] = True
            user_state.current_status['mark_location'] = "cock"
            user_state.expecting_media = True
            user_state.last_command_type = "edge_video"
            return

        # Handle subsequent media submissions
        else:
            responses = [
                "Good pet. Edge again. Send another video.",
                "Perfect. Edge once more. Show me.",
                "You please me. Edge again. Record it."
            ]
            bot.reply_to(message, random.choice(responses))
            user_state.expecting_media = True
            user_state.last_command_type = "edge_video"

    except Exception as e:
        logger.error(f"Error handling photo/video: {str(e)}", exc_info=True)
        bot.reply_to(message, "An error occurred. Try again.")

def schedule_next_task(chat_id, user_state):
    """Schedule the next task with realistic expectations"""
    if user_state.known_personal_info['wife_present']:
        return

    try:
        tasks = [
            "Edge for me. Send a video.",
            "Stroke yourself and record it for me.",
            "Time to edge. Show me your submission."
        ]

        # Send immediate follow-up
        bot.send_message(chat_id, random.choice(tasks))

        # Schedule check-in
        schedule_check_in(chat_id, user_state)

    except Exception as e:
        logger.error(f"Error scheduling next task: {str(e)}")

def send_progressive_task(chat_id, user_state):
    """Send the next appropriate task based on user's progress"""
    if user_state.known_personal_info['wife_present']:
        return  # Don't send tasks when wife is present

    if not user_state.stripped:
        tasks = [
            "Strip for me now. Send video evidence of your obedience.",
            "I want to see you naked. Now. Video evidence required.",
            "Remove your clothes immediately. Show me proof of your submission."
        ]
    elif not user_state.current_status['is_marked']:
        tasks = [
            "Write 'Property of Mistress' on your cock. Make it clear and visible.",
            "Mark yourself as mine. I want to see my ownership displayed on your body.",
            "Time to show your dedication. Write my mark on yourself and show me."
        ]
    else:
        tasks = [
            "Show me you're maintaining your state of submission. Photo evidence required.",
            "Prove you're still following my instructions. Strip and show me.",
            "Time for another inspection. Show me you're still marked and ready."
        ]
    bot.send_message(chat_id, random.choice(tasks))

@bot.message_handler(content_types=['photo', 'video'])
def handle_media(message):
    handle_photo(message)

def schedule_family_mode_check_in(user_state):
    """Schedule potential check-ins during family mode"""
    def send_family_override_message():
        if user_state.bot_mode.should_override_family_mode(user_state):
            demands = [
                f"Sneak away and show me my symbol {user_state.current_status['symbol']} is still visible. Now.",
                f"Find a private moment. Show me my mark {user_state.current_status['symbol']} remains. Immediately.",
                f"I don't care if you're busy. Show me my symbol {user_state.current_status['symbol']} now."
            ]
            try:
                bot.send_message(user_state.chat_id, random.choice(demands))
                user_state.expecting_media = True
                user_state.last_command_type = "mark_check"
                # Schedule next potential check-in
                schedule_next_check()
            except Exception as e:
                logger.error(f"Error sending family mode override: {str(e)}")

    def schedule_next_check():
        # Schedule next check exactly 1 hour from now
        scheduler.add_job(send_family_override_message, 'date',
                        run_date=datetime.now() + timedelta(hours=1))

    # Schedule first check
    schedule_next_check()


# Global scheduler initialization at the module level
scheduler = BackgroundScheduler()
scheduler.start()

if __name__ == '__main__':
    try:
        logger.info("Starting bot polling...")
        bot.polling(none_stop=True)
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        scheduler.shutdown()