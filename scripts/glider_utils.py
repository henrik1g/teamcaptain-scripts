# Import necessary libraries
from scripts import config
import os
import json
import pandas as pd
import csv
import xml.etree.ElementTree as ET


flarmnet = ET.Element('FLARMNET')
def add_flarmdata(flarmid, user, fav=None, reg=None, compid=None,
                  color="0x000000ff", size=None):
    flarmdata = ET.SubElement(flarmnet, 'FLARMDATA', FlarmID=flarmid, user=str(user))
    if fav is not None:
        flarmdata.set('fav', str(fav))
    
    if reg:
        reg_element = ET.SubElement(flarmdata, 'REG')
        reg_element.text = reg
        
    if compid:
        compid_element = ET.SubElement(flarmdata, 'COMPID')
        compid_element.text = compid
        
    # Hinzufügen von <CUSTOM> mit COLOR und SIZE
    custom = ET.SubElement(flarmdata, 'CUSTOM')
    if color:
        color_element = ET.SubElement(custom, 'COLOR')
        color_element.text = color
    if size:
        size_element = ET.SubElement(custom, 'SIZE')
        size_element.text = str(size)

# Funktion zur XML Einrückung (Pretty Print)
def indent(elem, level=0):
    i = "\n" + level * "    "  # 4 Leerzeichen pro Ebene
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        for child in elem:
            indent(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = i
    if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i
    return elem

def create_glider_lx_xml_file(class_name):
    print(f"\t\t📄 Creating glider userflarm.xml file")
    filename = config.filename_map.get(class_name, "all")
    filepath = os.path.join(config.glider_output_dir, f"{config.comp_name}_{filename}_userflarm.xml")
    
    df = pd.read_excel(config.database_path)

    # Ensure all needed columns exist
    required_cols = ['COMP', 'FlarmID']
    if not all(col in df.columns for col in required_cols):
        raise ValueError("One or more required columns are missing in the Excel sheet.")

    # Drop rows where any required column is missing (i.e., end of table or incomplete rows)
    df = df.dropna(subset=['COMP','FlarmID'])

    if filename != 'all':
        df = df[df['Class'].isin([class_name])]

    # Replace NaN with empty string for relevant columns
    df[['FlarmID', 'COMP', 'Flag','Glider', 'Name']] = df[['FlarmID', 'COMP',
                                                           'Flag','Glider', 'Name']].fillna('')
    # Neue Spalte 'color' mit den zugeordneten Farbwerten
    df['color'] = df['Class'].map(config.color_map)

    for index, row in df.iterrows():
      add_flarmdata(f"{row['FlarmID']}",user=1, color=f"{row['color']}", size=30, compid=f"{row['COMP']}", fav=None)


    #Baum erstellen und einrücken
    indent(flarmnet)
    tree = ET.ElementTree(flarmnet)

    # Schreiben der XML-Datei
    with open(filepath, "wb") as file:
      file.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
      tree.write(file, encoding='utf-8')
      # Schreiben der XML-Datei

    print(f"\t\t✅ Saved userflarm.xml glider file at '{filepath.replace(os.sep, '/')}'")

# Create .txt files out of database.xlsx
# Now creates .txt files out of Database.xlsx
def create_glider_txt_file(class_name):
    print(f"\t\t📄 Creating glider .txt file")
    filename = config.filename_map.get(class_name, "all")
    filepath = os.path.join(config.glider_output_dir, f"{config.comp_name}_{filename}.txt")
    
    df = pd.read_excel(config.database_path)

    # Ensure all needed columns exist
    required_cols = ['COMP', 'Name', 'Flag','Glider', 'FlarmID']
    if not all(col in df.columns for col in required_cols):
        raise ValueError("One or more required columns are missing in the Excel sheet.")

    # Drop rows where any required column is missing (i.e., end of table or incomplete rows)
    df = df.dropna(subset=['Name'])

    if filename != 'all':
        df = df[df['Class'].isin([class_name])]

    # Replace NaN with empty string for relevant columns
    df[['FlarmID', 'COMP', 'Flag','Glider', 'Name']] = df[['FlarmID', 'COMP',
                                                           'Flag','Glider', 'Name']].fillna('')
    
    # Build the string using the specified format
    df['String'] = df.apply(lambda row: f"{row['FlarmID']},,{row['Flag'] + ' ' if row['Flag'] else ''}{row['COMP']},{row['Glider']},{row['Flag'] + ' ' if row['Flag'] else ''}{row['Name']}", axis=1)

# Write lines manually to avoid any escaping
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("ID,CALL,CN,TYPE,NAME\n")
        for line in df['String']:
            f.write(f"{line}\n")
    
    # Save only the "String" column to a .txt file
    #df['String'].to_csv(filepath, index=False, header=False, quoting=csv.QUOTE_NONE, escapechar='\\')

    print(f"\t\t✅ Saved .txt glider file at '{filepath.replace(os.sep, '/')}'")


def create_glider_xcsoar():
    print(f"\t\t📄 Creating xcsoar-flarm.txt file")
    filename = "xcsoar-flarm.txt"
    filepath = os.path.join(config.glider_output_dir, filename)
    
    df = pd.read_excel(config.database_path)

    # Ensure all needed columns exist
    required_cols = ['COMP', 'FlarmID']
    if not all(col in df.columns for col in required_cols):
        raise ValueError("One or more required columns are missing in the Excel sheet.")

    # Drop rows where any required column is missing (i.e., end of table or incomplete rows)
    df = df.dropna(subset=['FlarmID','COMP'])

    
    # Build the string using the specified format
    df['String'] = df.apply(lambda row: f"{row['FlarmID']}={row['COMP']}", axis=1)

# Write lines manually to avoid any escaping
    with open(filepath, "w", encoding="utf-8") as f:
        for line in df['String']:
            f.write(f"{line}\n")
    
    # Save only the "String" column to a .txt file
    #df['String'].to_csv(filepath, index=False, header=False, quoting=csv.QUOTE_NONE, escapechar='\\')

    print(f"\t\t✅ Saved xcsoar-flarm.txt glider file at '{filepath.replace(os.sep, '/')}'")




# Create a glider .json file from the .txt file
def create_glider_json_file(class_name):
    print(f"\t\t📄 Creating glider .json file")
    filename = os.path.join(config.glider_output_dir, f"{config.comp_name}_{config.filename_map.get(class_name, 'all')}.txt")
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

# Create both .txt and .json files (only needed once below)
def create_glider_files(class_name):
    print(f"\t🔍 Fetching glider data")
    create_glider_txt_file(class_name)
    create_glider_json_file(class_name)
    create_glider_xcsoar()
    create_glider_lx_xml_file(class_name)

# Update all glider files
def update_glider_files():
    print("⚙️  Updating glider files...")
    for class_name in config.classes:
        print(f"\t⚙️  Updating glider files for class: {class_name}")
        create_glider_files(class_name)
    print(f"\t⚙️  Updating glider files for all classes combined")
    create_glider_files('all')
