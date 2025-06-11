# parsers/upi_parser.py

import re
from .base_parser import BaseParser
from datetime import datetime
from category_predictor import CategoryPredictor

class SalaryParser(BaseParser):
    def parse(self, message):
        try:
            print("In Salary Parser ------------------")
            amount_match = re.search(r'INR ([\d,]+\.\d{1,2}) deposited', message)
            account_match = re.search(r'A/c XX(\d+)', message)
            date_match = re.search(r'on (\d{2}-[A-Z]{3}-\d{2})', message)
            if not (amount_match and account_match and date_match):
                return None

            # Convert to datetime object
            amount = float(amount_match.group(1).replace(',', ''))
            date = datetime.strptime(date_match.group(1), '%d-%b-%y').strftime('%d/%m/%Y')
            
            account_end = account_match.group(1)
            if account_end == '5000':
                account = '(p)HDFC'
            elif account_end == '4765':
                account = '(v)HDFC'
            else:
                account = 'Unknown'

            return {
                'Date': date,
                'Account': account,
                'Category': 'Salary',
                'Subcategory': '',
                'Note': 'Salary Credit',
                'Amount': amount,
                'Income/Expense': 'Income',
                'Description': ''
            }
        except Exception as e:
            print(f"Error parsing Salary message: {e}")
            return None
