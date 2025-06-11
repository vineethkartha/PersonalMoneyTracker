import unittest
import tempfile
import os
import pandas as pd
from excel_writer import ExcelWriter

class TestExcelWriter(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.tsv')
        self.test_file_path = self.temp_file.name
        self.temp_file.close()
        self.excel_writer = ExcelWriter(self.test_file_path)

    def tearDown(self):
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

    def test_write_to_excel_data(self):
        sample_data = {
            'Date': '06/09/2025',
            'Account': '(p)HDFC',
            'Category': 'Food and other',
            'Subcategory': 'Groceries and household items',
            'Note': 'Test Note',
            'Amount': 100.0,
            'Income/Expense': 'Expense',
            'Description': 'added from telegram'
        }

        self.excel_writer.write_transaction(sample_data)

        df = pd.read_csv(self.test_file_path, sep='\t')

        # Check headers
        expected_columns = ['Date', 'Account', 'Category', 'Subcategory', 'Note', 'Amount', 'Income/Expense', 'Description']
        self.assertListEqual(list(df.columns), expected_columns)

        # Check row data
        written_row = df.iloc[0].to_dict()
        for key in sample_data:
            self.assertEqual(str(written_row[key]), str(sample_data[key]))

    def test_append_to_existing_file(self):
        sample_data1 = {
            'Date': '06/09/2025',
            'Account': '(p)HDFC',
            'Category': 'Food and other',
            'Subcategory': 'Groceries and household items',
            'Note': 'First Entry',
            'Amount': 200.0,
            'Income/Expense': 'Expense',
            'Description': 'added from telegram'
        }

        sample_data2 = {
            'Date': '06/10/2025',
            'Account': '(v)HDFC',
            'Category': 'Food and other',
            'Subcategory': 'Eating out',
            'Note': 'Second Entry',
            'Amount': 150.0,
            'Income/Expense': 'Expense',
            'Description': 'added from telegram'
        }

        self.excel_writer.write_transaction(sample_data1)
        self.excel_writer.write_transaction(sample_data2)

        df = pd.read_csv(self.test_file_path, sep='\t')

        # Validate row count
        self.assertEqual(len(df), 2)

        self.assertEqual(df.iloc[0]['Note'], 'First Entry')
        self.assertEqual(df.iloc[1]['Note'], 'Second Entry')

if __name__ == '__main__':
    unittest.main()
