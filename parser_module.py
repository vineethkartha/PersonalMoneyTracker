# parser_module.py
import re
from datetime import datetime

class BaseParser:
    def parse(self, message):
        raise NotImplementedError("Subclasses must implement this method")

class UPIParser(BaseParser):
    def parse(self, message):
        try:
            amount_match = re.search(r'Sent Rs\.?\s?(\d+(?:\.\d{1,2})?)', message)
            to_match = re.search(r'To (.+)', message)
            date_match = re.search(r'On (\d{2}[-/]\d{2}[-/]\d{2})', message)
            account_match = re.search(r'A/C \*(\d+)', message)

            if not (amount_match and to_match and date_match and account_match):
                return None

            amount = float(amount_match.group(1))
            to = to_match.group(1).split('\n')[0].strip()
            date = datetime.strptime(date_match.group(1), '%d/%m/%y').strftime('%Y-%m-%d')
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
                'Category': 'Household',
                'Subcategory': 'misc',
                'Note': to,
                'Amount': amount,
                'Income/Expense': 'Expense',
                'Description': ''
            }
        except Exception as e:
            print(f"Error parsing UPI message: {e}")
            return None

class CreditCardParser(BaseParser):
    def parse(self, message):
        try:
            amount_match = re.search(r'Rs\.?\s?(\d+(?:\.\d{1,2})?) spent on your .*? Credit Card ending (\d+)', message)
            merchant_match = re.search(r'at (.+?) on', message)
            date_match = re.search(r'on (\d{2}[-/]\d{2}[-/]\d{2})', message)

            if not (amount_match and merchant_match and date_match):
                return None

            amount = float(amount_match.group(1))
            card_end = amount_match.group(2)
            merchant = merchant_match.group(1).strip()
            date = datetime.strptime(date_match.group(1), '%d/%m/%y').strftime('%Y-%m-%d')

            if card_end in ['7752', '7760']:
                account = 'SBI Credit Card'
            else:
                account = 'HDFC Credit Card'

            if any(name in merchant.lower() for name in ['dmart', 'avenue super mart', 'family fruits and vege']):
                category = 'Food and other'
                subcategory = 'Groceries and household items'
            elif any(name in merchant.lower() for name in ['hotel', 'restaurant', 'ice cream']):
                category = 'Food and other'
                subcategory = 'Eating out'
            else:
                category = 'Household'
                subcategory = 'misc'

            return {
                'Date': date,
                'Account': account,
                'Category': category,
                'Subcategory': subcategory,
                'Note': merchant,
                'Amount': amount,
                'Income/Expense': 'Expense',
                'Description': ''
            }
        except Exception as e:
            print(f"Error parsing Credit Card message: {e}")
            return None

class SalaryParser(BaseParser):
    def parse(self, message):
        try:
            amount_match = re.search(r'INR ([\d,]+\.\d{1,2}) deposited', message)
            account_match = re.search(r'A/c XX(\d+)', message)
            date_match = re.search(r'on (\d{2}-[A-Z]{3}-\d{2})', message)

            if not (amount_match and account_match and date_match):
                return None

            amount = float(amount_match.group(1).replace(',', ''))
            account_end = account_match.group(1)
            date = datetime.strptime(date_match.group(1), '%d-%b-%y').strftime('%Y-%m-%d')

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

class TransactionParser:
    def __init__(self):
        self.parsers = [UPIParser(), CreditCardParser(), SalaryParser()]

    def parse(self, message):
        for parser in self.parsers:
            result = parser.parse(message)
            if result:
                return result
        return None
