import os
import subprocess
from datetime import datetime

def git_sync():
    try:
        # Configure git if not already done
        subprocess.run(['git', 'config', 'user.name', 'UtilityAnon1'])
        subprocess.run(['git', 'config', 'user.email', 'utilityanon@gmail.com'])
        
        # Add all changes
        subprocess.run(['git', 'add', '.'])
        
        # Create commit with timestamp
        commit_message = f"Auto-backup: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(['git', 'commit', '-m', commit_message])
        
        # Push changes
        subprocess.run(['git', 'push', 'origin', 'main'])
        print("Successfully backed up to GitHub")
        
    except Exception as e:
        print(f"Error during git sync: {str(e)}")

if __name__ == "__main__":
    git_sync()
