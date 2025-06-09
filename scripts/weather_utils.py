# Import necessary libraries
from scripts import config
import subprocess
import datetime
import os

# Update the weather briefing by running the metbrief script
def update_metbrief():
    print("⚙️  Updating weather briefing...")
    metbrief_script = os.path.join("externals", "metbrief", "metbrief.py")
    if not os.path.exists(metbrief_script):
        print(f"❌ metbrief.py script not found at '{metbrief_script}'. Please ensure it exists.")
    else:
        try:
            subprocess.run(
                ["python", "metbrief.py"],
                cwd="externals/metbrief",
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("✅ Weather briefing updated successfully.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Weather briefing update failed (exit code {e.returncode}).")

 
# Get the folgder path for the latest weather briefing
def get_latest_weather_briefing_folderPath():
    today = datetime.date.today().strftime('%m%d')
    folderPath = os.path.join(config.weather_briefing_path, today)
    return os.path.normpath(folderPath)

# Get the full path of the latest weather briefing file
def get_latest_weather_briefing_fullPath():
    today = datetime.date.today().strftime('%m%d')
    fullFilepath = os.path.join(get_latest_weather_briefing_folderPath(), str(today) + "_" + str(os.path.basename(config.weather_briefing_path)) + ".odp")
    return fullFilepath