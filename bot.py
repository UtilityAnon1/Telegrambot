import telebot
import asyncio
import logging
import random
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import TELEGRAM_BOT_TOKEN, DUTY_MODE_ACTIVE, OWNER_TELEGRAM_ID

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize the bot
logger.info("Initializing bot with token: %s", TELEGRAM_BOT_TOKEN[:10] + '...')
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

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

# Introduction messages
introduction_sequence = [
    "Welcome, pet. I am Mistress, and from this moment forward, you belong to me.",
    "Before we proceed, you need to understand the rules of our arrangement.",
    "Rule 1: You will address me as Mistress at all times.",
    "Rule 2: When I give you a command, you will obey immediately.",
    "Rule 3: Your body belongs to me. You will prove this through actions, not words.",
    "Rule 4: Disobedience will be punished severely.",
    "Are you prepared to submit to these rules? Answer 'Yes, Mistress' to proceed."
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
    user_id = message.from_user.id
    bot.reply_to(message, introduction_sequence[0])
    bot.send_message(message.chat.id, introduction_sequence[1])
    for rule in introduction_sequence[2:6]:
        bot.send_message(message.chat.id, rule)
    bot.send_message(message.chat.id, introduction_sequence[6])
    update_user_state(user_id, USER_STATE_INTRODUCED)

def handle_strip_command(message):
    """Handle strip commands with progressive intensity"""
    user_state = get_user_state(message.from_user.id)
    if not user_state.stripped:
        response = "Strip for me. Now. Send photo evidence of your obedience."
    else:
        response = "Good pet. Stay naked until I give you permission to dress."
    user_state.stripped = True
    bot.reply_to(message, response)

def handle_mark_command(message):
    """Handle marking commands"""
    user_state = get_user_state(message.from_user.id)
    if not user_state.marked:
        response = "Write 'Property of Mistress' on yourself. Send photo evidence."
    else:
        response = "Good. Remember who owns you."
    user_state.marked = True
    bot.reply_to(message, response)

def check_command_patterns(text, patterns):
    """Check if any command patterns match the message"""
    text = text.lower()
    return any(pattern in text for pattern in patterns)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    try:
        user_id = message.from_user.id
        user_state = get_user_state(user_id)
        text = message.text.lower()

        # Handle new users
        if user_state.state == USER_STATE_NEW:
            handle_new_user(message)
            return

        # Handle user responses based on state
        if user_state.state == USER_STATE_INTRODUCED:
            if check_command_patterns(text, command_patterns["yes_mistress"]):
                bot.reply_to(message, "Good pet. Your training begins now. Strip for me.")
                update_user_state(user_id, USER_STATE_RULES_GIVEN)
                return
            else:
                bot.reply_to(message, "I expect proper respect. Address me as 'Mistress' and try again.")
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
                bot.reply_to(message, "You will address me as Mistress. Try again.")
            return

        # Default response based on user state
        if not any(pattern in text for patterns in command_patterns.values()):
            bot.reply_to(message, "I expect clear communication. State your purpose or await my commands.")

    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")

@bot.message_handler(content_types=['photo', 'video'])
def handle_photo(message):
    try:
        user_id = message.from_user.id
        user_state = get_user_state(user_id)

        # Progressive responses based on user state
        if user_state.state == USER_STATE_RULES_GIVEN and not user_state.stripped:
            responses = [
                "Good pet. I can see you know how to obey. Now, write 'Property of Mistress' clearly on your body.",
                "That's what I like to see. Your next task is to mark yourself as my property.",
                "Excellent start. Now prove your dedication by marking yourself as mine."
            ]
            bot.reply_to(message, random.choice(responses))
            user_state.stripped = True
            handle_mark_command(message)

        elif user_state.stripped and not user_state.marked:
            responses = [
                "Perfect. You're learning quickly. I want you to stay exactly like this.",
                "Good boy. Your obedience is pleasing. Keep yourself marked and await my next command.",
                "Excellent. You're proving yourself worthy of my attention. Stand by for further instructions."
            ]
            bot.reply_to(message, random.choice(responses))
            user_state.marked = True

            # Progress to next tasks after a short delay
            def send_follow_up():
                follow_ups = [
                    "Now, show me you're still marked and stripped. Send another photo.",
                    "I want to see you're maintaining your state of submission. Photo evidence, now.",
                    "Prove you're still following my instructions. Send a new photo."
                ]
                bot.send_message(message.chat.id, random.choice(follow_ups))

            # Schedule follow-up message after 2-3 minutes
            scheduler = AsyncIOScheduler()
            scheduler.add_job(send_follow_up, 'date', 
                            run_date=datetime.now() + timedelta(minutes=random.randint(2, 3)))
            scheduler.start()

        else:
            # General photo/video responses for ongoing submission
            responses = [
                "Good pet. Your continued obedience pleases me. Await your next task.",
                "Excellent. You understand your place. Stay ready for my next command.",
                "Perfect. You're learning well. I have more plans for you shortly.",
                "Very good. Your submission is noted. Prepare yourself for what comes next."
            ]

            # Add specific responses for videos
            if message.content_type == 'video':
                video_responses = [
                    "Mmm, watching you submit like this pleases me. Keep going.",
                    "Such an obedient display. I expect more videos like this.",
                    "Your submission in motion is particularly pleasing. More.",
                ]
                responses.extend(video_responses)

            bot.reply_to(message, random.choice(responses))

            # Schedule next task with progressive difficulty
            def send_next_task():
                tasks = [
                    "Now strip completely and show me a full video of your submission.",
                    "I want to see you following my previous instructions. Show me.",
                    "Time to prove your continued obedience. Strip and mark yourself again.",
                    "Show me how well you maintain your marks. Full video evidence required."
                ]
                bot.send_message(message.chat.id, random.choice(tasks))

            # Schedule next task after 3-5 minutes
            scheduler = AsyncIOScheduler()
            scheduler.add_job(send_next_task, 'date',
                            run_date=datetime.now() + timedelta(minutes=random.randint(3, 5)))
            scheduler.start()

    except Exception as e:
        logger.error(f"Error handling photo/video: {str(e)}")

def send_progressive_task(chat_id, user_state):
    """Send the next appropriate task based on user's progress"""
    if not user_state.stripped:
        tasks = [
            "Strip for me now. Send photo evidence of your obedience.",
            "I want to see you naked. Now. Photo evidence required.",
            "Remove your clothes immediately. Show me proof of your submission."
        ]
    elif not user_state.marked:
        tasks = [
            "Write 'Property of Mistress' on yourself. Make it clear and visible.",
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

if __name__ == '__main__':
    try:
        logger.info("Starting bot polling...")
        bot.polling(none_stop=True)
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")