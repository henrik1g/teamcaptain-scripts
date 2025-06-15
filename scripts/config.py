import os

# =========================
# General Configuration
# =========================

# Competition name (should match name used for metbrief folder, otherwise update below.)
comp_name = "tabor_25"

# Base URL for SoaringSpot event
base_url = 'https://www.soaringspot.com/en_gb/39th-fai-world-gliding-championships-tabor-2025'

# =========================
# Competition Classes & Mappings
# =========================

# List of competition classes
classes = ['Club', 'Standard', '15 Meter']

# Mapping from class name to file prefix (these are the names that files for classes will receive in the /data/.. path)
filename_map = {
    'Club': 'club',
    'Standard': 'std',
    '15 Meter': '15m'
}

# Mapping from class name to URL segment on SoaringSpot (check URL when looking at a task to update)
url_map = {
    'Club': 'club',
    'Standard': 'standard',
    '15 Meter': '-15-meter'
}

# Mapping from class name to SoaringSpot results table name (input names written the the results table on SoaringSpot)
results_table_map = {
    'Club': 'Club Class',
    'Standard': 'Standard Class',
    '15 Meter': '15 meter Class'
}

# =========================
# WhatsApp Integration
# =========================

# Default WhatsApp message to send with the weather briefing
whatsapp_message = "Chatty ist der Beste! Hier ist die heutige Wettervorhersage für Tabor 2025."

# WhatsApp group name to send the weather briefing to (Emojis are not allowed in the string here, but may be included in the actual group name! Looking for the closes match!)
#whatsapp_group = 'Piloten WGC Tabor'
whatsapp_group = 'Ich mache hier nur Notize'

# WhatsApp timeout for sending the message. This is the time the app waits between adding the presentation to the chat and closing the window
# Increase time if internet connection is weak or file is large
whatsapp_timeout = 30
whatsapp_group_send_time = 15

# =========================
# Git, Browser, and LibreOffice Settings
# =========================

# Path to github repo
github_path = "nilsschlautmann/wgc2025"

# Set up your git credentials if not already configured
os.environ['GIT_SSH_COMMAND'] = 'ssh -i ~/.ssh/id_rsa'

# Path to the LibreOffice executable (adjust if needed)
soffice_path = r"C:\Program Files\LibreOffice\program\soffice.exe"

# scripts/config.py
browser = "firefox"  # "chrome" or "firefox" 

# =========================
# File Locations
# =========================

# Path to the file containing URLs to open in Chrome
url_file = 'data/urls.txt'

# Path to the Excel database file (pilot, glider, etc.)
database_path = "data/database.xlsx"  # Adjust the path if needed

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
firefoxdriver_user_data_dir = 'data/.firefoxdriver_user_data'

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