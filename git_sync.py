import os
import subprocess
import logging
import time
from datetime import datetime
from config import GIT_REPO_URL, GIT_BRANCH, GIT_USERNAME, GIT_EMAIL

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def verify_git_credentials():
    """Verify git credentials are properly configured"""
    try:
        # Test git configuration
        username = subprocess.check_output(['git', 'config', 'user.name']).decode().strip()
        email = subprocess.check_output(['git', 'config', 'user.email']).decode().strip()

        if username != GIT_USERNAME or email != GIT_EMAIL:
            logger.info("Updating git credentials...")
            subprocess.run(['git', 'config', 'user.name', GIT_USERNAME], check=True)
            subprocess.run(['git', 'config', 'user.email', GIT_EMAIL], check=True)

        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error verifying git credentials: {str(e)}")
        return False

def check_git_repo():
    """Check if git repository exists and is properly configured"""
    try:
        # Check if .git directory exists
        if not os.path.exists('.git'):
            logger.info("Git repository not found. Cloning from remote...")
            subprocess.run(['git', 'clone', GIT_REPO_URL, '.'], check=True)
            logger.info("Repository cloned successfully")

        # Verify credentials
        if not verify_git_credentials():
            raise Exception("Failed to verify git credentials")

        # Verify remote
        remote_url = subprocess.check_output(['git', 'remote', 'get-url', 'origin']).decode().strip()
        if remote_url != GIT_REPO_URL:
            logger.info("Updating remote URL...")
            subprocess.run(['git', 'remote', 'set-url', 'origin', GIT_REPO_URL], check=True)

        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error setting up git repository: {str(e)}")
        return False

def git_sync(max_retries=3):
    """Sync changes to GitHub repository with retry mechanism"""
    retry_count = 0
    while retry_count < max_retries:
        try:
            # Ensure repository is properly set up
            if not check_git_repo():
                raise Exception("Failed to set up git repository")

            # Pull latest changes first to avoid conflicts
            logger.info("Pulling latest changes...")
            subprocess.run(['git', 'pull', 'origin', GIT_BRANCH], check=True)

            # Add all changes
            logger.info("Adding changes...")
            subprocess.run(['git', 'add', '.'], check=True)

            # Create commit with timestamp
            commit_message = f"Auto-backup: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            logger.info(f"Creating commit: {commit_message}")

            # Only commit if there are changes
            status = subprocess.check_output(['git', 'status', '--porcelain']).decode()
            if status:
                subprocess.run(['git', 'commit', '-m', commit_message], check=True)

                # Push changes
                logger.info("Pushing changes to GitHub...")
                subprocess.run(['git', 'push', 'origin', GIT_BRANCH], check=True)
                logger.info("Successfully backed up to GitHub")
                return True
            else:
                logger.info("No changes to commit")
                return True

        except Exception as e:
            retry_count += 1
            logger.error(f"Error during git sync (attempt {retry_count}/{max_retries}): {str(e)}")
            if retry_count < max_retries:
                logger.info(f"Retrying in 5 seconds...")
                time.sleep(5)
            else:
                logger.error("Max retries reached. Git sync failed.")
                raise

if __name__ == "__main__":
    try:
        git_sync()
    except Exception as e:
        logger.error(f"Failed to sync with GitHub: {str(e)}")