import os

# =========================
# General Configuration
# =========================

# Competition name (should match name used for metbrief folder, otherwise update below.)
comp_name = "SSM_2025"

# Base URL for SoaringSpot event
base_url = ' https://www.soaringspot.com/en_gb/suddeutsche-segelflugmeisterschaft-neresheim-2025'
# =========================
# Competition Classes & Mappings
# =========================

# List of competition classes
#classes = ['Club', 'Standard']
classes = ['Renn', 'Standard']

# Mapping from class name to file prefix (these are the names that files for classes will receive in the /data/.. path)
filename_map = {
#    'Club': 'club',
    'Renn': '15m',
    'Standard': 'std',
}

# Mapping from class name to URL segment on SoaringSpot (check URL when looking at a task to update)
url_map = {
#    'Club': 'unknown',
    'Renn': 'unknown',
    'Standard': 'standardklasse',
}

# Mapping from class name to SoaringSpot results table name (input names written the the results table on SoaringSpot)
results_table_map = {
    'Renn': 'Rennklasse',
    'Standard': 'Standardklasse',
}

# =========================
# WhatsApp Integration
# =========================

# Default WhatsApp message to send with the weather briefing
whatsapp_message = "Chatty ist der Beste! Hier ist die heutige Wettervorhersage für Neresheim2025."

# WhatsApp group name to send the weather briefing to (Emojis are not allowed in the string here, but may be included in the actual group name! Looking for the closes match!)
whatsapp_group = 'SSM25'

# WhatsApp timeout for sending the message. This is the time the app waits between adding the presentation to the chat and closing the window
# Increase time if internet connection is weak or file is large
whatsapp_timeout = 30
whatsapp_group_send_time = 15

# =========================
# Git, Browser, and LibreOffice Settings
# =========================

# Path to github repo
github_path = "henrik1g/teamcaptain-scripts"

# Set up your git credentials if not already configured
os.environ['GIT_SSH_COMMAND'] = 'ssh -i ~/.ssh/id_rsa'

# Path to the LibreOffice executable (adjust if needed)
soffice_path = r"/usr/bin/libreoffice"

# scripts/config.py
browser = "firefox"  # "chrome" or "firefox" 

# =========================
# File Locations
# =========================

# Path to the file containing URLs to open in Chrome
url_file = 'data/urls.txt'

# Path to the Excel database file (pilot, glider, etc.)
database_path = "data/Database.xlsx"

# =========================
# Weather Briefing Settings
# =========================

# Path to the weather briefing folder (used by metbrief.py)
weather_briefing_path = os.path.join('externals', 'metbrief', 'briefings', comp_name)

# =========================
# Output Directories
# =========================

# Directory for generated task files
task_output_dir = 'data/tasks'

# Directory for generated glider files
glider_output_dir = 'data/gliders'

# Directory for Chrome user data (used by Selenium)
chromedriver_user_data_dir = 'data/.chromedriver_user_data'

# Directory for Chrome user data (used by Selenium)
firefoxdriver_user_data_dir = '/home/henrik/.mozilla/firefox/wnytyd2d.TC_JEGC'

# =========================
# SoaringSpot & CUP Download
# =========================

# URL for downloading .cup files from SoaringSpot links
cup_url = 'https://xlxjz3geasj4wiei7n5vzt7zzu0qibmm.lambda-url.eu-central-1.on.aws/?url='

# =========================
# Shared State Variables
# =========================

# Dictionary to store selected task IDs for each class
selected_task_ids = {}

# Whether to automatically commit and push to git after updates
commit_and_push_to_git = True

# UserData Driver (there can only be one in chrome)
whatsapp_driver = None

# All browser drivers
all_drivers = []
