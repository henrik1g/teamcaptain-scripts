import requests

# Shared base URL and task date
date_segment = "practice-2-on-2025-06-06"
base_url = "https://xlxjz3geasj4wiei7n5vzt7zzu0qibmm.lambda-url.eu-central-1.on.aws/?url=https://www.soaringspot.com/en_gb/39th-fai-world-gliding-championships-tabor-2025/tasks"

# Classes and corresponding output filenames
classes = {
    "-15-meter": "data/tasks/15m.cup",
    "club": "data/tasks/club.cup",
    "standard": "data/tasks/std.cup"
}

# Download each task file
for class_name, filename in classes.items():
    full_url = f"{base_url}/{class_name}/{date_segment}"
    print(f"📥 Downloading from: {full_url}")

    response = requests.get(full_url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"✅ Saved as: {filename}")
    else:
        print(f"❌ Failed to download {full_url} (status code: {response.status_code})")