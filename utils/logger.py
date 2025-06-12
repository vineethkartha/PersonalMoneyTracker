# logger.py
import csv
import os
from datetime import datetime

LOG_FILE = 'logs/transaction_log.csv'

# Ensure log file exists with headers
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'ID', 'Name', 'Raw Message', 'Parsed Result'])


def log_transaction(userid, name, message, result):
    try:
        with open(LOG_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([datetime.now().isoformat(), userid, name, message, result])
    except Exception as e:
        print(f"Error logging transaction: {e}")
