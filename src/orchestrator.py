# src/orchestrator.py
#----------------------------------------------------------------------------------
# This script orchestrates the generation of reports, sends them via email, and cleans up afterwards.
# It runs specified Python scripts, collects their output files, sends them as email attachments,
# and finally deletes the files from the reports directory.
#
# author: ekastel
# date: 2025-06-27
#--------------------------------------------------------------------------------

import os
import smtplib
import subprocess
import sys
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Paths
BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR.parent / "reports" / "mail"

# Scripts to run in order
# Make sure these scripts exist in the src/ folder
SCRIPTS_TO_RUN = [
    "generate_excel_report.py",
    "create_visual_en.py"
]

# Email configuration loaded from .env file
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
RECIPIENTS = [email.strip() for email in os.getenv('RECIPIENTS', '').split(',')]


def run_report_scripts():
    """Executes all Python scripts that generate reports."""
    print("--- 1. Running scripts to generate reports ---")
    for script_name in SCRIPTS_TO_RUN:
        script_path = BASE_DIR / script_name
        if not script_path.exists():
            print(f"WARNING: Script '{script_name}' not found. Skipping.")
            continue
        try:
            print(f"Executing '{script_name}'...")
            # Use sys.executable to ensure the same Python interpreter is used
            subprocess.run([sys.executable, script_path], check=True, capture_output=True, text=True)
            print(f"'{script_name}' executed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"ERROR executing '{script_name}': {e.stderr}")
            # Decide whether to stop or continue if a script fails
            # return False
    print("--- All report scripts have been executed. ---")
    return True

def send_email_with_attachments():
    """Finds reports, attaches them, and sends an email."""
    print("\n--- 2. Preparing and sending email ---")
    
    report_files = list(REPORTS_DIR.glob('*'))
    if not report_files:
        print("No reports found to send. Aborting email process.")
        return False

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = ", ".join(RECIPIENTS)
    msg['Subject'] = f"Automated Reports - {pd.Timestamp.now().strftime('%Y-%m-%d')}"

    # Email body
    body = "Good morning,\n\nPlease find the automatically generated reports attached.\n\nRegards."
    msg.attach(MIMEText(body, 'plain'))

    # Attach files
    for file_path in report_files:
        try:
            with open(file_path, "rb") as f:
                part = MIMEApplication(f.read(), Name=file_path.name)
            part['Content-Disposition'] = f'attachment; filename="{file_path.name}"'
            msg.attach(part)
            print(f"Attached: {file_path.name}")
        except Exception as e:
            print(f"Could not attach file {file_path.name}. Error: {e}")

    # Send email
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure connection
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Email sent successfully to: {', '.join(RECIPIENTS)}")
        return True
    except Exception as e:
        print(f"ERROR sending email: {e}")
        return False

def cleanup_reports():
    """Deletes all files from the reports folder."""
    print("\n--- 3. Cleaning up the reports folder ---")
    report_files = list(REPORTS_DIR.glob('*'))
    if not report_files:
        print("No reports to clean up.")
        return
        
    for file_path in report_files:
        try:
            os.remove(file_path)
            print(f"Deleted: {file_path.name}")
        except OSError as e:
            print(f"ERROR deleting file {file_path.name}: {e}")
    print("--- Cleanup complete. ---")

def main():
    """Main function to orchestrate the entire process."""
    print(">>> Starting Report Orchestrator <<<")
    
    # Ensure the reports directory exists
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    if run_report_scripts():
        if send_email_with_attachments():
            cleanup_reports()
            
    print("\n>>> Orchestrator process finished. <<<")

if __name__ == '__main__':
    import pandas as pd
    main()