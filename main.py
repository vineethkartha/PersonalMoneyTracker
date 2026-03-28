from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from dotenv import load_dotenv
load_dotenv()

import os
from bot.handlers import start, send_file, handle_message, button_handler, summary_handle
from category_predictor import get_predictor


TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def main():
    dp = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('sendfile', send_file))
    dp.add_handler(CommandHandler('summary', summary_handle))
    dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    dp.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    predictor = get_predictor()
    print("Category Predictor loaded")
    dp.run_polling()

if __name__ == '__main__':
    main()
