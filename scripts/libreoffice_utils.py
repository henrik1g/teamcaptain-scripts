# Import necessary libraries
from scripts import config
import subprocess
import psutil
import os

# Function to open a file in LibreOffice Impress
def open_file(filepath):
    try:
        subprocess.Popen([config.soffice_path, "--norestore", "--impress", filepath])
    except Exception as e:
        print(f"❌ Could not open file in LibreOffice: {e}")

# Function to close all LibreOffice windows
def close_windows():
    print("⚠️  Closing all LibreOffice windows...")
    closed = 0
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and 'soffice' in proc.info['name'].lower():
                proc.terminate()
                closed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    if closed:
        print(f"✅ Closed {closed} LibreOffice process(es).")
    else:
        print("ℹ️  No LibreOffice processes found.")

# Function to convert ODP files to PDF using LibreOffice
def convert_odp_to_pdf(odp_path):
    output_dir = os.path.dirname(odp_path)
    try:
        subprocess.run([
            config.soffice_path, "--headless", "--convert-to", "pdf", odp_path, "--outdir", output_dir
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