# Import necessary libraries
from scripts import libreoffice_utils
from scripts import whatsapp_utils
from scripts import weather_utils
from scripts import chrome_utils
from scripts import glider_utils
from scripts import task_utils
from scripts import config
from scripts import utils
import time
import os

def main_menu():
    utils.print_welcome_message()
    print_menu_header()
    while True:
        try:
            choice = input("\nEnter your choice: ").strip().lower()
            if choice == "1":
                day_preparation()
            elif choice == "2":
                menu_continuous_mode()
            elif choice == "3":
                select_task_ids()
            elif choice == "4":
                update_task_and_glider_files()
            elif choice == "5":
                update_open_metbrief()
            elif choice == "6":
                open_tabs()
            elif choice == "7":
                open_metbrief()
            elif choice == "8":
                send_whatsapp()
            elif choice == "9":
                close_windows()
            elif choice == "0":
                update_Git_Settings()
            elif choice == "q":
                menu_quit()
                break
            else:
                print("❌ Invalid choice. Please try again.")
            # Print the menu header again after each action
            print_menu_header()
        except KeyboardInterrupt:
            menu_quit()

# Function to print menu headers
def print_menu_header():
    print("\n" + "="*100)
    print("⚙️  Main Menu ⚙️")
    print("="*100)
    print("Please choose an option from the menu below:")
    print("="*100)
    print('1. Prepare for the day (update tasks, gliders, weather briefing, and open all tabs)')
    print("2. Run continuously, checking for new tasks every 30 seconds and updating if needed")
    print('3. Select task IDs for classes (only to activate old tasks)')
    print("4. Update glider and task files")
    print("5. Update and open weather briefing (no WhatsApp send)")
    print("6. Open Chrome tabs from the URL file")
    print("7. Open the latest weather briefing")
    print("8. Send latest weather briefing via WhatsApp")
    print("9. Close all open Chrome and LibreOffice windows")
    print("0. Update git settings (enable/disable automatic commit and push after updates)")
    print("Q. Quit")
    print("="*100)

# Do a full day preparation
def day_preparation():
    # --- TASK AND GLIDER FILES ---
    print("⚙️  Preparing for the day...")
    # Update task files
    update_task_and_glider_files()
    # Update weather briefing
    weather_utils.update_metbrief()
    # Open Chrome tabs from the URL file and latest weather briefing
    open_tabs()
    # Open the latest weather briefing
    open_metbrief()

def menu_continuous_mode():
    print("🔄 Entering continuous update mode. Press Ctrl+C to stop. \n")
    last_task_ids = task_utils.return_latest_task_ids_for_classes()
    try:
        while True:
            # Check for new tasks every 30 seconds
            current_task_ids = task_utils.return_latest_task_ids_for_classes()
            if current_task_ids != last_task_ids:
                print("🆕 New tasks detected! Updating and pushing...")
                # Load the latest task IDs for each class
                config.selected_task_ids = current_task_ids
                # Update task files
                update_task_and_glider_files()
            else:
                print("⏳ No new tasks. Checking again in 30 seconds... Press Ctrl+C to stop.")
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n⏹️  Continuous update stopped by user.")

# Select task IDs for each class
def select_task_ids():
    task_utils.select_task_ids()

# Function to update task and glider files
def update_task_and_glider_files():
    # Update task files
    task_utils.update_task_files()
    # Update glider files
    glider_utils.update_glider_files()
    # Commit and push task and glider files if enabled
    if config.commit_and_push_to_git == True:
        utils.commit_and_push_task_and_glider_files()

# Function to close all Chrome windows
def open_tabs():
    chrome_utils.open_tabs()

# Function to close all chrome and LibreOffice windows
def close_windows():
    chrome_utils.close_windows()
    libreoffice_utils.close_windows()

def open_metbrief():
    # Open the latest weather briefing
    print("⚙️  Opening latest weather briefing")
    filepath = weather_utils.get_latest_weather_briefing_folderPath()
    fullFilepath = weather_utils.get_latest_weather_briefing_fullPath()
    if os.path.exists(filepath):
        libreoffice_utils.open_file(fullFilepath)
        print(f"✅ Latest weather briefing opened")
    else:
        print("❌ Latest weather briefing not found. Please generate it first.")

# Update and open latest weather briefing
def update_open_metbrief():
    # Update the weather briefing
    weather_utils.update_metbrief()
    # Close all LibreOffice windows before opening the latest weather briefing
    libreoffice_utils.close_windows()
    # Open the latest weather briefing
    open_metbrief()

# Function to send the weather briefing to a WhatsApp group
def send_whatsapp():
    print(f"⚙️  Creating PDF from ODP file...")
    odp_path = weather_utils.get_latest_weather_briefing_fullPath()
    if not os.path.exists(odp_path):
        print("❌ ODP file not found.")
        return
    pdf_path = libreoffice_utils.convert_odp_to_pdf(odp_path)
    if pdf_path:
        whatsapp_utils.send_pdf_to_whatsapp_group(pdf_path)

# Function to enable/disable git commit/push elsewhere
def update_Git_Settings():
    print("="*100)
    print("⚙️  Git Settings")
    print("="*100)
    print("Current setting: Automatic git commit and push after updates is", "enabled" if config.commit_and_push_to_git else "disabled")
    print("="*100)
    choice = input("❓ Do you want to enable automatic git commit and push after updates? (Y/N)? ").strip().lower()
    if choice == "y":
        config.commit_and_push_to_git = True
        print("✅ Automatic git commit and push enabled.")
    elif choice == "n":
        config.commit_and_push_to_git = False
        print("ℹ️  Automatic git commit and push disabled.")
    else:
        print("❌ Invalid choice. No changes made.")

# Function to gracefully quit
def menu_quit():
    try:
        choice = input('\nDo you want to close all open windows? (Y/N): ').strip().lower()

        # Close all Chrome and LibreOffice windows if the user chooses to do so
        if choice == "y":
            close_windows()
        elif choice == "n":
            print("ℹ️  Not closing any windows.")
        else:
            print("ℹ️  Invalid choice. Not closing any windows.")

        print("\n👋 Exiting the script. Thank you for using the Team Captain Script!")
    except KeyboardInterrupt:
        print("\n\n👋  Fine - be like that. Exiting without closing windows.")
    exit(0)