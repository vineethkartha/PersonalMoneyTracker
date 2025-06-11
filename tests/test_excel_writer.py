import unittest
import tempfile
import os
import csv
from excel_writer import ExcelWriter

class TestExcelWriter(unittest.TestCase):
    def setUp(self):
        # Create a temporary file for each test
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.tsv')
        self.test_file_path = self.temp_file.name
        self.temp_file.close()
        self.excel_writer = ExcelWriter(self.test_file_path)
    def tearDown(self):
        # Clean up the temporary file after each test
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

        # Read the file and validate its content
        with open(self.test_file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='\t')
            rows = list(reader)

        # Check headers
        expected_headers = ['Date', 'Account', 'Category', 'Subcategory', 'Note', 'Amount', 'Income/Expense', 'Description']
        self.assertEqual(rows[0], expected_headers)

        # Check row data
        expected_row = [
            '06/09/2025',
            '(p)HDFC',
            'Food and other',
            'Groceries and household items',
            'Test Note',
            '100.0',
            'Expense',
            'added from telegram'
        ]
        self.assertEqual(rows[1], expected_row)

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

        # Read the file and validate its content
        with open(self.test_file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='\t')
            rows = list(reader)

        # Validate row count: header + 2 rows
        self.assertEqual(len(rows), 3)

        self.assertEqual(rows[1][4], 'First Entry')
        self.assertEqual(rows[2][4], 'Second Entry')

if __name__ == '__main__':
    unittest.main()
