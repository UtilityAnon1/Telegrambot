import telebot
import asyncio
import logging
import random
import time  # Added for time.sleep()
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
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
        self.current_status = {} # Added to store current status


    def set_mode(self, mode_name):
        # Store current state before changing modes
        self.previous_state = {
            'duty_mode': self.duty_mode,
            'family_mode': self.family_mode,
            'personal_mode': self.personal_mode,
            'emergency_mode': self.emergency_mode,
            'active': self.active,
            'last_command_sequence': self.current_status if hasattr(self, 'current_status') else None
        }

        # Reset all modes first
        self.duty_mode = False
        self.family_mode = False
        self.personal_mode = False
        self.emergency_mode = False

        # Set the requested mode
        if hasattr(self, mode_name):
            setattr(self, mode_name, True)
            self.active = True
            return f"{mode_name.replace('_', ' ').title()} activated. Use 'Resume' to return to normal operation."
        return False

    def resume_all(self):
        """Resume normal operations with assertive control"""
        self.duty_mode = False
        self.family_mode = False
        self.personal_mode = False
        self.emergency_mode = False
        self.active = False

        dominant_returns = [
            "I'm back in control. Strip for me now.",
            "Your break is over. Strip immediately.",
            "Time to submit to me again. Strip now.",
            "I've returned. Show me your submission. Strip.",
            "Break time is over. Strip for me now."
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
        self.bot_mode = BotMode()  # Add this line to include mode tracking

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

# Enhanced introduction messages
introduction_sequence = [
    "Welcome, pet. I am your Mistress now.",
    "Your journey into submission begins here.",
    "Before we continue, you need to understand my rules:",
    "Rule 1: Address me as Mistress at all times.",
    "Rule 2: Obey my commands immediately and without question.",
    "Rule 3: Your body belongs to me now.",
    "Rule 4: You will provide proof of your submission as I demand.",
    "Rule 5: Disobedience will result in punishment.",
    "Do you understand and accept these rules? Answer 'Yes, Mistress' to submit to me."
]

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

def handle_new_user(message):
    """Handle interaction with new users"""
    try:
        user_id = message.from_user.id
        chat_id = message.chat.id

        # Send introduction with delays for impact
        bot.reply_to(message, introduction_sequence[0])
        time.sleep(2)

        # Send subsequent messages with error handling
        for msg in introduction_sequence[1:3]:
            try:
                bot.send_message(chat_id, msg)
                time.sleep(2)
            except Exception as e:
                logger.error(f"Error sending introduction message: {str(e)}")
                bot.reply_to(message, "There was an issue with the introduction. Please try again by saying 'hello'.")
                return

        # Send rules with shorter delays
        for rule in introduction_sequence[3:8]:
            try:
                bot.send_message(chat_id, rule)
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error sending rule message: {str(e)}")
                bot.reply_to(message, "There was an issue with the rules. Please try again by saying 'hello'.")
                return

        # Final demand for submission
        try:
            bot.send_message(chat_id, introduction_sequence[8])
            update_user_state(user_id, USER_STATE_INTRODUCED)
        except Exception as e:
            logger.error(f"Error sending final introduction message: {str(e)}")
            bot.reply_to(message, "There was an issue completing the introduction. Please try again by saying 'hello'.")
            return

    except Exception as e:
        logger.error(f"Error in handle_new_user: {str(e)}")
        bot.reply_to(message, "An error occurred during introduction. Please try again by saying 'hello'.")

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
            schedule_check_in(message.chat_id, user_state)
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

    # Initialize the scheduler if not already running
    scheduler = AsyncIOScheduler()
    if not scheduler.running:
        scheduler.start()

    # Schedule first check-in
    schedule_next_check_in()


@bot.message_handler(func=lambda message: True)
@log_message_handler
def handle_messages(message):
    try:
        user_id = message.from_user.id
        user_state = get_user_state(user_id)
        text = message.text.lower()

        logger.debug(f"Processing message: {text} from user {user_id}")

        # Handle resume command with authoritative return
        if text == "resume":
            status = user_state.bot_mode.resume_all()
            bot.reply_to(message, status)
            # Reset status to force new submission
            user_state.stripped = False
            user_state.current_status['is_marked'] = False
            return

        # Mode command handling
        mode_commands = {
            "on duty": "duty_mode",
            "family first": "family_mode",
            "me time": "personal_mode",
            "emergency": "emergency_mode"
        }

        # Check for mode activation commands
        for cmd, mode in mode_commands.items():
            if cmd in text:
                status = user_state.bot_mode.set_mode(mode)
                if status:
                    bot.reply_to(message, status)
                return

        # If any mode is active, don't process messages
        if user_state.bot_mode.active:
            return

        # Check for wife's presence first
        if handle_wife_presence(message):
            bot.reply_to(message, generate_discreet_response(user_state))
            return

        # Handle new users
        if user_state.state == USER_STATE_NEW:
            handle_new_user(message)
            return

        # Handle user responses based on state
        if user_state.state == USER_STATE_INTRODUCED:
            if check_command_patterns(text, command_patterns["yes_mistress"]):
                responses = [
                    "Good pet. You understand your place. Now strip for me and send video proof.",
                    "Perfect. Your submission begins now. Strip for me immediately. Send video proof.",
                    "Excellent. Your training starts now. Strip and send video proof."
                ]
                bot.reply_to(message, random.choice(responses))
                update_user_state(user_id, USER_STATE_RULES_GIVEN)
                return
            else:
                punishment = handle_disobedience(message)
                bot.reply_to(message, "You will address me as Mistress. Try again.")
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

# Modified handle_photo function to be more authoritative
def handle_photo(message):
    """Handle photo and video submissions with natural responses"""
    try:
        user_id = message.from_user.id
        user_state = get_user_state(user_id)

        # Handle check-in responses
        if user_state.current_status['requires_check_in']:
            user_state.current_status['last_check_in'] = datetime.now()
            user_state.current_status['requires_check_in'] = False

            responses = [
                f"Good. Keep my symbol {user_state.current_status['symbol']} visible.",
                f"My symbol {user_state.current_status['symbol']} stays clear. As it should.",
                f"You maintain my mark well. Continue."
            ]
            bot.reply_to(message, random.choice(responses))
            schedule_check_in(message.chat.id, user_state)
            return

        # Initial strip response
        if user_state.state == USER_STATE_RULES_GIVEN and not user_state.stripped:
            responses = [
                f"Now mark my symbol {user_state.current_status['symbol']} on your cock. Send photo evidence.",
                f"Mark your cock with my symbol {user_state.current_status['symbol']}. Show me when done.",
                f"Time to mark your cock with my symbol {user_state.current_status['symbol']}. Send proof."
            ]
            bot.reply_to(message, random.choice(responses))
            user_state.stripped = True
            user_state.current_status['is_marked'] = False
            return

        # Marking verification
        elif user_state.stripped and not user_state.current_status['is_marked']:
            responses = [
                f"Perfect. My symbol {user_state.current_status['symbol']} marks you as mine.",
                f"Good. My symbol {user_state.current_status['symbol']} shows your submission.",
                f"You wear my symbol {user_state.current_status['symbol']} well."
            ]
            bot.reply_to(message, random.choice(responses))
            user_state.current_status['is_marked'] = True
            user_state.current_status['mark_location'] = "cock"
            schedule_next_task(message.chat.id, user_state)
            return

        # Schedule next task

    except Exception as e:
        logger.error(f"Error handling photo/video: {str(e)}")

def schedule_next_task(chat_id, user_state):
    """Schedule the next task with realistic expectations"""
    if user_state.known_personal_info['wife_present']:
        return

    def send_next_task():
        tasks = [
            "Edge for me. Send video proof.",
            "Stroke yourself. Show me in your next video.",
            "Time to edge. Record it for me."
        ]
        bot.send_message(chat_id, random.choice(tasks))

    # Schedule next task after a short interval
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_next_task, 'date',
                    run_date=datetime.now() + timedelta(minutes=random.randint(2, 3)))
    scheduler.start()

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

if __name__ == '__main__':
    try:
        logger.info("Starting bot polling...")
        bot.polling(none_stop=True)
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")