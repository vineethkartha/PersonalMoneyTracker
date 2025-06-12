import os
from datetime import datetime
from shutil import move

def archive_and_reset_file(original_file):
    if not os.path.exists(original_file):
        print("No file to archive.")
        return None  # Nothing to send

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_filename = f"data/import_{timestamp}.tsv"

    # Rename (move) the file
    move(original_file, archive_filename)

    # Create a new empty file with headers
    from excel_writer import ExcelWriter
    ExcelWriter(original_file)  # This will create a new file with headers

    return archive_filename  # Return the archived file path to send
