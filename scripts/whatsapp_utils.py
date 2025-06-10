# Import necessary libraries
from scripts import chrome_utils
from scripts import config
from scripts import utils
from selenium.webdriver.common.by import By
import os
import time

# Function to send the latest weather briefing PDF to a WhatsApp group
def send_pdf_to_whatsapp_group(pdf_path):
    print(f"⚙️  Sending latest weather briefing to WhatsApp group '{config.whatsapp_group}'")
    try:
        
        if config.driver == None:
            config.driver = chrome_utils.open_chrome(config.chromedriver_user_data_dir, False)
            first_tab = True
        else:
            first_tab = False

        url = "https://web.whatsapp.com/"
        chrome_utils.open_tab(config.driver, url, first_tab)
        # Switch to the newest tab
        config.driver.switch_to.window(config.driver.window_handles[-1])

        # Wait for WhatsApp Web to load (minimized sleep, responsive)
        search_box = utils.wait_for_element(config.driver, By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]', timeout=30, poll_frequency=0.2)
        if not search_box:
            print("❌ WhatsApp Web did not load properly. Please check your internet connection and try again.")
            if first_tab:
                config.driver.quit()
            return

        search_box.click()
        search_box.send_keys(config.whatsapp_group)
        # Wait for chats to load
        time.sleep(1)

        # Re-find all chat titles after the DOM update
        chat_spans = config.driver.find_elements(By.XPATH, '//span[@title]')
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
            print(f"❌ Could not find WhatsApp group containing '{search_substring}'.")
            if first_tab:
                config.driver.quit()
            return
        group.click()

        # Attach file
        attach_btn = utils.wait_for_element(config.driver, By.CSS_SELECTOR, "span[data-icon='plus-rounded']", timeout=10, poll_frequency=0.2)
        if not attach_btn:
            print("❌ Could not find attach button.")
            if first_tab:
                config.driver.quit()
            return
        attach_btn.click()

        file_input = utils.wait_for_element(config.driver, By.CSS_SELECTOR, "input[type='file']", timeout=5, poll_frequency=0.2)
        if not file_input:
            print("❌ Could not find file input.")
            if first_tab:
                config.driver.quit()
            return
        file_input.send_keys(os.path.abspath(pdf_path))

        # Message input (caption)
        msg_box = utils.wait_for_element(config.driver, By.XPATH, '//div[@contenteditable="true"][@aria-placeholder="Add a caption"]', timeout=5, poll_frequency=0.2)
        if not msg_box:
            print("❌ Could not find message input box.")
            if first_tab:
                config.driver.quit()
            return
        msg_box.click()
        msg_box.send_keys(config.whatsapp_message)
        msg_box.send_keys(u'\ue007')  # Press Enter

        # Wait for the message to be sent
        time.sleep(config.whatsapp_wait)  # Wait for a few seconds to ensure the message is sent
        if not first_tab:
            config.driver.close()
            # Switch back to the last remaining tab (if any)
            if config.driver.window_handles:
                config.driver.switch_to.window(config.driver.window_handles[-1])
        else:
            config.driver.quit()
        print("✅ PDF sent to WhatsApp group.")
    except Exception as e:
        print(f"❌ Error sending PDF to WhatsApp group. Please check if the group name is correct and you are logged in to WhatsApp Web. Error: {e}")
        try:
            if first_tab:
                config.driver.quit()
        except:
            print("❌ Failed to close the browser config.driver. Something really went wrong.")