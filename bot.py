import os
import logging
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    Filters
)

# Настройка логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Токен не найден! Проверьте BOT_TOKEN в настройках Render")

def start(update: Update, context: CallbackContext):
    update.message.reply_text("✅ Бот успешно запущен!")

def main():
    try:
        updater = Updater(TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        
        dispatcher.add_handler(CommandHandler("start", start))
        
        logger.info("Бот запускается...")
        updater.start_polling()
        updater.idle()
        
    except Exception as e:
        logger.critical(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
