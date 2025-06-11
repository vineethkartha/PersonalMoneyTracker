# parsers/upi_parser.py

import re
from .base_parser import BaseParser
from datetime import datetime
from category_predictor import CategoryPredictor

class UPIParser(BaseParser):
    def parse(self, message):
        try:
            print("In UPI Parser---------------")
            amount_match = re.search(r'Sent Rs\.?\s?(\d+(?:\.\d{1,2})?)', message)
            to_match = re.search(r'To (.+)', message)
            date_match = re.search(r'On (\d{2}[-/]\d{2}[-/]\d{2})', message)
            account_match = re.search(r'A/C \*(\d+)', message)

            if not (amount_match and to_match and date_match and account_match):
                print("skipping upi")
                return None

            amount = float(amount_match.group(1))
            to = to_match.group(1).split('\n')[0].strip()
            date = datetime.strptime(date_match.group(1), '%d/%m/%y').strftime('%d/%m/%Y')
            account_end = account_match.group(1)

            if account_end == '5000':
                account = '(p)HDFC'
            elif account_end == '4765':
                account = '(v)HDFC'
            else:
                account = 'Unknown'

            predictor = CategoryPredictor()
            category, subcategory = predictor.predict(to)
            print(f"Predicted Category: {category}, Subcategory: {subcategory}")

            return {
                'Date': date,
                'Account': account,
                'Category': category,
                'Subcategory': subcategory,
                'Note': to,
                'Amount': amount,
                'Income/Expense': 'Expense',
                'Description': ''
            }
        except Exception as e:
            print(f"Error parsing UPI message: {e}")
            return None
