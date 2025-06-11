from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv
import pandas as pd
import fasttext
import re
import os

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

# Load fastText model
model = fasttext.load_model('models/category_model.ftz')

# Excel file location
excel_file = 'data/import.xlsx'

def start(update, context):
    update.message.reply_text('Hello! Send me your expense details.')

def append_to_excel(data):
    try:
        df_existing = pd.read_excel(excel_file)
    except FileNotFoundError:
        df_existing = pd.DataFrame()

    df_new = pd.DataFrame([data])
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    df_combined.to_excel(excel_file, index=False)
    print("Transaction added successfully!")

def parse_message(message):
    if 'spent on your SBI Credit Card' in message or 'spent on your HDFC Credit Card' in message:
        return parse_credit_card_message(message)
    elif 'Sent Rs.' in message and 'From HDFC Bank A/C' in message:
        return parse_upi_message(message)
    elif 'deposited in HDFC Bank A/c' in message:
        return parse_income_message(message)
    else:
        return None

def parse_credit_card_message(message):
    amount_match = re.search(r'Rs\.(\d+(\.\d{1,2})?)', message)
    date_match = re.search(r'on (\d{2}/\d{2}/\d{2})', message)
    card_end_match = re.search(r'Credit Card ending (\d+)', message)
    merchant_match = re.search(r'at (.+?) on', message)

    if not (amount_match and date_match and card_end_match and merchant_match):
        return None

    amount = amount_match.group(1)
    date = date_match.group(1)
    card_end = card_end_match.group(1)
    merchant = merchant_match.group(1)

    if card_end in ['7752', '7760']:
        account = 'SBI creditcard'
    else:
        account = 'HDFC creditcard'

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
    amount_match = re.search(r'Sent Rs\.(\d+(\.\d{1,2})?)', message)
    date_match = re.search(r'On (\d{2}/\d{2}/\d{2})', message)
    account_end_match = re.search(r'A/C \*(\d+)', message)
    to_match = re.search(r'To (.+?)\n', message)

    if not (amount_match and date_match and account_end_match and to_match):
        return None

    amount = amount_match.group(1)
    date = date_match.group(1)
    account_end = account_end_match.group(1)
    to = to_match.group(1)

    if account_end == '5000':
        account = '(p)HDFC'
    elif account_end == '4765':
        account = '(v)HDFC'
    else:
        account = 'Unknown'

    prediction = model.predict(to)[0][0]
    _, category, subcategory = prediction.split('__')

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

def parse_income_message(message):
    amount_match = re.search(r'INR\s([\d,]+\.\d{2})', message)
    date_match = re.search(r'on (\d{2}-[A-Z]{3}-\d{2})', message)
    account_end_match = re.search(r'A/c XX(\d+)', message)
    payer_match = re.search(r'Cr-[^-]+-(.+?)-', message)

    if not (amount_match and date_match and account_end_match):
        return None

    # Clean amount (remove commas)
    amount = amount_match.group(1).replace(',', '')
    date = date_match.group(1).replace('-', '/')
    account_end = account_end_match.group(1)

    if account_end == '5000':
        account = '(p)HDFC'
    elif account_end == '4765':
        account = '(v)HDFC'
    else:
        account = 'Unknown'

    payer = payer_match.group(1).strip() if payer_match else 'Unknown Source'

    return {
        'Date': date,
        'Account': account,
        'Category': 'Salary',
        'Subcategory': '',
        'Note': payer,
        'Amount': amount,
        'Income/Expense': 'Income',
        'Description': ''
    }

def handle_message(update, context):
    user_message = update.message.text
    result = parse_message(user_message)

    if result:
        append_to_excel(result)

        reply = (
            f"💰 *Amount*: ₹{result['Amount']}\n"
            f"📅 *Date*: {result['Date']}\n"
            f"🏦 *Account*: {result['Account']}\n"
            f"📂 *Category*: {result['Category']}\n"
            f"🔖 *Subcategory*: {result['Subcategory']}\n"
            f"📝 *Note*: {result['Note']}\n"
            f"💼 *Type*: {result['Income/Expense']}"
        )

        update.message.reply_text(reply, parse_mode='Markdown')
    else:
        update.message.reply_text("❗ I couldn't parse this message. Please check the format.")

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print("Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
