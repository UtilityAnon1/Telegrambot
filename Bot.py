import telebot  
import datetime  
import config  

# Initialize the bot
bot = telebot.TeleBot(config.TELEGRAM_BOT_TOKEN)

# Define user states and tracking
user_states = {}
silent_hours = (16, 8)  # Silent from 4 PM to next morning when user confirms awake
active_modes = {
    "duty_mode": False,
    "family_time": False,
    "personal_time": False
}

# Function to check if it's within silent hours
def is_silent_hours():
    now = datetime.datetime.now().hour
    return silent_hours[0] <= now or now < silent_hours[1]
from datetime import datetime
from config import NO_MESSAGE_DAYS, DUTY_MODE

def can_send_message():
    today = datetime.today().strftime('%A')  # Get current day (e.g., 'Monday')
    
    if today in NO_MESSAGE_DAYS and not DUTY_MODE:
        return False  # Block messages if it's a restricted day and you're not on duty
    return True  # Otherwise, allow messages
# Command to activate duty mode
@bot.message_handler(commands=['on_duty'])
def activate_duty_mode(message):
    active_modes["duty_mode"] = True
    bot.reply_to(message, "Duty Mode activated. I will remain silent unless overridden.")

# Command to deactivate duty mode
@bot.message_handler(commands=['off_duty'])
def deactivate_duty_mode(message):
    active_modes["duty_mode"] = False
    bot.reply_to(message, "Duty Mode deactivated. I'm watching you again.")

# Command to confirm morning wake-up (ends silent mode)
@bot.message_handler(commands=['awake'])
def confirm_awake(message):
    bot.reply_to(message, "Good morning, pet. I’m watching you again.")
    
# Handle normal messages
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if is_silent_hours() and not active_modes["duty_mode"]:
        return  # Ignore messages during silent hours unless overridden
    bot.reply_to(message, "Yes? Do you have something to confess?")
# handle normal messages
def handle_message():
    if can_send_message():
        send_message("Your dominatrix is waiting...")
    else:
        print("Messaging is restricted today.")
# Start bot polling
if __name__ == "__main__":
    bot.polling()
