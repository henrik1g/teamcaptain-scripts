from scripts import config
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium import webdriver
import psutil
import sys
import os

def open_browser(userData=False, runHeadless=False, whatsAppBrowser=False):
    if whatsAppBrowser:
        browser = "chrome"
    else:
        browser = getattr(config, "browser", "firefox").lower()
    if browser == "chrome":
        chrome_options = ChromeOptions()
        if userData:
            close_chrome_with_userdata(config.chromedriver_user_data_dir)
            chrome_options.add_argument("user-data-dir=" + os.path.join(os.path.dirname(sys.argv[0]), config.chromedriver_user_data_dir))
        if runHeadless:
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--new-window")
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=chrome_options)
    elif browser == "firefox":
        geckodriver_path = "/snap/bin/geckodriver"
        driver_service = webdriver.FirefoxService(executable_path=geckodriver_path)
        firefox_options = FirefoxOptions()
        if runHeadless:
            firefox_options.add_argument("--headless")
        profile = None
        if userData:
            # userData should be the path to the Firefox profile directory
            firefox_options.profile = config.firefoxdriver_user_data_dir
        driver = webdriver.Firefox(options=firefox_options,service=driver_service)
    else:
        raise ValueError(f"Unsupported browser: {browser}")
    if whatsAppBrowser:
        config.whatsapp_driver = driver
    else:
        config.all_drivers.append(driver)
    return driver

def close_chrome_with_userdata(chromedriver_user_data_dir):
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
    print("⚠️  Closing all browser windows...")
    # Close all tracked browser windows
    closed = 0
    for driver in getattr(config, "all_drivers", []):
        try:
            driver.quit()
            closed += 1
        except Exception:
            pass
    if closed:
        print(f"✅ Closed {closed} browser process(es).")
    else:
        print("ℹ️  No browser processes found.")
    config.all_drivers.clear()

def close_whatsapp_driver():
    try:
        config.whatsapp_driver.quit()
        config.whatsapp_driver = None
    except:
        print("❌ Failed to close the browser config.whatsapp_driver. Something really went wrong.")

# Function to open a URL in browser, handling the first tab differently
def open_tab(driver, url, first_tab):
    if first_tab:
        try:
            driver.get(url)
        except Exception as e:
            print(f"❌ Could not open URL '{url}' - Check if it is valid.")
        first_tab = False
    else:
        driver.execute_script(f"window.open('{url}', '_blank');")
    # Always switch to the newest tab (works for both Chrome and Firefox)
    driver.switch_to.window(driver.window_handles[-1])
    return first_tab

# Function to open Chrome tabs from the url file
def open_tabs():
    if not os.path.exists(config.url_file):
        print(f"❌ URL file '{config.url_file}' does not exist. Skipping opening tabs and latest weather briefing.")
        return
    print("⚙️  Opening browser tabs from URL file...")

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
                        url = url.strip()
                        win_key = win_part.replace("{WIN:", "")
                        if win_key == "I":
                            # {WIN:I} - one window per class
                            github_path = getattr(config, "github_path", "")
                            base_replacements = {"{gitHubPath}": github_path}
                            if any(ph in url for ph in ("{taskID}", "{classURL}", "{classFile}")):
                                for class_name in config.classes:
                                    task_id = config.selected_task_ids.get(class_name, "")
                                    class_url = config.url_map.get(class_name, "")
                                    file_url = config.filename_map.get(class_name, "")
                                    if not all([task_id, class_url, file_url]):
                                        continue
                                    replacements = {
                                        **base_replacements,
                                        "{taskID}": task_id,
                                        "{classURL}": class_url,
                                        "{classFile}": file_url,
                                    }
                                    url_filled = url
                                    for key, value in replacements.items():
                                        url_filled = url_filled.replace(key, value)
                                    # Use a unique window number for each class window
                                    win_urls.setdefault(f"I_{class_name}", []).append(url_filled)
                            else:
                                # If no class placeholders, treat as a normal window
                                win_urls.setdefault("I", []).append(url)
                        else:
                            win_num = int(win_key)
                            github_path = getattr(config, "github_path", "")
                            base_replacements = {"{gitHubPath}": github_path}
                            if any(ph in url for ph in ("{taskID}", "{classURL}", "{classFile}")):
                                for class_name in config.classes:
                                    task_id = config.selected_task_ids.get(class_name, "")
                                    class_url = config.url_map.get(class_name, "")
                                    file_url = config.filename_map.get(class_name, "")
                                    if not all([task_id, class_url, file_url]):
                                        continue
                                    replacements = {
                                        **base_replacements,
                                        "{taskID}": task_id,
                                        "{classURL}": class_url,
                                        "{classFile}": file_url,
                                    }
                                    url_filled = url
                                    for key, value in replacements.items():
                                        url_filled = url_filled.replace(key, value)
                                    win_urls.setdefault(win_num, []).append(url_filled)
                            else:
                                url_filled = url
                                for key, value in base_replacements.items():
                                    url_filled = url_filled.replace(key, value)
                                win_urls.setdefault(win_num, []).append(url_filled)
                    except Exception:
                        print(f"❌ URL '{line}' has an invalid window ID.")
                        continue
                else:
                    # No {WIN:} - default to window 0
                    url = line
                    github_path = getattr(config, "github_path", "")
                    base_replacements = {"{gitHubPath}": github_path}
                    if any(ph in url for ph in ("{taskID}", "{classURL}", "{classFile}")):
                        for class_name in config.classes:
                            task_id = config.selected_task_ids.get(class_name, "")
                            class_url = config.url_map.get(class_name, "")
                            file_url = config.filename_map.get(class_name, "")
                            if not all([task_id, class_url, file_url]):
                                continue
                            replacements = {
                                **base_replacements,
                                "{taskID}": task_id,
                                "{classURL}": class_url,
                                "{classFile}": file_url,
                            }
                            url_filled = url
                            for key, value in replacements.items():
                                url_filled = url_filled.replace(key, value)
                            win_urls.setdefault(0, []).append(url_filled)
                    else:
                        url_filled = url
                        for key, value in base_replacements.items():
                            url_filled = url_filled.replace(key, value)
                        win_urls.setdefault(0, []).append(url_filled)

        # Step 2: Open each window and load its URLs (each URL in a new tab in that window)
        first_window = True
        for win_num in win_urls:
            first_tab = True
            urls = win_urls[win_num]

            if first_window:
                config.driver = open_browser(True, False, False)
                first_window = False
                for url in urls:
                    first_tab = open_tab(config.driver, url, first_tab)
            else:
                driver = open_browser(None, False, False)
                for url in urls:
                    first_tab = open_tab(driver, url, first_tab)
            
        print("✅ Browser tabs opened successfully.")
    except Exception as e:
        print(f"❌ Error opening browser tabs: {e}")
