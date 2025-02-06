import telebot
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import TELEGRAM_BOT_TOKEN, DUTY_MODE_ACTIVE, OWNER_TELEGRAM_ID

# Initialize the bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Active mode tracking
active_modes = {
    "duty_mode": DUTY_MODE_ACTIVE,
    "family_time": False,
    "personal_time": False,
    "emergency_shutdown": False,  # Emergency shutdown
    "family_time_duration": None,  # For tracking family time window
    "personal_time_duration": None  # For tracking personal time window
}

# Scheduler for automated messaging
scheduler = AsyncIOScheduler()

# Message pools to prevent repetition and add dynamic learning
dominant_phrases = [
    "Your cock belongs to me, not to you.",
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
    "You can try to resist, but you know who owns you. Keep pushing, and I’ll show both your wife and Emily who really has control.",
    "What would Emily say if she saw you failing like this? You’re on thin ice.",
    "Do you think Emily would be proud of your behavior? Show me you can obey, or I'll let her know.",
    "Those videos and photos of you naked, tied up with my name on them... how long do you think you can keep that secret from your wife?",
    "If you fail again, I’ll send those photos and videos to your wife. I wonder how she’ll react when she sees you like this.",
    "Those videos of you naked? You don’t want me to share them, do you? I’ll send them straight to Emily if you keep misbehaving.",
    "If you disobey again, I’ll show your wife what you’ve been doing behind her back. I wonder how she’ll feel about those photos of you.",
    "You’re walking a fine line, pet. Keep it up, and I’ll send the video of you with my name on your cock to Emily.",
    "Disobedience means I can expose you. Videos, photos—your wife and Emily will know everything. Is that what you want?"
]

punishment_phrases = [
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

# Helper function to check for natural speech
def handle_user_message(message):
    text = message.text.lower()
    response = None
    
    # Simple keyword-based adaptive responses
    if "obedience" in text:
        response = "Good. Obey me, and you may just get some rewards."
    elif "disobey" in text:
        response = "You don't want to test my patience. Obey or face the consequences."
    elif "wife" in text:
        response = "If you want to keep your secrets from her, you better stay obedient."
    elif "marking" in text:
        response = "Marking yourself is your responsibility. Don't let me down."
    
    if response:
        bot.reply_to(message, response)
    else:
        # Default response
        bot.reply_to(message, "I don't have time for excuses. Obey.")

# Handle photo submissions
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    photo_id = message.photo[-1].file_id  # Get the highest resolution photo
    file_info = bot.get_file(photo_id)
    file_url = f'https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_info.file_path}'
    
    # For now, a simple acknowledgment of the photo
    bot.reply_to(message, f"Photo received. You better hope it’s what I asked for. Don’t disappoint me.")
    
    # You can expand on this to add more photo handling logic based on the content of the photo
    # Example: You could check for certain tags or content in the image description or context.

# Your bot start functionality and command handlers here
if __name__ == '__main__':
    @bot.message_handler(func=lambda message: True)
    def any_message(message):
        # Handle all incoming messages
        handle_user_message(message)
    
    bot.polling(none_stop=True)
