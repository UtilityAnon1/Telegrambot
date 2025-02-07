import random

# config.py - Simplified configuration with conditional personal time logic (percentage-based)

# Define the available modes and their default states (all off initially)
MODES = {
    'duty_mode': False,
    'family_time_mode': False,
    'me_time_mode': False,
    'emergency_pause': False,
}

# Define the responses for each mode when activated
MODE_RESPONSES = {
    'duty_mode': 'You are now in Duty Mode. Focus on your responsibilities.',
    'family_time_mode': 'You are now in Family First Mode. Time to be present with loved ones.',
    'me_time_mode': 'You are now in Personal Time Mode. Enjoy your personal moments.',
    'emergency_pause': 'You are now in Emergency Pause Mode. All interactions are temporarily paused.',
    'personal_time_denied': 'I do not allow you personal time right now. Focus on me.',
}

# Mode commands (activation phrases for each mode)
MODE_COMMANDS = {
    'duty_mode': 'duty mode',
    'family_time_mode': 'family first',
    'me_time_mode': 'personal time',
    'emergency_pause': 'emergency',
    'resume': 'resume'
}

# Function to determine if personal time is allowed based on a percentage chance
def check_personal_time_permission():
    # Adjust the percentage chance (e.g., 50% chance to allow personal time)
    chance = random.randint(1, 100)  # Generates a random number between 1 and 100
    if chance <= 50:  # 50% chance to allow personal time (you can adjust the percentage here)
        return True  # Personal time allowed
    else:
        return False  # Personal time denied

# Define resume behavior: Deactivates any active mode and returns to full power mode
def handle_resume():
    for mode in MODES:
        MODES[mode] = False  # Turn off all modes when "resume" is activated
    return 'You are back in full control. All previous modes have been deactivated.'
