import logging
import threading
import time
import sys
from bot import bot
from git_sync import git_sync

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def git_sync_thread():
    """Background thread for git synchronization"""
    logger.info("Git sync thread started")
    while True:
        try:
            git_sync()
            time.sleep(300)  # Sync every 5 minutes
        except Exception as e:
            logger.error(f"Error in git sync thread: {str(e)}")
            time.sleep(60)  # Wait a minute before retrying on error

def main():
    try:
        # Start git sync in background thread
        sync_thread = threading.Thread(target=git_sync_thread, daemon=True)
        sync_thread.start()

        # Start the Telegram bot
        logger.info("Starting Telegram bot")
        bot.infinity_polling(timeout=20, long_polling_timeout=5)
    except KeyboardInterrupt:
        logger.info("Stopping bot...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Bot crashed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()