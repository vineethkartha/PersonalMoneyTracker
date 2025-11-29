# parsers/upi_parser.py

import re
from .base_parser import BaseParser
from datetime import datetime
from category_predictor import get_predictor

class CreditCardParser(BaseParser):
    def parse(self, message):
        try:
            print("In Credit Card Parser----------------------")
            amount_match = re.search(r'(?:₹|Rs\.?\s?)([\d,]+(?:\.\d{1,2})?)', message)
            card_match = re.search(r'Credit Card ending (\d{4})', message)
            merchant_match = re.search(r'at (.*?) on', message)
            date_match = re.search(r'on (\d{2}/\d{2}/\d{2})', message)
            
            if not (amount_match and merchant_match and date_match):
                print("skipping credit card")
                return None

            amount = float(amount_match.group(1).replace(',', '')) if amount_match else 0.0
            merchant = merchant_match.group(1).strip() if merchant_match else 'Unknown'
            date = datetime.strptime(date_match.group(1), '%d/%m/%y').strftime('%d/%m/%Y')            

            card_number = card_match.group(1) if card_match else ''
            if card_number in ['7752', '7760']:
                account = 'SBI creditcard'
            else:
                account = 'HDFC creditcard'

            # Category determination
            predictor = get_predictor()
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

