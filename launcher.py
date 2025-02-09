import logging
from bot import bot

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    # Start the Telegram bot
    logger.info("Starting Telegram bot")
    bot.polling(none_stop=True)

if __name__ == "__main__":
    main()