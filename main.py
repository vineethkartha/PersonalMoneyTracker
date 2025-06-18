from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from dotenv import load_dotenv
load_dotenv()

import os
from bot.handlers import start, send_file, handle_message, button_handler, summary_handle



TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

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
