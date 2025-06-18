from bot.auth import ALLOWED_USERS
from utils import cleanMarkdown

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
        if user_id != submitting_user_id:
            try:
                context.bot.send_message(chat_id=user_id, text=message, parse_mode='MarkdownV2')
            except Exception as e:
                print(f"Failed to send notification to {user_id}: {str(e)}")
