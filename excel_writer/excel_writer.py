# excel_writer.py
import os
import pandas as pd

class ExcelWriter:
    def __init__(self, filename):
        self.filename = filename
        if not os.path.exists(self.filename) or os.stat(self.filename).st_size == 0:
            # Ensure header is written if file doesn't exist or is empty
            df = pd.DataFrame(columns=[
                'Date', 'Account', 'Category', 'Subcategory', 'Note', 'Amount', 'Income/Expense', 'Description'
            ])
            df.to_csv(self.filename, sep='\t', index=False)

    def write_transaction(self, transaction):
        try:
            # Add description note
            transaction['Description'] = 'added from telegram'
            df_existing = pd.read_csv(self.filename, sep='\t')

            df_new = pd.DataFrame([transaction])
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)

            df_combined.to_csv(self.filename, sep='\t', index=False)
            print("Writing to the file")
            print(transaction)
        except Exception as e:
            print(f"Error writing to file: {e}")

    def read_transactions(self):
        try:
            data = []
            existing_data = pd.read_csv(self.filename, sep='\t')
            for index in range(0,len(existing_data)):
                row_data = existing_data.iloc[index].to_dict()
                data.append(row_data)
        except Exception as e:
            print(f"Error reading from file: {e}")
            
        return data
