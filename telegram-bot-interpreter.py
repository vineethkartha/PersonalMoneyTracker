# telegram_bot_interpreter.py

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv
import os

from parser_module import TransactionParser
from excel_writer import ExcelWriter
from logger import log_transaction
import re

# this is to fix the issue Error: Can't parse entities: can't find end of\ the entity starting at byte offset 161
def escape_markdown(text):
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

# Initialize parser, Excel writer, and log file
parser = TransactionParser()
excel_writer = ExcelWriter('data/import.tsv')


def start(update, context):
    update.message.reply_text('Hello! Send me your expense details.')


def handle_message(update, context):
    user_message = update.message.text
    try:
        parsed_data = parser.parse(user_message)
        if parsed_data:
            excel_writer.write_transaction(parsed_data)
            log_transaction(user_message, str(parsed_data))
            reply = (
                f"✅ *Transaction Parsed*\n"
                f"💰 *Amount*: ₹{escape_markdown(str(parsed_data['Amount']))}\n"
                f"🏦 *Account*: {escape_markdown(parsed_data['Account'])}\n"
                f"📂 *Category*: {escape_markdown(parsed_data['Category'])}\n"
                f"🗂️ *Subcategory*: {escape_markdown(parsed_data['Subcategory'])}\n"
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
