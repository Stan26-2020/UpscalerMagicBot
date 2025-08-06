import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Отключаем ненужные логи httpx
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")

def start(update, context):
    update.message.reply_text("🤖 Бот работает! Отправьте мне фото")

def handle_photo(update, context):
    update.message.reply_text("📸 Фото получено. Идет обработка...")
    # Здесь будет ваша логика обработки фото
    update.message.reply_text("✅ Обработка завершена")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))
    
    logger.info("Бот запущен в polling-режиме")
    updater.start_polling(
        poll_interval=1.0,
        timeout=10,
        drop_pending_updates=True
    )
    updater.idle()

if __name__ == "__main__":
    if not TOKEN:
        logger.critical("Токен не найден! Задайте BOT_TOKEN в настройках Render")
    else:
        main()
