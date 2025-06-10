# Team Captain Script

This project provides a set of tools to automate and streamline the management of glider competitions, including task and glider file generation, weather briefing creation, WhatsApp integration, and browser automation for SoaringSpot and related platforms.

---

## 🚀 Capabilities

- **Task & Glider File Management:**  
  - Automatically fetches and updates task and glider lists from SoaringSpot.
  - Generates `.txt`, `.json`, `.tsk`, and `.cup` files for various platforms (OGN, GlideAndSeek, SeeYou, etc.).

- **Weather Briefing Automation:**  
  - Runs [metbrief](https://github.com/jkretz/metbrief) to generate weather briefings.
  - Opens and converts weather briefings to PDF using LibreOffice.

- **Browser Automation:**  
  - Opens multiple Chrome windows/tabs based on a configurable URL file.
  - Supports dynamic placeholders and window assignment in URLs. This allows to open tracking sites with the files supported

- **WhatsApp Integration:**  
  - Sends the latest weather briefing PDF directly to a WhatsApp group via WhatsApp Web automation.

- **Menu-Driven Workflow:**  
  - Interactive menu for daily preparation, continuous monitoring, manual updates, and more.

---

## ⚙️ Configuration

All configuration is managed in [`scripts/config.py`](scripts/config.py):

- **Competition & File Paths:**  
  - `base_url`: SoaringSpot event URL  
  - `url_file`: Path to the URL list  
  - `database_path`: Path to the Excel database  
  - `task_output_dir`, `glider_output_dir`: Output directories

- **Weather Briefing:**  
  - `weather_briefing_path`: Path for weather briefings

- **WhatsApp:**  
  - `whatsapp_group`: Name of the WhatsApp group  
  - `whatsapp_message`: Default message to send

- **LibreOffice & Git:**  
  - `soffice_path`: Path to LibreOffice executable  
  - `commit_and_push_to_git`: Enable/disable automatic git commit/push (see below for more information on using git)

- **Mappings:**  
  - `classes`, `filename_map`, `url_map`, `results_table_map`: Competition class mappings

**To customize:**  
Edit `scripts/config.py` to match your event, file locations, and preferences.

---

## 🛠️ Installation

1. **Install Dependencies:**
   - [LibreOffice](https://www.libreoffice.org/download/download/)
   - [Miniconda/Anaconda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html)
   - [Google Chrome](https://www.google.com/chrome/)
   - [ChromeDriver](https://chromedriver.chromium.org/downloads) (ensure it matches your Chrome version)

2. **Set up the metbrief submodule:**
   - See the corresponding section below for more information.

2. **Clone the Repository:**
   ```bash
   git clone https://github.com/nilsschlautmann/wgc2025
   cd yourrepo
   ```

3. **Set Up the Environment:**
   ```bash
   conda env create -f environment.yml
   conda activate teamcaptain
   ```

4. **Configure the Script:**
   - Edit `scripts/config.py` as described above.

5. **(Optional) WhatsApp Web:**
   - The first time you run WhatsApp automation, scan the QR code in the opened Chrome window.

---

## 📝 Usage

From the project root, run:

```bash
python teamcaptain.py
```

You will be presented with an interactive menu.  
Choose options to update tasks, generate files, open browser tabs, send WhatsApp messages, and more.

---

## 📄 URL File Format

- Place URLs in `data/urls.txt`.
- Use placeholders like `{taskID}`, `{classURL}`, `{classFile}` for dynamic replacement.
- Use `{WIN:N}` to open URLs in specific windows. If no window is specified, {WIN:0} is the default choice
- `{WIN:I}` tells the script to open **one window per competition class** for the given URL.
- If the URL contains class placeholders (like `{taskID}`, `{classURL}`, `{classFile}`), the script will generate a separate URL for each class, replacing the placeholders accordingly.
- Each generated URL will be opened in its own window, in the order classes are defined in your configuration.
- This is useful for tracking or visualization sites where you want a dedicated window for each class.

**Example:**
```
https://www.example.com
{WIN:2} https://another.com/{taskID}
{WIN:I}https://ogn.cloud/?tsk=https://raw.githubusercontent.com/nilsschlautmann/wgc2025/main/data/tasks/{classFile}.tsk&lst=https://raw.githubusercontent.com/nilsschlautmann/wgc2025/main/data/gliders/{classFile}.txt
```

---

## 📊 Database File Usage

The script uses an Excel database file (`data/database.xlsx`) to manage and store pilot, glider, and registration information for the competition.  
This file is referenced in your configuration as `database_path` in [`scripts/config.py`](scripts/config.py).

### How to Use the Database

- **Location:**  
  Place your Excel file at `data/database.xlsx` (or update the path in `config.py` if you move it).

- **Structure:**  
  The database should contain at least the following columns:
  - `Pilot Name`
  - `Glider Type`
  - `Competition Number`
  - `Registration`
  - `Class`
  - (Add any other fields your workflow requires)

- **Editing:**  
  Edit the file using Excel, LibreOffice, or any spreadsheet editor.  
  Save your changes before running the script.

- **Purpose:**  
  The script reads this file to generate glider lists, task files, and to ensure all pilot and glider data is up to date for each competition class.  
  Any updates to pilot or glider information should be made in this file.

- **Customization:**  
  If you add or rename columns, update the relevant code in `scripts/glider_utils.py` and `scripts/task_utils.py` to match your new structure.

### Example Workflow

1. Update pilot/glider data in `data/database.xlsx`.
2. Run the script (`python teamcaptain.py`) and choose the menu option to update tasks and gliders.
3. The script will read the latest data from the database and generate the necessary files for tracking and scoring platforms.

---

## ☁️ Weather Briefing Setup & Usage

The script can automatically generate and process weather briefings using the [metbrief](https://github.com/jkretz/metbrief) tool.

### 1. Install and Configure metbrief

- The `metbrief` tool is included as a subfolder in `externals/metbrief`.
- Edit `externals/metbrief/user_details.py` and add your login details for services like flugwetter.de and TopMeteo.

### 2. Configure Paths

- Make sure `weather_briefing_path` in [`scripts/config.py`](scripts/config.py) points to the correct folder (usually something like `externals/metbrief/briefings/tabor_25`).

### 3. Generate a Weather Briefing

- The script will call `metbrief.py` automatically when you select the weather briefing option from the menu.
- This will:
  - Download the latest weather data and charts.
  - Create a new folder for today’s date in the briefing directory.
  - Generate an `.odp` (LibreOffice presentation) and convert it to PDF.

### 4. Open or Send the Briefing

- The script can open the generated weather briefing in LibreOffice or send the PDF to WhatsApp (if configured).

### Notes & Tips

- **First-time setup:**  
  You should run `metbrief.py` at least once manually to ensure all dependencies are installed and credentials are set.
- **Customization:**  
  You must adjust the template and chart sources in the `metbrief` folder as needed for your competition.
- **Troubleshooting:**  
  If weather briefing generation fails, check the logs in the terminal and ensure your credentials and paths are correct.

---

## 🗂️ Git Configuration & Manual Push

### Git Setup

- Make sure you have [Git](https://git-scm.com/downloads) installed and configured with your SSH key or credentials.
- The script uses the SSH key specified in `scripts/config.py` (see the `os.environ['GIT_SSH_COMMAND']` line).
- If you need to change the SSH key, update the path in `config.py`:
  ```python
  os.environ['GIT_SSH_COMMAND'] = 'ssh -i ~/.ssh/id_rsa'
  ```
- Ensure your user name and email are set:
  ```bash
  git config --global user.name "Your Name"
  git config --global user.email "your.email@example.com"
  ```

### Files to Push Manually

If you choose to push updates manually (or if automatic git push is disabled), make sure to add and commit the following files after running the script:

- **Task files:**  
  All files in `data/tasks/` (e.g., `.tsk`, `.cup`, `.txt`, `.json`)

- **Glider files:**  
  All files in `data/gliders/`

- **Weather briefings:**  
  All files in `externals/metbrief/briefings/tabor_25/` (or your configured `weather_briefing_path`)

- **Database:**  
  `data/database.xlsx` (if you made changes to pilot/glider data)

**Example manual workflow:**
```bash
git add data/tasks/* data/gliders/* externals/metbrief/briefings/tabor_25/* data/database.xlsx
git commit -m "Update tasks, gliders, and weather briefing"
git push
```

**Tip:**  
If you add new files or folders, make sure they are not excluded by `.gitignore`.

## 🔧 Enabling or Disabling Automatic Git Push

By default, the script can automatically commit and push changes to your git repository after updates (such as new task, glider, or weather briefing files).  
You can enable or disable this feature at any time from the interactive menu.

### How to Change Git Push Settings

1. **Start the script:**
   ```bash
   python teamcaptain.py
   ```

2. **From the main menu, select the option to update Git settings.**
   - The menu will display the current setting (enabled or disabled).
   - You will be prompted:
     ```
     Do you want to enable automatic git commit and push after updates? (Y/N)?
     ```
   - Enter `y` to enable or `n` to disable automatic git commit and push.

3. **Effect:**
   - If enabled, the script will automatically add, commit, and push relevant files after each update.
   - If disabled, you must manually add, commit, and push files using git (see the section above for which files to push).

**Tip:**  
You can change this setting as often as you like from the menu.  
The current setting is stored in memory for the current session.

---

## ⚠️ Limitations & Known Issues

- **WhatsApp Web:**  
  - Requires manual QR code scan on first use.
  - WhatsApp Web UI changes may break automation (update selectors in `whatsapp_utils.py` if needed).

- **LibreOffice:**  
  - Force-closing LibreOffice may trigger recovery dialogs on next start.

- **Chrome Automation:**  
  - ChromeDriver and Chrome versions must match.
  - Only Chrome is supported for browser automation.

- **Platform:**  
  - Tested on Windows. Linux and macOS should work but is not officially supported.

---

## 🧩 Extending & Customizing

- Add new menu options in `scripts/menu_utils.py`.
- Add new automation or integrations as new modules in `scripts/`.
- All shared configuration is in `scripts/config.py`.

---

## 🤝 Contributing

Pull requests and suggestions are welcome!  
Please open an issue for bugs or feature requests.

---

## 📚 Credits

- [metbrief](https://github.com/jkretz/metbrief) for weather briefing generation.
- [Selenium](https://www.selenium.dev/) for browser automation.
- [LibreOffice](https://www.libreoffice.org/) for document conversion.

---

## 📬 Support

For questions or help, please contact [nils.schlautmann@gmail.com].