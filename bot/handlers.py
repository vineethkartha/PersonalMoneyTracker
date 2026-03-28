# bot/handlers.py

"""
Telegram Bot Command and Message Handlers (Updated for v20+).
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from bot.auth import ALLOWED_USERS
from bot.categories import CATEGORIES
from bot.notifications import notify_other_users
from utils import cleanMarkdown, log_transaction, archive_and_reset_file

from excel_writer import ExcelWriter
from parsers import get_parser

# Excel data file
DATA_FILE = 'data/import.tsv'
excel_writer = ExcelWriter(DATA_FILE)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message to the user."""
    await update.message.reply_text('Hello! Send me your expense details.')

async def send_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the archived transaction file to the user if authorized."""
    user_id = update.effective_user.id
    user_name = update.message.from_user.first_name

    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("❌ You are not authorized to request this file.")
        return

    archived_file = archive_and_reset_file(DATA_FILE)
    file_sent_status = ''

    if archived_file:
        try:
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_DOCUMENT)
            with open(archived_file, 'rb') as doc:
                await context.bot.send_document(chat_id=update.effective_chat.id, document=doc)
            await update.message.reply_text("✅ File sent and reset completed.")
            file_sent_status = archived_file + ' sent'
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error sending file: {str(e)}")
            file_sent_status = str(e)
    else:
        file_sent_status = "No transactions to report."
        await update.message.reply_text(file_sent_status)

    print(file_sent_status)
    log_transaction(user_id, user_name, 'File Requested', file_sent_status)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Parse and process incoming messages as transaction data."""
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("🚫 Access denied. You are not authorized to use this bot.")
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
                [InlineKeyboardButton("✏️ Edit", callback_data='edit')],
                [InlineKeyboardButton("🚫 Cancel", callback_data='cancel')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(reply, reply_markup=reply_markup, parse_mode='MarkdownV2')
        else:
            await update.message.reply_text("❗Could not parse this transaction. Please review the message format.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {str(e)}")
        log_transaction(user_id, user_name, user_message, f"Error: {str(e)}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button interactions for confirmation and editing."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == 'confirm':
        transaction = context.user_data.get('transaction')
        if transaction:
            excel_writer.write_transaction(transaction)
            await query.edit_message_text(text="✅ Transaction saved.")
            await notify_other_users(context, user_id, transaction)
        else:
            await query.edit_message_text(text="⚠️ No transaction to save.")

    elif query.data == 'edit':
        keyboard = [[InlineKeyboardButton(cat, callback_data=f"cat_{cat}")] for cat in CATEGORIES.keys()]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Select a new category:", reply_markup=reply_markup)

    elif query.data == 'cancel':
        context.user_data.pop('transaction', None)
        try:
            await query.edit_message_text("❌ Transaction cancelled.")
        except:
            await query.message.reply_text("❌ Transaction cancelled.")
        return

    elif query.data.startswith('cat_'):
        selected_category = query.data.replace('cat_', '')
        context.user_data['transaction']['Category'] = selected_category
        subcategories = CATEGORIES[selected_category]

        if subcategories != ['']:
            keyboard = [[InlineKeyboardButton(sub, callback_data=f"sub_{sub}")] for sub in subcategories]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text=f"Category set to *{cleanMarkdown(selected_category)}*\nNow select a subcategory:",
                reply_markup=reply_markup, parse_mode='MarkdownV2')
        else:
            context.user_data['transaction']['Subcategory'] = ""
            transaction = context.user_data.get('transaction')
            excel_writer.write_transaction(transaction)
            await query.edit_message_text(
                text=f"✅ Transaction saved with category: *{cleanMarkdown(selected_category)}*",
                parse_mode='MarkdownV2')
            await notify_other_users(context, user_id, transaction)

    elif query.data.startswith('sub_'):
        selected_subcategory = query.data.replace('sub_', '')
        context.user_data['transaction']['Subcategory'] = selected_subcategory
        transaction = context.user_data.get('transaction')
        if transaction:
            excel_writer.write_transaction(transaction)
            await query.edit_message_text(
                text=f"✅ Transaction saved with updated category: *{cleanMarkdown(transaction['Category'])}* and subcategory: *{cleanMarkdown(transaction['Subcategory'])}*",
                parse_mode='MarkdownV2')
            await notify_other_users(context, user_id, transaction)
        else:
            await query.edit_message_text(text="⚠️ No transaction to save.")

async def summary_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a summary of all recorded transactions to the user."""
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("❌ You are not authorized to request this file.")
        return

    data = excel_writer.read_transactions()
    if not data:
        await update.message.reply_text("No transactions recorded.\n")
        return

    summary_text = "📊 *Transaction Summary:*\n\n"
    for transaction in data:
        summary_text += (
            f"💰 ₹{cleanMarkdown(str(transaction['Amount']))} | "
            f"📂 {cleanMarkdown(transaction['Category'])}\n"
        )
    
    await update.message.reply_text(summary_text, parse_mode='MarkdownV2')
