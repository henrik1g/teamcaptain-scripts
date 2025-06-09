# Import necessary libraries
from scripts import config
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import psutil
import sys
import os

# Open Chrome with specified user data and headless mode
def open_chrome(userData, runHeadless):
    # Set up Chrome options
    chrome_options = Options()

    # Add user data directory if provided
    if userData not in [None, ""]:
        # Close previous Chrome instances with the same user data directory
        close_driver_with_userdata(config.chromedriver_user_data_dir)
        chrome_options.add_argument("user-data-dir=" + os.path.join(os.path.dirname(sys.argv[0]), userData))  # Use a custom user data directory

    # Check if running headless
    if runHeadless == True:
        # If running headless, add the headless argument
        chrome_options.add_argument("--headless")

    chrome_options.add_argument("--new-window")  # Open in a new window
    chrome_options.add_experimental_option("detach", True)  # <-- This keeps Chrome open
    chrome_options.add_argument("--log-level=3")  # Suppress most Chrome logs
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])  # Suppress DevTools and other logs
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--disable-gpu")  # Sometimes helps with GPU-related warnings

    driver = webdriver.Chrome(options=chrome_options)
    return driver

def close_driver_with_userdata(chromedriver_user_data_dir):
    user_data_dir = os.path.join(os.path.dirname(sys.argv[0]), chromedriver_user_data_dir)
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info['cmdline'])
                if user_data_dir in cmdline:
                    proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

def close_windows():
    print("⚠️  Closing all Chrome windows...")
    closed = 0
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                proc.terminate()
                closed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    if closed:
        print(f"✅ Closed {closed} Chrome process(es).")
    else:
        print("ℹ️  No Chrome processes found.")

# Function to open a URL in Chrome, handling the first tab differently
def open_tab(driver, url, first_tab):
    if first_tab:
        try:
            driver.get(url)
        except Exception as e:
            print(f"❌ Could not open URL '{url}' - Check if it is valid.")
        first_tab = False
    else:
        driver.execute_script(f"window.open('{url}', '_blank');")
        
    return first_tab

# Function to open Chrome tabs from the url file
def open_tabs():
    # Parse URLs and their desired window numbers
    if not os.path.exists(config.url_file):
        print(f"❌ URL file '{config.url_file}' does not exist. Skipping opening tabs and latest weather briefing.")
    else:
        print("⚙️  Opening Chrome tabs from URL file...")
    try:
        win_urls = {}  # {window_number: [url1, url2, ...]}
        with open(config.url_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("{WIN:"):
                    try:
                        win_part, url = line.split("}", 1)
                        win_num = int(win_part.replace("{WIN:", ""))
                        win_urls.setdefault(win_num, []).append(url.strip())
                    except Exception:
                        continue
                else:
                    win_urls.setdefault(0, []).append(line)

        # Open each window and load its URLs (each URL in a new tab in that window)
        for win_num in sorted(win_urls.keys()):
            driver = open_chrome(None, False)
            urls = win_urls[win_num]
            first_tab = True
            for url in urls:
                # Placeholder replacement logic
                if "{taskID}" in url or "{classURL}" in url or "{classFile}" in url:
                    for class_name in config.classes:
                        task_id = config.selected_task_ids.get(class_name, False)
                        classURL = config.url_map.get(class_name, False)
                        fileURL = config.filename_map.get(class_name, False)
                        replacements = {
                            "{taskID}": task_id,
                            "{classURL}": classURL,
                            "{classFile}": fileURL
                        }
                        url_filled = url
                        for key, value in replacements.items():
                            url_filled = url_filled.replace(key, value)
                        first_tab = open_tab(driver, url_filled, first_tab)
                else:
                    first_tab = open_tab(driver, url, first_tab)
        print("✅ Chrome tabs opened successfully.")
    except Exception as e:
        print(f"❌ Error opening Chrome tabs: {e}") 