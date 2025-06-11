# excel_writer.py
import os
import pandas as pd
from datetime import datetime

class ExcelWriter:
    def __init__(self, filename):
        self.filename = filename
        if not os.path.exists(self.filename):
            df = pd.DataFrame(columns=[
                'Date', 'Account', 'Category', 'Subcategory', 'Note', 'Amount', 'Income/Expense', 'Description'
            ])
            df.to_csv(self.filename, sep='\t', index=False)

    def write_transaction(self, transaction):
        try:
            # Add description note
            transaction['Description'] = 'added from telegram'
            df = pd.read_csv(self.filename, sep='\t')
            df = pd.concat([df, pd.DataFrame([transaction])], ignore_index=True)
            df.to_csv(self.filename, sep='\t', index=False)
            print("Writting to the file")
            print(transaction)
        except Exception as e:
            print(f"Error writing to file: {e}")
