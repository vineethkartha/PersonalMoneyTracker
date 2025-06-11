# excel_writer.py
import os
import pandas as pd

class ExcelWriter:
    def __init__(self, filename):
        self.filename = filename
        if not os.path.exists(self.filename):
            df = pd.DataFrame(columns=[
                'Date', 'Account', 'Category', 'Subcategory', 'Note', 'Amount', 'Income/Expense', 'Description'
            ])
            df.to_excel(self.filename, index=False)

    def write_transaction(self, transaction):
        try:
            df = pd.read_excel(self.filename)
            df = pd.concat([df, pd.DataFrame([transaction])], ignore_index=True)
            df.to_excel(self.filename, index=False)
            print("Entry made to excel")
        except Exception as e:
            print(f"Error writing to Excel: {e}")
