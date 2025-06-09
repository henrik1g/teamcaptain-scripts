# Import necessary libraries
from scripts import task_utils
from scripts import config
from selenium.common.exceptions import NoSuchElementException
from git import Repo, GitCommandError
import datetime
import time
import os

# Initialize things
def initialize():
    # Ensure output directories exist
    if not os.path.exists(config.task_output_dir):
        os.makedirs(config.task_output_dir)
    if not os.path.exists(config.glider_output_dir):
        os.makedirs(config.glider_output_dir)

    # Load the latest task IDs for each class
    config.selected_task_ids = task_utils.return_latest_task_ids_for_classes()

# Function to wait for an element to be present in the DOM
def wait_for_element(driver, by, value, timeout=30, poll_frequency=0.2):
    end_time = time.time() + timeout
    while True:
        try:
            element = driver.find_element(by, value)
            time.sleep(0.5)
            return element
        except NoSuchElementException:
            if time.time() > end_time:
                break
            time.sleep(poll_frequency)
    return None

# Function to update and push task/glider files
def commit_and_push_task_and_glider_files():
    try:
        repo = Repo(os.getcwd())
        repo.git.add(["data/"])
        if repo.is_dirty(index=True, working_tree=False, untracked_files=False):
            print(f"⚙️  Committing/pushing task and glider files")
            repo.index.commit("Update tasks and gliders")
            origin = repo.remote(name='origin')
            origin.push()
            print("✅ Changes committed and pushed successfully.")
        else:
            print("ℹ️  No changes to commit.")
    except GitCommandError as e:
        print(f"❌ Commit or push failed: {e}")

# Function to print welcome message
def print_welcome_message():
    print("="*100 + "\n" + "="*100)
    print("⚙️  Welcome to the Team Captain Script!")
    print("📅 Today's date:", datetime.date.today().strftime('%Y-%m-%d'))
    print("This script helps you manage tasks, gliders, and weather briefings for your team.")
    print("Please follow the prompts to prepare for the day and manage your workflow.")
    print("Let's get started!")
    print("="*100 + "\n" + "="*100)