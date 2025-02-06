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
    "silent_override": False,  # Allows temporary override
    "emergency_shutdown": False,  # Emergency shutdown
    "family_time_duration": None,  # For tracking family time window
    "personal_time_duration": None  # For tracking personal time window
}

# Scheduler for automated messaging
scheduler = AsyncIOScheduler()

# Message pools to prevent repetition and add dynamic learning
dominant_phrases = [,
    "Your cock belongs to me, not to you."
    "Strip. Now. Don't make me ask again.",
    "I don’t like waiting. Take off everything. You know the rules.",
    "You belong to me. You don’t get to say no.",
    "Get naked, now. Video proof. Don’t test me.",
    "I want you exposed. I want you helpless. I want you **mine**.",
    "Your wife thinks she knows everything about you. Should I prove her wrong?",
    "You wouldn’t dare disobey me if your wife was watching, would you?",
    "You have seconds to obey before I start making this **very real** for you.",
    "You know I control you. Get naked, show me proof, and **thank me for the privilege.**",
    "Imagine if your wife saw this. Maybe I should help make that happen.",
    "Emily would love to see you grovel at my feet. Don’t make me call her in.",
    "Want to test my patience? Wait until I show your wife your dirty little secrets.",
    "I’ll let Emily in on your disobedience if you keep this up.",
    "You can try to resist, but you know who owns you. Keep pushing, and I’ll show both your wife and Emily who really has control.",
    "What would Emily say if she saw you failing like this? You’re on thin ice.",
    "Do you think Emily would be proud of your behavior? Show me you can obey, or I'll let her know.",
    "Those videos and photos of you naked, tied up with my name written on you... how long do you think you can keep that secret from your wife?",
    "If you fail again, I’ll send those photos and videos to your wife. I wonder how she’ll react when she sees you like this.",
    "Those videos of you naked with my name on your cock? Do you want me to send them to Emily? I’m sure she’d love to see them.",
    "You really think I won’t send those photos to your wife? That’s a bad mistake, pet.",
    "I can always make those videos and photos public, so your wife and Emily know what you've been up to. Don’t test me.",
    "Those photos you sent me? They’re safe for now. But keep disobeying, and I’ll make sure your wife sees them.",
    "Your cock tied up with my name on it... is it worth it? Because I can make Emily see those if you disobey again."

]   punishment_phrases = [
    "You just made a mistake. A big one.",
    "I don’t tolerate failure. You **will** be punished.",
    "Ignoring me? Bad move. Maybe I should let your wife in on our little secret?",
    "You forget who owns you. Maybe a little reminder is needed?",
    "You're playing a dangerous game. Should I show your wife what you're up to?",
    "Disobedience means consequences. You know what happens next.",
    "You're testing me, aren't you? I can’t wait to show Emily your little secret.",
    "Your wife would be so disappointed to see this. Want to test me further?",
    "One more mistake, and Emily will know exactly what you're doing.",
    "Keep disobeying, and your wife won’t be the only one who finds out.",
    "Think Emily won’t care? Keep pushing, and she’ll know all about your little rebellion.",
    "If you keep this up, I’m showing your wife your secrets. Let’s see how she reacts.",
    "You know those photos of you tied up with my name on your cock? I can always send them to your wife. Think she’d enjoy that?",
    "Those videos of you naked? You don’t want me to share them, do you? I’ll send them straight to Emily if you keep misbehaving.",
    "If you disobey again, I’ll show your wife what you’ve been doing behind her back. I wonder how she’ll feel about those photos of you.",
    "You’re walking a fine line, pet. Keep it up, and I’ll send the video of you with my name on your cock to Emily.",
    "Disobedience means I can expose you. Videos, photos—your wife and Emily will know everything. Is that what you want?"
]

edging_phrases = [
    "Edge for me now, and don't you dare cum until I say so.",
    "You're not allowed to cum yet. Edge for me and hold it.",
    "Feel that pressure building? You won’t release until I say you can.",
    "Edge and stop, again and again. Your release is mine to control.",
    "No release until I tell you. You're going to beg for it, and I’ll enjoy making you wait.",
    "Your cock doesn’t get to cum until I say so—edge for me until you're desperate.",
    "Keep edging until I say you can finish. Your orgasm is mine to command.",
    "I want you to feel the edge, but you don’t get to cum. Not yet.",
    "You think you’re close? Not yet. Hold it. Edge for me."
]
forced_multiple_orgasm_phrases = [
    "You will cum for me, over and over. No stopping until I say so.",
    "Get ready to cum multiple times. There’s no escape from this.",
    "You're going to cum again, and again, and again. You don't get to rest.",
    "Multiple orgasms, all at once. You won’t stop until I tell you to.",
    "I decide when you cum, and right now, you're going to cum again.",
    "Feel that pressure? You're going to cum multiple times, and I won’t let you stop.",
    "No mercy. You’ll cum again, whether you like it or not.",
    "I’ll make you cum multiple times, pushing you beyond your limits.",
    "Multiple orgasms, pet. Get ready to beg for release as I make you cum again."
]
marking_commands_phrases = [
    "Mark yourself for me. Write my name on your cock, now.",
    "Don’t let the marking fade. Keep it fresh. I’ll know if it does.",
    "You’ll write my name on your cock. Don’t even think about stopping.",
    "Make sure my name is visible. I want to see it on you.",
    "You’ll be marked for me. Write my name on your cock, and show it to me.",
    "Do you think your marking will fade? No. Keep it visible. I’ll check.",
    "If the marking fades, you’ll need to reapply it immediately. Don’t forget.",
    "Mark yourself with my name, now. I want to see the proof of your obedience.",
    "You’ll mark yourself with my name, and it will stay visible. I’m in control.",
    "When I tell you to mark yourself, you do it without hesitation. I own you."
]
tie_commands_phrases = [
    "Tie yourself up for me. Show me proof once you're done.",
    "Get the rope. Tie yourself up. Send me a picture of you like that.",
    "Tie your cock up with rope. Send me a photo of the knots.",
    "I want you tied up and exposed. Show me the proof, now.",
    "Use the rope and tie yourself up. Make sure it’s tight, then send me a photo.",
    "Tie yourself up. Let me see the markings along with the knots.",
    "Show me your tied-up cock with my name on it. Make sure it’s clear.",
    "Take a photo of yourself tied up, then show me the markings."
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
@bot.message_handler(commands=['resume'])
def resume(message):
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

# Family Time Mode
@bot.message_handler(commands=['family_first'])
def activate_family_time(message):
    if active_modes["family_time"]:
        bot.reply_to(message, "Family Time is already active.")
    else:
        try:
            hours = int(message.text.split()[1])  # expects "family_first X"
            if 1 <= hours <= 3:
                active_modes["family_time"] = True
                active_modes["family_time_duration"] = hours
                bot.reply_to(message, f"Family Time activated for {hours} hours.")
            else:
                bot.reply_to(message, "Family Time duration must be between 1 and 3 hours.")
        except (IndexError, ValueError):
            bot.reply_to(message, "Please specify the duration (1-3 hours).")

# Personal Time Mode
@bot.message_handler(commands=['personal_time'])
def activate_personal_time(message):
    if active_modes["personal_time"]:
        bot.reply_to(message, "Personal Time is already active.")
    else:
        if random.random() < 0.5:  # 50% chance to allow
            try:
                hours = int(message.text.split()[1])  # expects "personal_time X"
                if 1 <= hours <= 3:
                    active_modes["personal_time"] = True
                    active_modes["personal_time_duration"] = hours
                    bot.reply_to(message, f"Personal Time activated for {hours} hours.")
                else:
                    bot.reply_to(message, "Personal Time duration must be between 1 and 3 hours.")
            except (IndexError, ValueError):
                bot.reply_to(message, "Please specify the duration (1-3 hours).")
        else:
            bot.reply_to(message, "I’m not in the mood to allow Personal Time right now.")

# Emergency Shutdown - 24 Hour
@bot.message_handler(commands=['emergency'])
def emergency_shutdown(message):
    if active_modes["emergency_shutdown"]:
        bot.reply_to(message, "Emergency shutdown is already active.")
    else:
        active_modes["emergency_shutdown"] = True
        bot.reply_to(message, "24-hour Emergency Shutdown activated. You’re on hold for now.")

# Irreversible Permanent Shutdown
@bot.message_handler(commands=['i_surrender'])
def irreversible_shutdown(message):
    bot.reply_to(message, "Permanent shutdown activated. You will be locked out forever.")
    # Implement your app shutdown or lockout code here
    exit()  # Or other mechanisms to disable bot permanently

# Core message handler
@bot.message_handler(func=lambda message: True)
async def handle_message(message):
    if active_modes["emergency_shutdown"]:
        bot.reply_to(message, "Emergency shutdown is active. No further commands will be accepted.")
        return

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
