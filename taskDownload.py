import requests
from bs4 import BeautifulSoup
import json
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
import re

# URL der Webseite
url = 'https://www.soaringspot.com/en_gb/jwgc2024/tasks/club/task-2-on-2024-07-15'

# Sende eine GET-Anfrage an die Webseite
response = requests.get(url)

# Überprüfe den Statuscode der Antwort
if response.status_code == 200:
    # Verarbeite den Quelltext der Seite
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Finde das Script-Tag, das die taskData-Variable enthält
    script_tag = soup.find('script', string=re.compile(r'var taskData'))
    
    if script_tag:
        # Extrahiere den Inhalt des Script-Tags
        script_content = script_tag.string
        
        # Finde den JSON-Teil der taskData-Variable mit einem regulären Ausdruck
        json_data_match = re.search(r'var taskData = Map\.SoaringSpot\.taskNormalize\((\{.*?\})\);', script_content, re.DOTALL)
        
        if json_data_match:
            # Extrahiere den JSON-String aus dem Match-Objekt
            json_data_str = json_data_match.group(1)
            
            # Bereinige den JSON-String von eventuellen HTML-Entities und zusätzlichen Daten
            json_data_str = json_data_str.split('});')[0] + '}'
            json_data_str = json_data_str.strip()

            # Lade die JSON-Daten
            try:
                data = json.loads(json_data_str)
                
                # Root Element
                task = Element('Task', type="RT")

                # Function to create a waypoint
                def create_waypoint(parent, point):
                    point_type = point['type'].capitalize() if point['type'] != 'point' else 'Turn'
                    point_elem = SubElement(parent, 'Point', type=point_type)
                    waypoint_elem = SubElement(point_elem, 'Waypoint', altitude=str(point['elevation']), name=point['name'])
                    location_elem = SubElement(waypoint_elem, 'Location', latitude=str(point['latitude']), longitude=str(point['longitude']))
                    
                    if point_type == 'Start':
                        oz_elem = SubElement(point_elem, 'ObservationZone', length="10000.0", type="Line")
                    elif point_type == 'Finish':
                        oz_elem = SubElement(point_elem, 'ObservationZone', radius="4000.0", type="Cylinder")
                    else:
                        oz_elem = SubElement(point_elem, 'ObservationZone', radius="500", type="Cylinder")
                    return point_elem

                # Create waypoints
                for point in data['task_points']:
                    create_waypoint(task, point)

                # Convert to XML string
                xml_str = tostring(task, 'utf-8').decode('utf-8')

                # Save to .tsk file
                with open('task.tsk', 'w') as file:
                    file.write(xml_str)

                print("TSK file created successfully.")
            except json.JSONDecodeError as e:
                print(f"JSONDecodeError: {e}")
                print(f"JSON Data: {json_data_str}")
        else:
            print("JSON data not found in the script tag.")
    else:
        print("Script tag containing taskData variable not found.")
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
