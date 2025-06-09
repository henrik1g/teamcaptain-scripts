# Import necessary libraries
from scripts import config
import os
import json
import pandas as pd
import csv

# Create .txt files out of database.xlsx
def create_glider_txt_file(class_name):
    print(f"\t\t📄 Creating glider .txt file")
    filename = config.filename_map.get(class_name, "all")
    filepath = os.path.join(config.glider_output_dir, f"{filename}.txt")
    
    df = pd.read_excel(config.database_path, sheet_name='WGC2025')

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
    filename = os.path.join(config.glider_output_dir, f"{config.filename_map.get(class_name, 'all')}.txt")
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

# Update all glider files
def update_glider_files():
    print("⚙️  Updating glider files...")
    for class_name in config.classes:
        print(f"\t⚙️  Updating glider files for class: {class_name}")
        create_glider_files(class_name)
    print(f"\t⚙️  Updating glider files for all classes combined")
    create_glider_files('all')