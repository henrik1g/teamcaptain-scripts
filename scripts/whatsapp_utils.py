# Import necessary libraries
from scripts import browser_utils
from scripts import config
from scripts import utils
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os
import time

# Function to send the latest weather briefing PDF to a WhatsApp group
def send_pdf_to_whatsapp_group(pdf_path):
    print(f"⚙️  Sending latest weather briefing to WhatsApp group '{config.whatsapp_group}'")
    try:
        # Should only ever be None
        if config.whatsapp_driver == None:
            config.whatsapp_driver = browser_utils.open_browser(userData=True, runHeadless=False, whatsAppBrowser=True)
            first_tab = True
        else:
            first_tab = False

        url = "https://web.whatsapp.com/"
        browser_utils.open_tab(config.whatsapp_driver, url, first_tab)
        # Switch to the newest tab
        config.whatsapp_driver.switch_to.window(config.whatsapp_driver.window_handles[-1])

        # Wait for WhatsApp Web to load (minimized sleep, responsive)
        search_box = utils.wait_for_element(config.whatsapp_driver, By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]', timeout=config.whatsapp_timeout, poll_frequency=0.2)
        if not search_box:
            print("❌ WhatsApp Web did not load properly. Please check your internet connection and try again.")
            if first_tab:
                browser_utils.close_whatsapp_driver()
            return

        search_box.click()
        time.sleep(0.2)
        try:
            search_box.clear()
        except Exception:
            # fallback if clear() is not supported
            search_box.send_keys(Keys.BACKSPACE * 30)
        search_box.send_keys(config.whatsapp_group)
        # Wait for chats to load
        time.sleep(1)

        # Re-find all chat titles after the DOM update
        chat_spans = config.whatsapp_driver.find_elements(By.XPATH, '//span[@title]')
        group = None
        for span in chat_spans:
            try:
                title = span.get_attribute("title")
                if config.whatsapp_group in title and span.is_displayed():
                    group = span
                    break
            except Exception:
                continue
        if not group:
            print(f"❌ Could not find WhatsApp group containing '{config.whatsapp_group}'.")
            if first_tab:
                browser_utils.close_whatsapp_driver()
            return
        group.click()

        # Attach file
        attach_btn = utils.wait_for_element(config.whatsapp_driver, By.CSS_SELECTOR, "span[data-icon='plus-rounded']", timeout=config.whatsapp_timeout, poll_frequency=0.2)
        if not attach_btn:
            print("❌ Could not find attach button.")
            if first_tab:
                browser_utils.close_whatsapp_driver()
            return
        attach_btn.click()

        file_input = utils.wait_for_element(config.whatsapp_driver, By.CSS_SELECTOR, "input[type='file']", timeout=config.whatsapp_timeout, poll_frequency=0.2)
        if not file_input:
            print("❌ Could not find file input.")
            if first_tab:
                browser_utils.close_whatsapp_driver()
            return
        file_input.send_keys(os.path.abspath(pdf_path))

        # Message input (caption)
        msg_box = utils.wait_for_element(config.whatsapp_driver, By.XPATH, '//div[@contenteditable="true"][@aria-placeholder="Add a caption"]', timeout=config.whatsapp_timeout, poll_frequency=0.2)
        if not msg_box:
            print("❌ Could not find message input box.")
            if first_tab:
                browser_utils.close_whatsapp_driver()
            return
        msg_box.click()
        msg_box.send_keys(config.whatsapp_message)
        msg_box.send_keys(u'\ue007')  # Press Enter

        # Wait for the message to be sent
        time.sleep(config.whatsapp_group_send_time)  # Wait for a few seconds to ensure the message is sent
        if not first_tab:
            config.whatsapp_driver.close()
            # Switch back to the last remaining tab (if any)
            if config.whatsapp_driver.window_handles:
                config.whatsapp_driver.switch_to.window(config.whatsapp_driver.window_handles[-1])
        else:
            browser_utils.close_whatsapp_driver()
        print("✅ PDF sent to WhatsApp group.")
    except Exception as e:
        print(f"❌ Error sending PDF to WhatsApp group. Please check if the group name is correct and you are logged in to WhatsApp Web. Error: {e}")
        try:
            if first_tab:
                browser_utils.close_whatsapp_driver()
        except:
            print("❌ Failed to close the browser config.whatsapp_driver. Something really went wrong.")