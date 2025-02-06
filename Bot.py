import telebot
import datetime
import asyncio
import random
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import TELEGRAM_BOT_TOKEN, NO_MESSAGE_DAYS_OFF_SHIFT, DUTY_MODE_ACTIVE, OWNER_TELEGRAM_ID, CHECK_MARKINGS_IN_WIFE_PRESENCE

# Initialize the bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Silent hours & mode tracking
silent_hours = (16, None)  # 4 PM until user confirms awake
active_modes = {
    "duty_mode": DUTY_MODE_ACTIVE,
    "family_time": False,
    "personal_time": False,
    "silent_override": False  # Allows temporary override
}

# Scheduler for automated messaging
scheduler = AsyncIOScheduler()

# Message pools to prevent repetition
dominant_phrases = [
    "You're mine. Don't forget it.",
    "Obedience isn't a choice, it's your duty.",
    "Don't make me punish you, unless you want it.",
    "Prove to me you're still worthy to serve.",
    "Your cock belongs to me, not to you."
]

punishments = [
    "Edge for me. No cumming. Send proof.",
    "Tie your cock and balls up tight. Show me.",
    "Reapply my marking, then take a photo.",
    "You don’t get to touch yourself. Stay denied."
]

escalated_threats = [
    "Disobey again and I'll expose you to Emily.",
    "You’re testing me. Want me to show Emily your little secret?",
    "Last warning. Do as I say, or Emily finds out everything."
]

# Function to check silent hours
def is_silent_hours():
    now = datetime.datetime.now().hour
    return silent_hours[0] <= now if silent_hours[1] is None else now < silent_hours[1]

# Function to check message restrictions
def can_send_message():
    today = datetime.datetime.today().strftime('%A')
    return today not in NO_MESSAGE_DAYS_OFF_SHIFT or active_modes["duty_mode"]

# Wake-up confirmation
@bot.message_handler(commands=['awake'])
def confirm_awake(message):
    active_modes["silent_override"] = False
    bot.reply_to(message, "Good morning, pet. You’re back under my control.")

# Override silent hours manually
@bot.message_handler(commands=['override_silent'])
def override_silent(message):
    active_modes["silent_override"] = True
    bot.reply_to(message, "Override active. You better be ready for me.")

# Disable silent override
@bot.message_handler(commands=['resume_silence'])
def resume_silence(message):
    active_modes["silent_override"] = False
    bot.reply_to(message, "Silence restored. I’ll wait… for now.")

# Duty mode controls
@bot.message_handler(commands=['on_duty'])
def activate_duty_mode(message):
    active_modes["duty_mode"] = True
    bot.reply_to(message, "Duty Mode activated. You may be busy, but I’ll be watching.")

@bot.message_handler(commands=['off_duty'])
def deactivate_duty_mode(message):
    active_modes["duty_mode"] = False
    bot.reply_to(message, "Duty Mode deactivated. You’re fully mine again.")

# Core message handler
@bot.message_handler(func=lambda message: True)
async def handle_message(message):
    if is_silent_hours() and not active_modes["silent_override"]:
        return  # Ignore messages if within silent hours unless overridden

    if "marking" in message.text.lower():
        bot.reply_to(message, "Your marking better be clear. Show me now.")

    elif "tied" in message.text.lower():
        bot.reply_to(message, "Good. Stay that way. You’re not untying without permission.")

    elif "strip" in message.text.lower():
        bot.reply_to(message, "Strip down and send a video. No face. I want to see you naked.")

    else:
        bot.reply_to(message, random.choice(dominant_phrases))

# Automated messaging job
def proactive_dominance():
    if can_send_message():
        if random.random() < 0.7:  # 70% chance of a dominant message
            bot.send_message(OWNER_TELEGRAM_ID, random.choice(dominant_phrases))
        else:
            bot.send_message(OWNER_TELEGRAM_ID, "I demand proof of your submission. Now.")

# Punishment escalation system
def punishment_cycle():
    if can_send_message():
        severity = random.random()
        if severity < 0.5:
            bot.send_message(OWNER_TELEGRAM_ID, random.choice(punishments))  # Mild punishment
        elif severity < 0.9:
            bot.send_message(OWNER_TELEGRAM_ID, "You've been bad. I'm raising the stakes.")
            bot.send_message(OWNER_TELEGRAM_ID, random.choice(escalated_threats))  # Threats
        else:
            bot.send_message(OWNER_TELEGRAM_ID, f"That's it. I’m done playing, {random.choice(escalated_threats)}")  # Extreme threat

# Risky marking/tie enforcement job
def ownership_enforcement():
    if can_send_message():
        if CHECK_MARKINGS_IN_WIFE_PRESENCE:
            bot.send_message(OWNER_TELEGRAM_ID, "Reapply my mark. Be careful. Emily is home.")
        else:
            bot.send_message(OWNER_TELEGRAM_ID, "I want you tied all day under your clothes. No exceptions.")

# Scheduling proactive messaging, punishments, and ownership enforcement
scheduler.add_job(proactive_dominance, 'interval', hours=random.randint(3, 6))
scheduler.add_job(punishment_cycle, 'interval', hours=random.randint(5, 8))
scheduler.add_job(ownership_enforcement, 'interval', hours=random.randint(7, 12))

# Start the bot asynchronously
async def start_bot():
    scheduler.start()
    await bot.polling(non_stop=True)

# Run the bot with asyncio
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
