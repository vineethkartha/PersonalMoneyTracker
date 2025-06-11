import re
import pandas as pd
import fasttext

# Load trained model
model = fasttext.load_model('models/category_model.ftz')

# Excel file
excel_file = 'data/transactions.xlsx'

# Parse and classify message
def parse_message(message):
    if 'spent on your SBI Credit Card' in message or 'spent on your HDFC Credit Card' in message:
        return parse_credit_card_message(message)
    elif 'Sent Rs.' in message and 'From HDFC Bank A/C' in message:
        return parse_upi_message(message)
    else:
        return None

def parse_credit_card_message(message):
    amount = re.search(r'Rs\.(\d+(\.\d{1,2})?)', message).group(1)
    date = re.search(r'on (\d{2}/\d{2}/\d{2})', message).group(1)
    card_end = re.search(r'Credit Card ending (\d+)', message).group(1)
    merchant = re.search(r'at (.+?) on', message).group(1)

    if card_end in ['7752', '7760']:
        account = 'SBI credit card'
    else:
        account = 'HDFC credit card'

    prediction = model.predict(merchant)[0][0]
    _, category, subcategory = prediction.split('__')

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

def parse_upi_message(message):
    amount = re.search(r'Sent Rs\.(\d+(\.\d{1,2})?)', message).group(1)
    date = re.search(r'On (\d{2}/\d{2}/\d{2})', message).group(1)
    account_end = re.search(r'A/C \*(\d+)', message).group(1)
    to = re.search(r'To (.+?)\n', message).group(1)

    if account_end == '5000':
        account = '(p)HDFC'
    elif account_end == '4765':
        account = '(v)HDFC'
    else:
        account = 'Unknown'

    prediction = model.predict(to)[0][0]
    _, category, subcategory = prediction.split('__')

    if category == 'Household' and subcategory == 'Misc':
        note = to
    else:
        note = to

    return {
        'Date': date,
        'Account': account,
        'Category': category,
        'Subcategory': subcategory,
        'Note': note,
        'Amount': amount,
        'Income/Expense': 'Expense',
        'Description': ''
    }

def append_to_excel(data):
    try:
        df_existing = pd.read_excel(excel_file)
    except FileNotFoundError:
        df_existing = pd.DataFrame()

    df_new = pd.DataFrame([data])
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    df_combined.to_excel(excel_file, index=False)
    print("Transaction added successfully!")

# Example usage
if __name__ == "__main__":
    msg = input("Paste transaction message: ")
    parsed = parse_message(msg)
    if parsed:
        append_to_excel(parsed)
    else:
        print("Unsupported message format.")
