# Import necessary libraries
from scripts import config
from xml.etree.ElementTree import Element, SubElement, ElementTree, tostring
from bs4 import BeautifulSoup
from xml.dom import minidom
import numpy as np
import requests
import json
import html
import os
import re

# Get all available task IDs for a given class
def get_class_task_ids(class_name):
    url_comp_results = f'{config.base_url}/results'
    soup = BeautifulSoup(requests.get(url_comp_results).text, "html.parser")
    result_class_all = soup.find_all('table', class_='result-overview')
    task_ids = []
    pattern = re.compile(r'(daily|practice|task)-\d+-on-\d{4}-\d{2}-\d{2}')
    for comp_class in result_class_all:
        classURL = config.results_table_map.get(class_name, False)
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

# Select task IDs for each class
def select_task_ids():
    print("\n⚙️  Selecting task IDs for each class...")
    config.selected_task_ids = {}
    for class_name in config.classes:
        all_task_ids, latest_task_id = get_class_task_ids(class_name)
        print(f"\n📋 Available task IDs for {class_name}:")
        for idx, tid in enumerate(all_task_ids):
            print(f"\t{idx+1}: {tid}")
        sel = input(f"❓ Select task ID for {class_name} (1-{len(all_task_ids)}) [default: latest]: ").strip()
        if sel.isdigit() and 1 <= int(sel) <= len(all_task_ids):
            config.selected_task_ids[class_name] = all_task_ids[int(sel)-1]
        else:
            config.selected_task_ids[class_name] = latest_task_id
        print(f"\t✅ Selected task ID for {class_name}: {config.selected_task_ids[class_name]}")

# Function to return the latest task IDs for each class
def return_latest_task_ids_for_classes():
    latest_task_ids = {}
    for class_name in config.classes:
        _, latest_task_id = get_class_task_ids(class_name)
        latest_task_ids[class_name] = latest_task_id
    return latest_task_ids

# Fetch task data for a given class from SoaringSpot
def fetch_task_data(class_name):
    task_id = config.selected_task_ids[class_name]
    print(f"\t\t🔍 Fetching task data with task_id '{task_id}'")
    classURL = config.url_map.get(class_name, False)
    if not classURL:
        print(f"\t❌ No URL mapping found")
        return None
    
    url = f"{config.base_url}/tasks/{classURL}/{task_id}"
    
    response = requests.get(url)
    if response.status_code != 200:
        print(f"\t❌ Failed to fetch {url} (HTTP {response.status_code})")
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
        print(f"\t❌ taskData not found")
        return None

    # Extract the JSON data from the script tag
    script_content = script_tag.string
    match = re.search(r'var taskData = Map\.SoaringSpot\.taskNormalize\((\{.*?\})\);', script_content, re.DOTALL)
    if not match:
        print(f"\t❌ taskData JSON not found in script")
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
        print(f"\t❌ JSON parsing error: {e}")
        return None

# Create a waypoint element in the XML structure for the .tsk file
def create_waypoint(parent, point):
    point_type = point['type'].capitalize() if point['type'] != 'point' else 'Turn'
    point_elem = SubElement(parent, 'Point', type=point_type)
    wp_elem = SubElement(point_elem, 'Waypoint', altitude=str(point['elevation']), name=point['name'])
    SubElement(wp_elem, 'Location', latitude=str(np.rad2deg(point['latitude'])), longitude=str(np.rad2deg(point['longitude'])))
    
    if point_type == 'Start':
        SubElement(point_elem, 'ObservationZone', length=str(2*point['oz_radius1']), type="Line")
    else:
        SubElement(point_elem, 'ObservationZone', radius=str(point['oz_radius1']), type="Cylinder")

# Create and save a task .tsk file from the fetched soaringspot .json data
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
    filename = config.filename_map.get(class_name, class_name)
    filepath = os.path.join(config.task_output_dir, f"{config.comp_name}_{filename}.tsk")
    with open(filepath, "w", encoding='utf-8') as f:
        f.write(pretty_xml_no_decl)
    print(f"\t\t✅ Saved .tsk task file at '{filepath.replace(os.sep, '/')}'")
   
# Convert the original soaringspot .json data to a .json format that glideandseek expects
def convert_soaringspot_json_to_glideandseek_json(json_data):
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

        points.append(point)
    return {
        "type": task_type,
        "points": points
    }

# Create and save a task .json file from the fetched data
def create_task_json_file(soaringspot_json_data, class_name):
    filename = config.filename_map.get(class_name, class_name)
    filepath = os.path.join(config.task_output_dir, f"{config.comp_name}_{filename}.json")
    
    json_data = convert_soaringspot_json_to_glideandseek_json(soaringspot_json_data)
    if not json_data:
        print(f"\t❌ Failed to convert JSON data for {class_name}")
        return
    
    with open(filepath, "w", encoding='utf-8') as f:
        json.dump(json_data, f, indent=4)
    
    print(f"\t\t✅ Saved .json task file at '{filepath.replace(os.sep, '/')}'")

# Create a task .cup file from the fetched data (using the weglide URL which takes care of this task)
def create_task_cup_file(class_name):
    classURL = config.url_map.get(class_name, False)
    task_id = config.selected_task_ids[class_name]
    full_url = f"{config.cup_url}{config.base_url}/tasks/{classURL}/{task_id}"
    print(f"\t\t📄 Creating .cup task file")

    response = requests.get(full_url)
    if response.status_code == 200:
        filename = config.filename_map.get(class_name, class_name)
        filepath = os.path.join(config.task_output_dir, f"{config.comp_name}_{filename}.cup")
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"\t\t✅ Saved .cup task file at '{filepath.replace(os.sep, '/')}'")
    else:
        print(f"\t❌ Failed to download .cup task file (status code: {response.status_code})")

# Update task files for all classes
def update_task_files():
    print("⚙️  Updating task files...")
    for class_name in config.classes:
        print(f"\t⚙️  Updating task files for class: {class_name}")
        # Create task files for each class
        task_data = fetch_task_data(class_name)
        if task_data:
            soaringspot_json_data = extract_json_from_html(task_data)
            create_task_json_file(soaringspot_json_data, class_name)
            create_task_tsk_file(soaringspot_json_data, class_name)
            create_task_cup_file(class_name)

