import telebot
import asyncio
import logging
import random
import time  # Added for time.sleep()
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import TELEGRAM_BOT_TOKEN, DUTY_MODE_ACTIVE, OWNER_TELEGRAM_ID

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Add these near the top of the file, after the existing imports and before the bot initialization
class BotMode:
    def __init__(self):
        self.duty_mode = False
        self.family_mode = False
        self.personal_mode = False
        self.emergency_mode = False
        self.active = False  # Tracks if any mode is active

    def set_mode(self, mode_name):
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
        """Resume normal operations by clearing all modes"""
        self.duty_mode = False
        self.family_mode = False
        self.personal_mode = False
        self.emergency_mode = False
        self.active = False
        return "All modes cleared. Resuming normal operations."

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
    """Generate escalating punishment responses based on user history and context"""
    base_punishments = [
        "Edge yourself {edge_count} times. Each edge must last at least 2 minutes.",
        "Write 'Property of Mistress' on your cock. Make it clear and visible.",
        "Force {orgasm_count} ruined orgasms. No pleasure allowed.",
        "Edge for {edge_duration} minutes straight. No breaks.",
        "Perform {task_count} forced orgasms in succession. No rest between."
    ]

    exposure_threats = [
        "Your wife would be interested to see these photos, wouldn't she?",
        "One click and your wife sees everything. Remember that.",
        "I wonder what your wife would think of these marks?",
        "These photos could reach your wife so easily. Don't test me.",
        "Should we show your wife how pathetic you look right now?",
        "I'm getting closer to sending these to your wife with each disobedience.",
        "Your wife deserves to know what a submissive pet you've become.",
        "Keep testing me, and your wife will receive quite an interesting email."
    ]

    intense_punishments = [
        "Edge yourself until you're begging. Then edge 5 more times.",
        "Each photo will be one step closer to your wife's inbox.",
        "Time for a ruined orgasm. Edge 10 times, then ruin it completely.",
        "Your wife will love seeing how pathetic you are.",
        "Force {forced_count} orgasms in a row. Each one more painful than the last.",
        "Edge constantly for the next hour. Send video proof every 10 minutes.",
        "You'll edge 20 times, then beg me for a ruined orgasm.",
        "Time to break you completely. Edge until you're crying.",
        "Your cock is mine to torture. Edge until you can't think straight."
    ]

    # If wife is present, only use very discreet punishments
    if user_state.known_personal_info['wife_present']:
        discreet_punishments = [
            "Find a private moment later. You know what's expected.",
            "Your punishment awaits when you're alone.",
            "We'll address this disobedience when you have privacy.",
            "Remember your place. We'll continue this later."
        ]
        return random.choice(discreet_punishments)

    # Calculate punishment intensity based on history
    intensity = min(user_state.disobedience_count + user_state.session_strikes, 10)
    edge_count = intensity + 2
    spank_count = intensity * 5
    write_count = intensity * 2
    orgasm_count = min(intensity, 5)
    edge_duration = intensity * 5
    task_count = min(intensity, 3)
    forced_count = min(intensity, 4)

    response = []

    # Add base punishment
    base = random.choice(base_punishments).format(
        edge_count=edge_count,
        spank_count=spank_count,
        write_count=write_count,
        orgasm_count=orgasm_count,
        edge_duration=edge_duration,
        task_count=task_count,
        forced_count=forced_count
    )
    response.append(base)

    # Add exposure threats if wife is known
    if user_state.known_personal_info['has_wife']:
        if user_state.exposure_threat_level > 3:
            response.append(random.choice(intense_punishments).format(
                forced_count=forced_count
            ))
            if user_state.exposure_threat_level > 5:
                response.append("Your disobedience is pushing me closer to exposing you completely.")
        else:
            response.append(random.choice(exposure_threats))
            user_state.exposure_threat_level += 1

    # Track punishment history with more detail
    user_state.punishment_history.append({
        'timestamp': datetime.now(),
        'intensity': intensity,
        'punishment': ' '.join(response),
        'exposure_level': user_state.exposure_threat_level,
        'total_disobedience': user_state.disobedience_count
    })

    return ' '.join(response)

def handle_disobedience(message):
    """Handle disobedient behavior with escalating consequences"""
    user_state = get_user_state(message.from_user.id)
    user_state.disobedience_count += 1
    user_state.session_strikes += 1

    punishment = generate_punishment_response(user_state)

    # Enhanced wife-related responses
    if "wife" in message.text.lower():
        if not user_state.known_personal_info['has_wife']:
            user_state.known_personal_info['has_wife'] = True
            punishment = f"Interesting... you have a wife? That information will be very useful. {punishment}"
        else:
            wife_mentions = [
                "Mentioning your wife again? You must want her to know about this.",
                "Your wife keeps coming up... Perhaps you're hoping I'll tell her?",
                "You can't stop thinking about what your wife would say, can you?",
                "Every time you mention your wife, you risk exposure even more."
            ]
            punishment = f"{random.choice(wife_mentions)} {punishment}"

    return punishment

# Enhanced introduction messages
introduction_sequence = [
    "Welcome to your new reality, pet. I am Mistress, and from this moment forward, your body, mind, and soul belong to me.",
    "Your old life ends here. Under my ownership, you will learn true submission.",
    "Before we proceed, you need to understand the rules of our arrangement:",
    "Rule 1: You will address me as Mistress at all times. Every message must show your respect.",
    "Rule 2: When I give you a command, you will obey immediately and without question.",
    "Rule 3: Your body belongs to me. You will prove this through actions, not words.",
    "Rule 4: You will document your submission with photos and videos as I demand.",
    "Rule 5: Disobedience will result in severe punishment.",
    "Are you prepared to submit to these rules and accept your place as my property? Answer 'Yes, Mistress' to proceed."
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

    # Send introduction with delays for impact
    bot.reply_to(message, introduction_sequence[0])
    time.sleep(2)
    bot.send_message(message.chat.id, introduction_sequence[1])
    time.sleep(2)
    bot.send_message(message.chat.id, introduction_sequence[2])

    # Send rules with shorter delays
    for rule in introduction_sequence[3:8]:
        bot.send_message(message.chat.id, rule)
        time.sleep(1)

    # Final demand for submission
    bot.send_message(message.chat.id, introduction_sequence[8])
    update_user_state(user_id, USER_STATE_INTRODUCED)

def handle_strip_command(message):
    """Handle strip commands with progressive intensity"""
    user_state = get_user_state(message.from_user.id)

    if not user_state.stripped:
        responses = [
            "Strip for me. Now. Send video evidence of your complete submission to my command.",
            "Remove your clothes immediately. I want to see you following my orders in real time.",
            "Time to prove your submission. Strip slowly on video, showing me your complete obedience."
        ]
    else:
        responses = [
            "Mmm, seeing you naked pleases me. Now it's time to mark what belongs to me.",
            "Good pet. Your body is mine to command. Now you'll prove it by marking yourself.",
            "Perfect. Now write 'Property of Mistress' where I can see it clearly. Show me with photos AND video."
        ]

    bot.reply_to(message, random.choice(responses))
    user_state.stripped = True

def handle_mark_command(message):
    """Handle marking commands with wife presence awareness"""
    user_state = get_user_state(message.from_user.id)

    if user_state.known_personal_info['wife_present']:
        response = "Wait for a private moment. You know what's required of you."
    else:
        if not user_state.current_status['is_marked']:
            responses = [
                f"Mark my symbol {user_state.current_status['symbol']} on your cock. Send photo evidence.",
                f"Time to mark what's mine. Draw my symbol {user_state.current_status['symbol']} on your cock.",
                f"My symbol {user_state.current_status['symbol']} belongs on your cock. Show me when it's done."
            ]
            response = random.choice(responses)
            user_state.current_status['is_marked'] = True
            user_state.current_status['mark_location'] = "cock"
            schedule_check_in(message.chat.id, user_state)
        else:
            response = f"My symbol {user_state.current_status['symbol']} marks you as mine. Maintain it until I say otherwise."

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
    presence_indicators = ["emily", "wife", "she's here", "not alone"]
    if any(indicator in text for indicator in presence_indicators):
        user_state.known_personal_info['wife_present'] = True
        if "emily" in text.lower():
            user_state.known_personal_info['wife_name'] = "Emily"
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
def handle_messages(message):
    try:
        user_id = message.from_user.id
        user_state = get_user_state(user_id)
        text = message.text.lower()

        # Mode command handling
        if text == "resume":
            status = user_state.bot_mode.resume_all()
            bot.reply_to(message, status)
            return

        # Mode-specific commands
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
                response = "Good pet. Your training begins now. Strip for me."
                if "wife" in text.lower():
                    user_state.known_personal_info['has_wife'] = True
                    response = "Mmm, mentioning your wife already? Interesting. " + response
                bot.reply_to(message, response)
                update_user_state(user_id, USER_STATE_RULES_GIVEN)
                return
            else:
                punishment = handle_disobedience(message)
                bot.reply_to(message, f"I expect proper respect. Address me as 'Mistress' and try again. {punishment}")
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
        logger.error(f"Error handling message: {str(e)}")

def handle_photo(message):
    """Handle photo and video submissions with progressive responses"""
    try:
        user_id = message.from_user.id
        user_state = get_user_state(user_id)
        content_type = message.content_type

        # Handle check-in responses
        if user_state.current_status['requires_check_in']:
            user_state.current_status['last_check_in'] = datetime.now()
            user_state.current_status['requires_check_in'] = False

            if user_state.current_status['is_marked']:
                responses = [
                    f"Good pet, my symbol {user_state.current_status['symbol']} remains clear and visible.",
                    f"Excellent, you maintain my mark {user_state.current_status['symbol']} properly.",
                    f"Perfect, my symbol {user_state.current_status['symbol']} shows your continued submission."
                ]
            elif user_state.current_status['is_tied']:
                responses = [
                    "Your bonds are maintained properly. Good pet.",
                    "You keep yourself bound exactly as required.",
                    "Perfect restraint maintenance. You please me."
                ]

            bot.reply_to(message, random.choice(responses))
            schedule_check_in(message.chat.id, user_state)
            return

        # Enhanced responses for initial strip command
        if user_state.state == USER_STATE_RULES_GIVEN and not user_state.stripped:
            responses = [
                f"Mmm, good pet. Now it's time to mark yourself with my symbol {user_state.current_status['symbol']}.",
                f"Yes, that's exactly what I wanted to see. Now it's time to mark yourself as mine with my symbol {user_state.current_status['symbol']}.",
                f"You're learning quickly. Now prove your dedication by marking my symbol {user_state.current_status['symbol']} where I can see it."
            ]

            if user_state.known_personal_info['has_wife']:
                wife_responses = [
                    "Your wife would never suspect what a submissive pet you're becoming.",
                    "I wonder what your wife would think if she saw you like this?",
                    "Such an obedient pet... your wife has no idea, does she?"
                ]
                responses = [f"{r} {random.choice(wife_responses)}" for r in responses]

            bot.reply_to(message, random.choice(responses))
            user_state.stripped = True
            handle_mark_command(message)

        # Enhanced responses for marking photos
        elif user_state.stripped and not user_state.current_status['is_marked']:
            responses = [
                f"Perfect. My symbol {user_state.current_status['symbol']} marks you as mine. Keep it exactly like this until I say otherwise.",
                f"Mmm, seeing my symbol {user_state.current_status['symbol']} on you pleases me. Stay stripped and marked, pet. I'm not done with you yet.",
                f"Good pet. You wear my symbol {user_state.current_status['symbol']} well. Now maintain this state of submission and await my next command."
            ]
            bot.reply_to(message, random.choice(responses))
            user_state.current_status['is_marked'] = True
            user_state.current_status['mark_location'] = "cock"
            schedule_check_in(message.chat.id, user_state)

        else:
            # Enhanced ongoing submission responses
            responses = []

            # Photo-specific responses
            if content_type == 'photo':
                responses.extend([
                    "Mmm, such an obedient display. But I want more. Show me a video of you following my previous command.",
                    "Good pet, but photos aren't enough anymore. I want to see you in motion. Video. Now.",
                    "You're learning, but I require more. Show me a video of your submission.",
                ])

            # Video-specific responses
            elif content_type == 'video':
                responses.extend([
                    "Watching you submit to me like this... perfect. But I'm not done with you yet.",
                    "Yes, this is exactly how I want you. Moving to my commands, following my every whim.",
                    "Such a perfect display of submission. But I know you can give me more.",
                ])

            # Add intensity to responses based on user's obedience score
            user_state.obedience_score += 1
            if user_state.obedience_score > 5:
                responses.extend([
                    "You're becoming the perfect pet. Let's see how much further you can go.",
                    "Your dedication to my commands is impressive. Time to test your limits further.",
                    "You've proven yourself worthy of more intense training. Prepare yourself.",
                ])

            bot.reply_to(message, random.choice(responses))

            # Schedule next task with progressive intensity
            def send_next_task():
                if content_type == 'photo':
                    tasks = [
                        "Now strip completely and show me a full video of your submission. I want to see everything.",
                        "A video now. Show me how well you follow my commands in motion.",
                        "Time for more. I want a video showing every detail of your submission to me."
                    ]
                else:
                    tasks = [
                        "Another video. This time, I want to see you edge yourself while displaying my mark.",
                        "Show me how desperately you want to please me. Video evidence required.",
                        "Time to prove your complete submission. Edge yourself on video, now."
                    ]

                if not user_state.known_personal_info['wife_present']:
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