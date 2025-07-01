# src/writer.py
#----------------------------------------------------------------
# This module contains functions to save transformed 
# data to CSV files.
#
# author: ekastel
# date: 2025-06-27
#----------------------------------------------------------------

def save_to_csv(dataframe, file_path):
    """Saves a pandas DataFrame to a CSV file."""
    print(f"Saving data to {file_path}...")
    # Ensure the directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(file_path, index=False)
    print("Save complete.")