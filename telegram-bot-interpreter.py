# telegram_bot_interpreter.py

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ChatAction
from dotenv import load_dotenv
import os

from parsers import get_parser
from excel_writer import ExcelWriter
from utils import log_transaction, archive_and_reset_file
import re

# GLOBAL CONSTANTS
DATA_FILE = 'data/import.tsv'

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
excel_writer = ExcelWriter(DATA_FILE)


def start(update, context):
    update.message.reply_text('Hello! Send me your expense details.')

def send_file(update, context):
    user_id = update.effective_user.id
    user_name = update.message.from_user.first_name
    if user_id not in ALLOWED_USERS:
        update.message.reply_text("❌ You are not authorized to request this file.")
        return

    archived_file = archive_and_reset_file(DATA_FILE)
    file_sent_status = ''
    if archived_file:
        try:
            # Indicate file is being uploaded
            context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_DOCUMENT)

            # Send the archived file
            context.bot.send_document(chat_id=update.effective_chat.id, document=open(archived_file, 'rb'))
            update.message.reply_text("✅ File sent and reset completed.")
            file_sent_status = archived_file + ' sent'
        except Exception as e:
            update.message.reply_text(f"⚠️ Error sending file: {str(e)}")
            file_sent_status = str(e)
    else:
        file_sent_status = "No transactions to report."
        update.message.reply_text(file_sent_status)
    print(file_sent_status)
    log_transaction(user_id, user_name, 'File Requested', file_sent_status)



def handle_message(update, context):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    
    if user_id not in ALLOWED_USERS:
        update.message.reply_text("🚫 Access denied. You are not authorized to use this bot.")
        return

    user_message = update.message.text
    parser = get_parser(user_message)
    try:
        parsed_data = parser.parse(user_message)
        if parsed_data:
            excel_writer.write_transaction(parsed_data)
            log_transaction(user_id, user_name, user_message, str(parsed_data))
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
        print(reply.split('\n')[0])
        update.message.reply_text(reply, parse_mode='MarkdownV2')

    except Exception as e:
        update.message.reply_text(f"⚠️ Error: {str(e)}")
        log_transaction(user_id, user_name,user_message, f"Error: {str(e)}")


def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    # This is to receive the import.tsv file
    dp.add_handler(CommandHandler('sendfile', send_file))
    
    print("Bot is running...")
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
