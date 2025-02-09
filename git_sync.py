import os
import subprocess
import logging
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def initialize_git():
    """Initialize git repository if not already initialized"""
    try:
        if not os.path.exists('.git'):
            logger.info("Initializing git repository...")
            subprocess.run(['git', 'init'], check=True)

        # Configure git credentials using environment variables
        github_token = os.environ.get('GITHUB_TOKEN')
        repo_url = os.environ.get('REPO_URL')
        git_username = os.environ.get('GIT_USERNAME', 'UtilityAnon1')
        git_email = os.environ.get('GIT_EMAIL', 'utilityanon@gmail.com')

        if not github_token or not repo_url:
            raise Exception("Missing required git credentials")

        # Configure git user
        subprocess.run(['git', 'config', 'user.name', git_username], check=True)
        subprocess.run(['git', 'config', 'user.email', git_email], check=True)

        # Format repository URL with token for authentication
        if 'https://' in repo_url:
            auth_repo_url = f"https://{github_token}@{repo_url.split('https://')[1]}"
        else:
            auth_repo_url = repo_url

        # Add remote if not exists
        try:
            subprocess.run(['git', 'remote', 'get-url', 'origin'], check=True)
            # Update remote URL with authentication
            subprocess.run(['git', 'remote', 'set-url', 'origin', auth_repo_url], check=True)
        except subprocess.CalledProcessError:
            subprocess.run(['git', 'remote', 'add', 'origin', auth_repo_url], check=True)

        # Ensure we're on main branch
        try:
            subprocess.run(['git', 'checkout', 'main'], check=True)
        except subprocess.CalledProcessError:
            subprocess.run(['git', 'checkout', '-b', 'main'], check=True)

        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Error initializing git: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during git initialization: {str(e)}")
        return False

def git_sync(max_retries=3):
    """Sync changes to GitHub repository with retry mechanism"""
    if not initialize_git():
        logger.error("Failed to initialize git repository")
        return False

    retry_count = 0
    while retry_count < max_retries:
        try:
            # Add all changes
            logger.info("Adding changes...")
            subprocess.run(['git', 'add', '.'], check=True)

            # Only commit if there are changes
            status = subprocess.check_output(['git', 'status', '--porcelain']).decode()
            if status:
                # Create commit with timestamp
                commit_message = f"Auto-backup: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                logger.info(f"Creating commit: {commit_message}")
                subprocess.run(['git', 'commit', '-m', commit_message], check=True)

                # Push changes
                logger.info("Pushing changes to GitHub...")
                subprocess.run(['git', 'push', '-u', 'origin', 'main'], check=True)
                logger.info("Successfully backed up to GitHub")
            else:
                logger.info("No changes to commit")
            return True

        except subprocess.CalledProcessError as e:
            retry_count += 1
            logger.error(f"Error during git sync (attempt {retry_count}/{max_retries}): {str(e)}")
            if retry_count < max_retries:
                logger.info(f"Retrying in 5 seconds...")
                time.sleep(5)
            else:
                logger.error("Max retries reached. Git sync failed.")
                return False

if __name__ == "__main__":
    try:
        git_sync()
    except Exception as e:
        logger.error(f"Failed to sync with GitHub: {str(e)}")