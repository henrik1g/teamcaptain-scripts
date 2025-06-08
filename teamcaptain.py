import os
import requests
from bs4 import BeautifulSoup
import json
import re
import html
import numpy as np
import pandas as pd
import csv
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, ElementTree, tostring
import subprocess
import webbrowser
from git import Repo, GitCommandError
import sys
import re
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import psutil
import time

# --- CONFIG ---
base_url = 'https://www.soaringspot.com/en_gb/39th-fai-world-gliding-championships-tabor-2025'
url_file = 'data/urls.txt'
whatsappMessage = "Chatty ist der Beste! Hier ist die aktuelle Wettervorhersage für Tabor 2025."
whatsAppGroup = 'Ich mache hier nur Notize'  # WhatsApp group name to send the weather briefing to
weatherBriefingPath = os.path.join('externals', 'metbrief', 'briefings', 'tabor_25')  # Competition name for weather briefing (as used in metbrief.py)

# TODO: Set up your git credentials if not already configured. Create ssh config file
os.environ['GIT_SSH_COMMAND'] = 'ssh -i ~/.ssh/id_rsa'
soffice_path = r"C:\Program Files\LibreOffice\program\soffice.exe" # Adjust this path if needed (libreoffice path)

# Output directories for tasks and gliders
task_output_dir = 'data/tasks'
glider_output_dir = 'data/gliders'
chromedriver_user_data_dir = 'data/.chromedriver_user_data'

# Load the Excel file
database = "data/database.xlsx"  # Adjust the path if needed


# Url for downloading .cup files from SoaringSpot links
cupURL = 'https://xlxjz3geasj4wiei7n5vzt7zzu0qibmm.lambda-url.eu-central-1.on.aws/?url='

# Classes to fetch tasks for
classes = ['Club', 'Standard', '15 Meter']

# Mapping from class names to desired filenames (.txt, .tsk, etc.)
filename_map = {
    'Club': 'club',
    'Standard': 'std',
    '15 Meter': '15m'
}

# Mapping from class names to soaringspot URLs
url_map = {
    'Club': 'club',
    'Standard': 'standard',
    '15 Meter': '-15-meter'
}

resultstable_map = {
    'Club': 'Club Class',
    'Standard': 'Standard Class',
    '15 Meter': '15 meter Class'
}

# Get the latest task IDs for each class
def get_task_ids(class_name):
    url_comp_results = f'{base_url}/results'
    soup = BeautifulSoup(requests.get(url_comp_results).text, "html.parser")
    result_class_all = soup.find_all('table', class_='result-overview')
    task_ids = []
    pattern = re.compile(r'(daily|practice|task)-\d+-on-\d{4}-\d{2}-\d{2}')
    for comp_class in result_class_all:
        classURL = resultstable_map.get(class_name, False)
        if classURL not in str(comp_class.contents[1]):
            continue
        for element in comp_class.find_all('tr'):
            for url in element.find_all('a'):
                href = url.get('href', '')
                match = pattern.search(href)
                if match:
                    task_id = match.group(0)
                    if task_id not in task_ids:
                        task_ids.append(task_id)

    # Sort by date (assuming format ...on-YYYY-MM-DD)
    task_ids_sorted = sorted(task_ids, key=lambda x: x.split('-on-')[-1])
    latest = task_ids_sorted[-1] if task_ids_sorted else None
    return task_ids_sorted, latest

# Prompt user for task ID selection
def select_task_id_for_classes():
    choice = input("\n❓ Do you want to select latest task IDs? (default is latest, select specific IDs if N) (Y/N)?").strip().lower()
    selected_task_ids = {}

    if choice == "y":
        for class_name in classes:
            _, latest_task_id = get_task_ids(class_name)
            selected_task_ids[class_name] = latest_task_id
    elif choice == "n":
        for class_name in classes:
            all_task_ids, latest_task_id = get_task_ids(class_name)
            print(f"\n📋 Available task IDs for {class_name}:")
            for idx, tid in enumerate(all_task_ids):
                print(f"\t{idx+1}: {tid}")
            sel = input(f"❓ Select task ID for {class_name} (1-{len(all_task_ids)}) [default: latest]: ").strip()
            if sel.isdigit() and 1 <= int(sel) <= len(all_task_ids):
                selected_task_ids[class_name] = all_task_ids[int(sel)-1]
            else:
                selected_task_ids[class_name] = latest_task_id
    else:
        print("ℹ️  Invalid choice, using latest for all classes.")
        for class_name in classes:
            _, latest_task_id = get_task_ids(class_name)
            selected_task_ids[class_name] = latest_task_id

    return selected_task_ids

# Function to return the latest task IDs for each class
def return_latest_task_ids_for_classes():
    latest_task_ids = {}
    for class_name in classes:
        _, latest_task_id = get_task_ids(class_name)
        latest_task_ids[class_name] = latest_task_id
    return latest_task_ids

# Fetch task data for a given class from SoaringSpot
def fetch_task_data(class_name):
    task_id = selected_task_ids[class_name]
    print(f"\t🔍 Fetching task data with task_id '{task_id}'")
    classURL = url_map.get(class_name, False)
    if not classURL:
        print(f"\t\t❌ No URL mapping found")
        return None
    
    url = f"{base_url}/tasks/{classURL}/{task_id}"
    
    response = requests.get(url)
    if response.status_code != 200:
        print(f"\t\t❌ Failed to fetch {url} (HTTP {response.status_code})")
        return None
    else:
        return response

# Extract JSON data from the HTML response for a given class
def extract_json_from_html(html_response):
    print(f"\t\t📄 Creating .json file")

    # Parse the HTML response to find the task data
    soup = BeautifulSoup(html_response.content, 'html.parser')
    script_tag = soup.find('script', string=re.compile(r'var taskData'))
    if not script_tag:
        print(f"\t\t❌ taskData not found")
        return None

    # Extract the JSON data from the script tag
    script_content = script_tag.string
    match = re.search(r'var taskData = Map\.SoaringSpot\.taskNormalize\((\{.*?\})\);', script_content, re.DOTALL)
    if not match:
        print(f"\t\t❌ taskData JSON not found in script")
        return None

    # Extract the JSON string and clean it up
    raw_str = match.group(1).strip()
    end_idx = raw_str.find(', [{')  # Find where first object ends
    if end_idx != -1:
        raw_str = raw_str[:end_idx]  # Keep only the first JSON object    
    json_str = html.unescape(raw_str)
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"\t\t❌ JSON parsing error: {e}")
        return None

# Create and save a task .tsk file from the fetched data
def create_task_tsk_file(json_data, class_name):
    print(f"\t\t📄 Creating .tsk file")
    if str(json_data['task_type']) == 'assigned_area':
        task = Element('Task', aat_min_time=str(json_data['task_duration']), type='AAT')
    else:
        task = Element('Task', type='RT')

    for point in json_data.get('task_points', []):
        create_waypoint(task, point)
            
    # Instead of the above, use this:
    rough_string = tostring(task, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")
    pretty_xml_no_decl = '\n'.join(pretty_xml.split('\n')[1:])  # remove the first line

    # Save to file
    filename = filename_map.get(class_name, class_name)
    filepath = os.path.join(task_output_dir, f"{filename}.tsk")
    with open(filepath, "w", encoding='utf-8') as f:
        f.write(pretty_xml_no_decl)
    print(f"\t\t✅ Saved .tsk task file at '{filepath.replace(os.sep, '/')}'")

# Create a waypoint element in the XML structure for the .tsk file
def create_waypoint(parent, point):
    point_type = point['type'].capitalize() if point['type'] != 'point' else 'Turn'
    point_elem = SubElement(parent, 'Point', type=point_type)
    wp_elem = SubElement(point_elem, 'Waypoint', altitude=str(point['elevation']), name=point['name'])
    SubElement(wp_elem, 'Location', latitude=str(np.rad2deg(point['latitude'])), longitude=str(np.rad2deg(point['longitude'])))
    
    if point_type == 'Start':
        SubElement(point_elem, 'ObservationZone', length=str(point['oz_radius1']), type="Line")
    else:
        SubElement(point_elem, 'ObservationZone', radius=str(point['oz_radius1']), type="Cylinder")
   
# Create and save a task .json file from the fetched data
def create_task_json_file(soaringspot_json_data, class_name):
    filename = filename_map.get(class_name, class_name)
    filepath = os.path.join(task_output_dir, f"{filename}.json")
    
    json_data = convert_json_to_glideandseek_format(soaringspot_json_data)
    if not json_data:
        print(f"\t\t❌ Failed to convert JSON data for {class_name}")
        return
    
    with open(filepath, "w", encoding='utf-8') as f:
        json.dump(json_data, f, indent=4)
    
    print(f"\t\t✅ Saved .json task file at '{filepath.replace(os.sep, '/')}'")

def convert_json_to_glideandseek_format(json_data):
    # Map task type
    task_type = "AAT" if str(json_data.get("task_type")) == "assigned_area" else "RT"
    points = []
    for pt in json_data.get("task_points", []):
        # Convert radians to degrees for lat/lng
        lat = np.rad2deg(pt["latitude"])
        lng = np.rad2deg(pt["longitude"])
        # Map type
        if pt["type"].lower() == "start":
            point_type = "Next"
        elif pt["type"].lower() == "finish":
            point_type = "Cylinder"
        elif task_type == "AAT":
            point_type = "AAT Sector"
        else:
            point_type = "Symmetric"
        # Build point dict
        point = {
            "type": point_type,
            "name": pt["name"],
            "altitude": float(pt["elevation"]),
            "lat": float(lat),
            "lng": float(lng),
            "radius": int(pt["oz_radius1"])
        }
        # Optional fields
        #if "oz_angle1" in pt:
        #    point["angle"] = int(np.rad2deg(pt["oz_angle1"]))
        #if point_type == "Symmetric" and "oz_radius2" in pt and pt["oz_radius2"]:
        #    point["cylinder"] = int(pt["oz_radius2"])
        points.append(point)
    return {
        "type": task_type,
        "points": points
    }

# Create a task .cup file from the fetched data
def create_task_cup_file(class_name):
    classURL = url_map.get(class_name, False)
    task_id = selected_task_ids[class_name]
    full_url = f"{cupURL}{base_url}/tasks/{classURL}/{task_id}"
    print(f"\t\t📄 Creating .cup task file")

    response = requests.get(full_url)
    if response.status_code == 200:
        filename = filename_map.get(class_name, class_name)
        filepath = os.path.join(task_output_dir, f"{filename}.cup")
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"\t\t✅ Saved .cup task file at '{filepath.replace(os.sep, '/')}'")
    else:
        print(f"\t\t❌ Failed to download .cup task file (status code: {response.status_code})")

# Create task files for each class
def create_task_files(class_name):
    task_data = fetch_task_data(class_name)
    if task_data:
        soaringspot_json_data = extract_json_from_html(task_data)
        create_task_json_file(soaringspot_json_data, class_name)
        create_task_tsk_file(soaringspot_json_data, class_name)
        create_task_cup_file(class_name)
    
def create_glider_txt_file(class_name):
    print(f"\t\t📄 Creating glider .txt file")
    filename = filename_map.get(class_name, "all")
    filepath = os.path.join(glider_output_dir, f"{filename}.txt")
    
    df = pd.read_excel(database, sheet_name='WGC2025')

    # Ensure all needed columns exist
    required_cols = ['COMP', 'Name', 'Flag', 'FlarmID']
    if not all(col in df.columns for col in required_cols):
        raise ValueError("One or more required columns are missing in the Excel sheet.")

    # Drop rows where any required column is missing (i.e., end of table or incomplete rows)
    df = df.dropna(subset=['Name'])

    if filename != 'all':
        df = df[df['Class'].isin([class_name])]

    # Replace NaN with empty string for relevant columns
    df[['FlarmID', 'COMP', 'Flag', 'Name']] = df[['FlarmID', 'COMP', 'Flag', 'Name']].fillna('')
    
    # Build the string using the specified format
    df['String'] = df.apply(lambda row: f"{row['FlarmID']},,{row['COMP']},{row['Flag'] + ' ' if row['Flag'] else ''}{row['Name']}", axis=1)

    # Write lines manually to avoid any escaping
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("ID,CALL,CN,TYPE,NAME\n")
        for line in df['String']:
            f.write(f"{line}\n")
    
    # Save only the "String" column to a .txt file
    #df['String'].to_csv(filepath, index=False, header=False, quoting=csv.QUOTE_NONE, escapechar='\\')

    print(f"\t\t✅ Saved .txt glider file at '{filepath.replace(os.sep, '/')}'")

# Create a glider .json file from the .txt file
def create_glider_json_file(class_name):
    print(f"\t\t📄 Creating glider .json file")
    filename = os.path.join(glider_output_dir, f"{filename_map.get(class_name, 'all')}.txt")
    outputfilename = filename.replace(".txt", ".json")
    # read as csv with ID,CALL,CN,TYPE,NAME
    lines = []
    with open(filename, "r" ,encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            lines.append(row[0].split(","))

        with open(outputfilename, "w" ,encoding="utf-8") as f:
            json.dump(
                [
                    {
                        "name": line[4] if len(line) > 4 else "",
                        "cn": line[2] if len(line) > 2 else "",
                        "glider": "",
                        "comp": line[2] if len(line) > 2 else "",
                        "flarm": [line[0]] if len(line) > 0 else "",
                    }
                    for line in lines[1:]
                ],
                f,
                indent=4,
            )
    print(f"\t\t✅ Saved .json glider file at '{outputfilename.replace(os.sep, '/')}'")

def create_glider_files(class_name):
    print(f"\t🔍 Fetching glider data")
    create_glider_txt_file(class_name)
    create_glider_json_file(class_name)

def commit_and_push_task_and_glider_files():
    answer = input("\n❓ Do you want to commit and push all changes to task and glider files? [Y/N]: ").strip().lower()
    if answer == "y":
        try:
            repo = Repo(os.getcwd())
            repo.git.add(["data/"])
            if repo.is_dirty(index=True, working_tree=False, untracked_files=False):
                print(f"⚙️  Committing task and glider files")
                repo.index.commit("Update tasks and gliders")
                origin = repo.remote(name='origin')
                origin.push()
                print("✅ Changes committed and pushed successfully.")
            else:
                print("ℹ️  No changes to commit.")
        except GitCommandError as e:
            print(f"❌ Commit or push failed: {e}")
    else:
        print(f"ℹ️  No changes were committed or pushed.")

def open_chrome(userData, runHeadless):
    # Close previous Chrome instances with the same user data directory
    close_chrome_with_userdata(chromedriver_user_data_dir)

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--new-window")  # Open in a new window
    chrome_options.add_experimental_option("detach", True)  # <-- This keeps Chrome open
    chrome_options.add_argument("--log-level=3")  # Suppress most Chrome logs
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])  # Suppress DevTools and other logs
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--disable-gpu")  # Sometimes helps with GPU-related warnings

    # Add user data directory if provided
    if userData not in [None, ""]:
        chrome_options.add_argument("user-data-dir=" + os.path.join(os.path.dirname(sys.argv[0]), userData))  # Use a custom user data directory

    # Check if running headless
    if runHeadless == True:
        # If running headless, add the headless argument
        chrome_options.add_argument("--headless")
        
    driver = webdriver.Chrome(options=chrome_options)
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

# Function to open a URL in Chrome, handling the first tab differently
def open_tab_in_chrome(driver, url, first_tab):
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
def open_chrome_tabs_from_file():
    # Open Chrome and load URLs from the file
    driver = open_chrome(None, False)  # Set to True if you want to run in headless mode

    with open(url_file, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]

    first_tab = True
    for url in urls:
        if "{taskID}" in url or "{classURL}" in url or "{classFile}" in url:
            for class_name in classes:
                task_id = selected_task_ids.get(class_name, False)
                classURL = url_map.get(class_name, False)
                fileURL = filename_map.get(class_name, False)
                url_filled = url.replace("{taskID}", task_id)
                url_filled = url_filled.replace("{classURL}", classURL)
                url_filled = url_filled.replace("{classFile}", fileURL)
                first_tab = open_tab_in_chrome(driver, url_filled, first_tab)
        else:
            first_tab = open_tab_in_chrome(driver, url, first_tab)

# Get the folgder path for the latest weather briefing
def get_latest_weather_briefing_folderPath():
    today = datetime.date.today().strftime('%m%d')
    folderPath = os.path.join(weatherBriefingPath, today)
    return os.path.normpath(folderPath)

# Get the full path of the latest weather briefing file
def get_latest_weather_briefing_fullPath():
    today = datetime.date.today().strftime('%m%d')
    fullFilepath = os.path.join(get_latest_weather_briefing_folderPath(), str(today) + "_" + str(os.path.basename(weatherBriefingPath)) + ".odp")
    return fullFilepath

# Function to open the latest weather briefing
def open_latest_weather_briefing():
    # Open the latest weather briefing
    filepath = get_latest_weather_briefing_folderPath()
    fullFilepath = get_latest_weather_briefing_fullPath()
    if os.path.exists(filepath):
        open_in_libreoffice(fullFilepath)
    else:
        print("❌ Latest weather briefing not found. Please generate it first.")

def open_in_libreoffice(filepath):
    try:
        subprocess.Popen([soffice_path, "--impress", filepath])
    except Exception as e:
        print(f"❌ Could not open file in LibreOffice: {e}")

def convert_odp_to_pdf(odp_path):
    output_dir = os.path.dirname(odp_path)
    try:
        subprocess.run([
            soffice_path, "--headless", "--convert-to", "pdf", odp_path, "--outdir", output_dir
        ], check=True)
        pdf_path = odp_path.replace('.odp', '.pdf')
        if os.path.exists(pdf_path):
            print(f"✅ PDF created at {pdf_path}")
            return pdf_path
        else:
            print("❌ PDF conversion failed.")
            return None
    except Exception as e:
        print(f"❌ PDF conversion error: {e}")
        return None

def send_pdf_to_whatsapp_group(group_name, message, pdf_path):
    driver = open_chrome(chromedriver_user_data_dir, True)  # Set to True if you want to run in headless mode
    driver.get("https://web.whatsapp.com/")
    time.sleep(10)

    # Search for the group
    search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
    search_box.click()
    search_box.send_keys(group_name)
    time.sleep(2)
    group = driver.find_element(By.XPATH, f'//span[@title="{group_name}"]')
    group.click()
    time.sleep(1)

    # Attach file
    attach_btn = driver.find_element(By.CSS_SELECTOR, "span[data-icon='plus-rounded']")
    attach_btn.click()
    time.sleep(1)
    file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
    file_input.send_keys(os.path.abspath(pdf_path))
    time.sleep(2)

    # Prompt for a message
    # Find the message input box and send the message
    msg_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@aria-placeholder="Add a caption"]')
    msg_box.click()
    msg_box.send_keys(message)
    msg_box.send_keys(u'\ue007')  # Press Enter

    print("✅ PDF sent to WhatsApp group.")
    time.sleep(5)
    driver.quit()

# Function to send the weather briefing to a WhatsApp group
def send_weather_briefing_to_whatsapp(group_name, message):
    odp_path = get_latest_weather_briefing_fullPath()
    if not os.path.exists(odp_path):
        print("❌ ODP file not found.")
        return
    pdf_path = convert_odp_to_pdf(odp_path)
    if pdf_path:
        send_pdf_to_whatsapp_group(group_name, message, pdf_path)

# --- MAIN LOOP ---
# TODO Make output directories if not exist
if not os.path.exists(task_output_dir):
    os.makedirs(task_output_dir)
if not os.path.exists(glider_output_dir):
    os.makedirs(glider_output_dir)

# Print a welcome message
print("⚙️  Welcome to the Team Captain Script!")

# --- TASK AND GLIDER FILES ---
# Ask user if they want to update task and glider files
choice = input("\n❓ Do you want to update the task and glider files? (Y/N)?").strip().lower()

if choice == "y":
    # Prompt user for task ID selection
    selected_task_ids = select_task_id_for_classes()

    # Iterate over each class and create task and glider files
    for class_name in classes:
        print(f"\n⚙️  Processing class: {class_name}")
        create_task_files(class_name)
        create_glider_files(class_name)

    # Create glider files for all classes combined
    print(f"\n⚙️  Processing for all classes combined")
    create_glider_files('all')  # Create a glider file for all classes combined

    # Commit and push task and glider files
    commit_and_push_task_and_glider_files()
elif choice == "n": 
    selected_task_ids = return_latest_task_ids_for_classes()
    print("ℹ️  Skipping task and glider file updates.")
else:
    selected_task_ids = return_latest_task_ids_for_classes()
    print('ℹ️  Invalid choice, skipping task and glider file updates.')

# --- WEATHER BRIEFING ---
# Ask user if they want to create a weather briefing
choice = input("\n❓ Do you want to create/update the weather briefing? (Y/N)?").strip().lower()
if choice == "y":
    # Ensure the metbrief.py script exists
    metbrief_script = os.path.join("externals", "metbrief", "metbrief.py")
    if not os.path.exists(metbrief_script):
        print(f"❌ metbrief.py script not found at '{metbrief_script}'. Please ensure it exists.")
    else:
        #Create the weather briefing
        print(f"⚙️  Creating weather briefing")
        # Call metbrief.py
        try:
            subprocess.run(
                ["python", "metbrief.py"],
                cwd="externals/metbrief",
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("✅ Weather briefing created successfully.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Weather briefing creation failed (exit code {e.returncode}).")
elif choice == "n": 
    print("ℹ️  Skipping weather briefing creation.")
else:
    print('ℹ️  Invalid choice, skipping weather briefing creation.')

# --- OPEN CHROME TABS ---
choice = input("\n❓ Do you want to open tabs from the URL file and the latest weather briefing? (Y/N)?").strip().lower()

if choice == "y":
    # Ensure the URL file exists
    if not os.path.exists(url_file):
        print(f"❌ URL file '{url_file}' does not exist. Skipping opening tabs and latest weather briefing.")
    else:
        # Open Chrome tabs from the URL file
        print(f"⚙️  Opening tabs from URL file and latest weather briefing")
        open_chrome_tabs_from_file()
        open_latest_weather_briefing()
elif choice == "n":
    print("ℹ️  Skipping opening tabs and latest weather presentation.")
else:   
    print('ℹ️  Invalid choice, skipping opening tabs and latest weather presentation.')

# Send latest weather briefing via WhatsappWeb

# --- OPEN CHROME TABS ---
choice = input("\n❓ Do you want to send the weather briefing to the WhatsApp Group? (Y/N)?").strip().lower()

if choice == "y":
    # Open Chrome tabs from the URL file
    print(f"⚙️  Sending latest weather briefing to WhatsApp group '{whatsAppGroup}'")
    send_weather_briefing_to_whatsapp(whatsAppGroup, whatsappMessage)
elif choice == "n":
    print("ℹ️  Skipping sending weather briefing to WhatsApp group.")
else:   
    print('ℹ️  Invalid choice, skipping sending weather briefing to WhatsApp group.')
# --- END OF MAIN LOOP ---
# --- END OF SCRIPT ---