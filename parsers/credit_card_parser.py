import re
from .base_parser import BaseParser
from datetime import datetime
from category_predictor import get_predictor

class CreditCardParser(BaseParser):
    def parse(self, message):
        try:
            print("In Credit Card Parser----------------------")
            
            # 1. Extract Amount (Handles commas and optional decimal points)
            amount_match = re.search(r'Rs\.?([\d,]+(?:\.\d{1,2})?)', message, re.IGNORECASE)
            
            # 2. Extract Card Number (Flexible pattern for both HDFC and SBI styles)
            card_match = re.search(r'(?:Card\s(?:ending\s)?|\s)(\d{4})\b', message, re.IGNORECASE)
            
            # 3. Extract Merchant (Captures text between 'at' and 'on' safely)
            merchant_match = re.search(r'\bat\s+(.*?)\s+on\b', message, re.IGNORECASE)
            
            # 4. Extract Date (Supports YYYY-MM-DD or DD/MM/YY)
            date_match = re.search(r'\bon\s+(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{2})', message, re.IGNORECASE)
            
            # Validation check
            if not (amount_match and merchant_match and date_match):
                print("Skipping credit card message due to missing mandatory fields")
                return None

            # Process Amount
            amount = float(amount_match.group(1).replace(',', ''))
            
            # Process Merchant
            merchant = merchant_match.group(1).strip()
            
            # Process Date dynamically based on the detected format
            raw_date = date_match.group(1)
            if '-' in raw_date:
                # Format: YYYY-MM-DD (HDFC)
                date_obj = datetime.strptime(raw_date, '%Y-%m-%d')
            else:
                # Format: DD/MM/YY (SBI)
                date_obj = datetime.strptime(raw_date, '%d/%m/%y')
            
            formatted_date = date_obj.strftime('%d/%m/%Y')            

            # Process Bank Account mapping based on text context
            card_number = card_match.group(1) if card_match else ''
            if 'SBI' in message.upper():
                account = 'SBI creditcard'
            elif 'HDFC' in message.upper():
                account = 'HDFC creditcard'
            else:
                account = f'Other creditcard ({card_number})'.strip()

            # Category determination
            predictor = get_predictor()
            category, subcategory = predictor.predict(merchant)
            print(f"Predicted Category: {category}, Subcategory: {subcategory}")
            
            return {
                'Date': formatted_date,
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
