# telegram_bot_interpreter.py

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv
import os

from parsers import get_parser
from excel_writer import ExcelWriter
from utils import log_transaction
import re

# this is to fix the issue Error: Can't parse entities: can't find end of\ the entity starting at byte offset 161
def cleanMarkdown(text):
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

# get the list of the allowed users
allowed_user_ids_str = os.getenv("ALLOWED_USER_IDS", "")
ALLOWED_USERS = set(map(int, allowed_user_ids_str.split(",")))if allowed_user_ids_str else set()

# Initialize parser, Excel writer, and log file
excel_writer = ExcelWriter('data/import.tsv')


def start(update, context):
    update.message.reply_text('Hello! Send me your expense details.')


def handle_message(update, context):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.username
    
    if user_id not in ALLOWED_USERS:
        update.message.reply_text("🚫 Access denied. You are not authorized to use this bot.")
        return

    user_message = update.message.text
    parser = get_parser(user_message)
    try:
        parsed_data = parser.parse(user_message)
        if parsed_data:
            excel_writer.write_transaction(parsed_data)
            log_transaction(user_id, user_name user_message, str(parsed_data))
            reply = (
                f"✅ *Transaction Parsed*\n"
                f"💰 *Amount*: ₹{cleanMarkdown(str(parsed_data['Amount']))}\n"
                f"🏦 *Account*: {cleanMarkdown(parsed_data['Account'])}\n"
                f"📂 *Category*: {cleanMarkdown(parsed_data['Category'])}\n"
                f"🗂️ *Subcategory*: {cleanMarkdown(parsed_data['Subcategory'])}\n"
                f"📝 *Note*: {parsed_data['Note']}\n"
                f"💵 *Type*: {parsed_data['Income/Expense']}\n"
                f"📅 *Date*: {parsed_data['Date']}"
            )
        else:
            reply = "❗Could not parse this transaction. Please review the message format."
        print(reply)
        update.message.reply_text(reply, parse_mode='MarkdownV2')

    except Exception as e:
        update.message.reply_text(f"⚠️ Error: {str(e)}")
        log_transaction(user_message, f"Error: {str(e)}")


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
