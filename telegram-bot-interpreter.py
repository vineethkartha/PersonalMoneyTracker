# telegram_bot_interpreter.py

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import ChatAction, InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
import os
import re

from parsers import get_parser
from excel_writer import ExcelWriter
from utils import log_transaction, archive_and_reset_file

# ======================
# GLOBAL CONSTANTS
# ======================
DATA_FILE = 'data/import.tsv'

# Categories and Subcategories (Expandable)
CATEGORIES = {
    "Education": [
        "Bhadra's School",
        "Vasu's school",
        "Academy",
        "co curricular",
        "Textbooks",
        "School supplies"
    ],
    "Entertainment": [
        "Misc",
        "Aquarium",
        "Photography",
        "Movie",
        "Books"
    ],
    "Food and others": [
        "Eating out",
        "Groceries and household items",
        "cook"
    ],
    "Health": [
        "Medicine",
        "Personal care",
        "Hospital",
        "Insurance"
    ],
    "Household": [
        "EMI",
        "Misc",
        "Maintainance",
        "Phone and Internet",
        "Bills"
    ],
    "Other expenses": [
        "Real estate investments",
        "Taxes",
        "PSR",
        "PoARR"
    ],
    "Tour": [
        "Travel",
        "Misc",
        "Accommodation",
        "Food"
    ],
    "Vehicle": [
        "Fuel",
        "Maintainance"
    ],
    "parents & extended family":[""],
    "Gift":[""],
    "shopping":[""]    
}

# ======================
# Setup
# ======================
def cleanMarkdown(text):
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

allowed_user_ids_str = os.getenv("ALLOWED_USER_IDS", "")
ALLOWED_USERS = set(map(int, allowed_user_ids_str.split(","))) if allowed_user_ids_str else set()

excel_writer = ExcelWriter(DATA_FILE)

# ======================
# Telegram Handlers
# ======================
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
            context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_DOCUMENT)
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
            context.user_data['transaction'] = parsed_data

            reply = (
                f"✅ *Transaction Parsed*\n"
                f"💰 *Amount*: ₹{cleanMarkdown(str(parsed_data['Amount']))}\n"
                f"🏦 *Account*: {cleanMarkdown(parsed_data['Account'])}\n"
                f"📂 *Category*: {cleanMarkdown(parsed_data['Category'])}\n"
                f"🗂️ *Subcategory*: {cleanMarkdown(parsed_data['Subcategory'])}\n"
                f"📝 *Note*: {cleanMarkdown(parsed_data['Note'])}\n"
                f"💵 *Type*: {parsed_data['Income/Expense']}\n"
                f"📅 *Date*: {parsed_data['Date']}\n\n"
                f"Do you want to save this?"
            )

            keyboard = [
                [InlineKeyboardButton("✅ Confirm", callback_data='confirm')],
                [InlineKeyboardButton("✏️ Edit", callback_data='edit')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(reply, reply_markup=reply_markup, parse_mode='MarkdownV2')

        else:
            update.message.reply_text("❗Could not parse this transaction. Please review the message format.")

    except Exception as e:
        update.message.reply_text(f"⚠️ Error: {str(e)}")
        log_transaction(user_id, user_name, user_message, f"Error: {str(e)}")

def notify_other_users(context, submitting_user_id, transaction):
    try:
        submitter = context.bot.get_chat(submitting_user_id)
        submitter_name = submitter.first_name
    except Exception:
        submitter_name = "Someone"
    message = (
        f"🔔 *New Transaction Added by *{cleanMarkdown(submitter_name)}\n"
        f"💰 *Amount*: ₹{cleanMarkdown(str(transaction['Amount']))}\n"
        f"🏦 *Account*: {cleanMarkdown(transaction['Account'])}\n"
        f"📂 *Category*: {cleanMarkdown(transaction['Category'])}\n"
        f"🗂️ *Subcategory*: {cleanMarkdown(transaction['Subcategory'])}\n"
        f"📝 *Note*: {cleanMarkdown(transaction['Note'])}\n"
        f"💵 *Type*: {transaction['Income/Expense']}\n"
        f"📅 *Date*: {transaction['Date']}"
    )

    for user_id in ALLOWED_USERS:
        if user_id != submitting_user_id:  # Don't notify the submitting user
            try:
                context.bot.send_message(chat_id=user_id, text=message, parse_mode='MarkdownV2')
            except Exception as e:
                print(f"Failed to send notification to {user_id}: {str(e)}")

                
def button_handler(update, context):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id  # ID of the user who confirmed
    
    if query.data == 'confirm':
        transaction = context.user_data.get('transaction')
        if transaction:
            excel_writer.write_transaction(transaction)
            query.edit_message_text(text="✅ Transaction saved.")
            # Notify other users
            notify_other_users(context, user_id, transaction)
        else:
            query.edit_message_text(text="⚠️ No transaction to save.")

    elif query.data == 'edit':
        keyboard = [[InlineKeyboardButton(cat, callback_data=f"cat_{cat}")] for cat in CATEGORIES.keys()]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="Select a new category:", reply_markup=reply_markup)

    elif query.data.startswith('cat_'):
        selected_category = query.data.replace('cat_', '')
        context.user_data['transaction']['Category'] = selected_category

        subcategories = CATEGORIES[selected_category]
        keyboard = [[InlineKeyboardButton(sub, callback_data=f"sub_{sub}")] for sub in subcategories]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text=f"Category set to *{cleanMarkdown(selected_category)}*\nNow select a subcategory:",
            reply_markup=reply_markup, parse_mode='MarkdownV2')

    elif query.data.startswith('sub_'):
        selected_subcategory = query.data.replace('sub_', '')
        context.user_data['transaction']['Subcategory'] = selected_subcategory

        transaction = context.user_data.get('transaction')
        if transaction:
            excel_writer.write_transaction(transaction)
            query.edit_message_text(
                text=f"✅ Transaction saved with updated category: *{cleanMarkdown(transaction['Category'])}* and subcategory: *{cleanMarkdown(transaction['Subcategory'])}*",
                parse_mode='MarkdownV2')
            # Notify other users
            notify_other_users(context, user_id, transaction)

        else:
            query.edit_message_text(text="⚠️ No transaction to save.")


def summary_handle(update, context):
    user_id = update.effective_user.id
    user_name = update.message.from_user.first_name

    if user_id not in ALLOWED_USERS:
        update.message.reply_text("❌ You are not authorized to request this file.")
        return

    data = excel_writer.read_transactions()
    messages = []
    if len(data) == 0:
        update.message.reply_text("No transactions recorded.\n")
        return
    
    for transaction in data:
        messages.append(
            f"Amount: ₹{cleanMarkdown(str(transaction['Amount']))}\n"
            f"Account: {cleanMarkdown(transaction['Account'])}\n"
            f"Category: {cleanMarkdown(transaction['Category'])}\n"
            f"Subcategory: {cleanMarkdown(transaction['Subcategory'])}\n"
            f"Note: {cleanMarkdown(transaction['Note'])}\n"
            f"Date: {cleanMarkdown(transaction['Date'])}\n\n"
        )

    full_message = '\n'.join(messages)

    print(full_message)

    # Telegram messages have a 4096 character limit, split if needed
    if len(full_message) > 4096:
        for i in range(0, len(full_message), 4096):
            update.message.reply_text(full_message[i:i+4096], parse_mode='MarkdownV2')
    else:
        update.message.reply_text(full_message, parse_mode='MarkdownV2')

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('sendfile', send_file))
    dp.add_handler(CommandHandler('summary', summary_handle))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
