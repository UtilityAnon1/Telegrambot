import telebot
import datetime
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from config import TELEGRAM_BOT_TOKEN, NO_MESSAGE_DAYS, DUTY_MODE

# Initialize the bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Define user states and tracking
user_states = {}
silent_hours = (16, 8)  # Silent from 4 PM to next morning when user confirms awake
active_modes = {
    "duty_mode": False,
    "family_time": False,
    "personal_time": False
}

# Initialize scheduler
scheduler = AsyncIOScheduler()

# Function to check if it's within silent hours
def is_silent_hours():
    now = datetime.datetime.now().hour
    return silent_hours[0] <= now or now < silent_hours[1]

def can_send_message():
    today = datetime.datetime.today().strftime('%A')  # Get current day (e.g., 'Monday')
    
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
async def handle_message(message):
    if is_silent_hours() and not active_modes["duty_mode"]:
        return  # Ignore messages during silent hours unless overridden
    bot.reply_to(message, "Yes? Do you have something to confess?")

# Job for scheduling and tasks (for example)
def scheduled_task():
    if can_send_message():
        bot.send_message(chat_id=message.chat.id, text="Your dominatrix is waiting...")
    else:
        print("Messaging is restricted today.")

# Setup scheduling tasks (example: run every hour)
scheduler.add_job(scheduled_task, 'interval', hours=1)

# Start the scheduler asynchronously
async def start_bot():
    scheduler.start()
    await bot.polling(non_stop=True)

# Run the bot with asyncio to allow asynchronous tasks
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
