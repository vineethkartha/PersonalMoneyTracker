# parser_module.py
import re
from datetime import datetime
from category_predictor import CategoryPredictor

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

            print(to_match)
            print(date_match)
            print(account_match)
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


class CreditCardParser(BaseParser):
    def parse(self, message):
        try:
            amount_match = re.search(r'(?:₹|Rs\.?\s?)([\d,]+(?:\.\d{1,2})?)', message)
            amount = float(amount_match.group(1).replace(',', '')) if amount_match else 0.0

            card_match = re.search(r'Credit Card ending (\d{4})', message)
            card_number = card_match.group(1) if card_match else ''

            if card_number in ['7752', '7760']:
                account = 'SBI credit card'
            else:
                account = 'HDFC credit card'

            merchant_match = re.search(r'at (.*?) on', message)
            merchant = merchant_match.group(1).strip() if merchant_match else 'Unknown'

            date_match = re.search(r'on (\d{2}/\d{2}/\d{2})', message)
            date = date_match.group(1) if date_match else ''
            
            print(amount_match)
            print(merchant_match)
            print(date_match)

            if not (amount_match and merchant_match and date_match):
                print("skipping credi card")
                return None
            
            # Category determination
            predictor = CategoryPredictor()
            category, subcategory = predictor.predict(merchant)
            print(f"Predicted Category: {category}, Subcategory: {subcategory}")
            
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
            print(f"Error parsing credit card message: {e}")
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
