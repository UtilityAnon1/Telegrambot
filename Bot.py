from config import * import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os

# Get your bot token from Telegram (you already have it)
TOKEN = "8067845782:AAHvpt4QMG2D2G3-KVMox7rHhRWEb9hfStg"

def start(update, context):
    update.message.reply_text("I'm watching you. Obey or face the consequences.")

def punish(update, context):
    update.message.reply_text("You failed. Prepare for punishment.")

def message_handler(update, context):
    text = update.message.text.lower()
    if "fail" in text:
        punish(update, context)
    else:
        update.message.reply_text("Good. Keep obeying.")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
