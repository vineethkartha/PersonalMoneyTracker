from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import re
from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

def start(update, context):
    update.message.reply_text('Hello! Send me your expense details.')

def parse_transaction(message):
    # Extract amount (₹ or Rs)
    amount_match = re.search(r'(?:₹|Rs\.?)\s?(\d+(?:\.\d{1,2})?)', message)
    amount = float(amount_match.group(1)) if amount_match else None

    # Determine if it's credit or debit
    if re.search(r'\b(received|credited|income|salary|got|deposit)\b', message, re.I):
        txn_type = 'Credit'
    elif re.search(r'\b(spent|debited|paid|purchase|bought|used)\b', message, re.I):
        txn_type = 'Debit'
    else:
        txn_type = 'Unknown'

    # Try to infer account
    account_keywords = ['HDFC', 'SBI', 'Cash', 'Wallet', 'Credit Card', 'Savings', 'Axis']
    account = next((word for word in account_keywords if word.lower() in message.lower()), 'Unknown')

    # Very basic category guessing
    category_keywords = {
        'food': ['dinner', 'lunch', 'groceries', 'restaurant', 'snacks'],
        'travel': ['uber', 'flight', 'train', 'bus', 'taxi'],
        'bills': ['electricity', 'bill', 'recharge', 'mobile'],
        'shopping': ['amazon', 'flipkart', 'bought', 'purchase'],
        'entertainment': ['movie', 'netflix', 'hotstar']
    }
    category = 'Uncategorized'
    for cat, keywords in category_keywords.items():
        if any(kw in message.lower() for kw in keywords):
            category = cat.capitalize()
            break

    return {
        'amount': amount,
        'type': txn_type,
        'account': account,
        'category': category
    }

def handle_message(update, context):
    user_message = update.message.text
    result = parse_transaction(user_message)

    reply = (
        f"💰 *Amount*: ₹{result['amount']}\n"
        f"📥 *Type*: {result['type']}\n"
        f"🏦 *Account*: {result['account']}\n"
        f"📂 *Category*: {result['category']}"
    )

    update.message.reply_text(reply, parse_mode='Markdown')


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
