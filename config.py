# Telegram Bot Token  
TELEGRAM_BOT_TOKEN = "8067845782:AAHvpt4QMG2D2G3-KVMox7rHhRWEb9hfStg"  

# Your Telegram User ID (Replace with your actual Telegram ID)  
OWNER_TELEGRAM_ID =  7827015430

# Default settings for tracking and restrictions  
DUTY_MODE_ACTIVE = False  
FAMILY_TIME_ACTIVE = False  
PERSONAL_TIME_ACTIVE = False  
VACATION_MODE_ACTIVE = False  

# Emergency shutdown keyword  
EMERGENCY_SHUTDOWN_PHRASE = "I surrender"  

# Emergency 24-hour pause keyword  
EMERGENCY_PAUSE_PHRASE = "Emergency"  

# Activation phrases for different modes  
FAMILY_TIME_PHRASE = "Family first"  
PERSONAL_TIME_PHRASE = "Personal time"  
DUTY_MODE_PHRASE = "On duty"  

# Ownership and marking awareness with added risk play  
BE_MINDFUL_OF_WIFE_PRESENCE = True  # Reflects mindfulness of wife’s presence
RISK_PLAY_ENABLED = True  # Allows for introducing risks for extra thrill and exposure

# Days when no messages should be sent if off shift
NO_MESSAGE_DAYS = ["Wednesday", "Saturday", "Sunday", "Monday"]  # Adjusted for consistency

# Silent hours configuration (starts at 4 PM and ends when user confirms awake)
SILENT_HOURS_START = 16  # 4 PM
SILENT_HOURS_CONFIRMATION_REQUIRED = True  # Silent hours end when the user confirms being awake

# Override silent hours or modes if unexpectedly available
OVERRIDE_PHRASE = "Override mode"  # Command to override silent hours or mode
RESUME_PHRASE = "Resume"  # Command to resume or reactivate the active mode
REVERT_PHRASE = "End override"  # Command to revert back to normal restrictions

# Polling and Async Configuration (aligning with `bot.py` updates)
# Polling setup for async processing
POLLING_INTERVAL = 5  # Polling interval (in seconds)
ASYNC_MODE_ENABLED = True  # We will keep async mode enabled
POLLING_TIMEOUT = 10  # Timeout for async tasks

# Async task settings
MAX_TASK_RETRIES = 3  # Max retry attempts for failed tasks
TASK_RETRY_INTERVAL = 10  # Time to wait between retries (in seconds)

# Other settings
UPDATE_INTERVAL = 5  # Adjust polling frequency for updates (in seconds)
