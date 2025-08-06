import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Отключаем лишние логи httpx
logging.getLogger("httpx").setLevel(logging.WARNING)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    logger.error("Токен бота не найден!")
    exit(1)

def start(update, context):
    """Обработчик команды /start"""
    update.message.reply_text("🤖 Бот активен! Отправьте мне фото")

def handle_photo(update, context):
    """Обработчик фотографий"""
    try:
        photo = update.message.photo[-1]
        update.message.reply_text("📸 Фото получено, начинаю обработку...")
        
        # Здесь будет ваша логика обработки
        # Например: file = photo.get_file(); file.download('image.jpg')
        
        update.message.reply_text("✅ Обработка завершена")
    except Exception as e:
        logger.error(f"Ошибка обработки фото: {e}")
        update.message.reply_text("⚠️ Произошла ошибка при обработке")

def main():
    """Основная функция"""
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))
    
    logger.info("Бот запущен в режиме polling")
    updater.start_polling(
        poll_interval=3.0,  # Увеличен интервал опроса
        timeout=15,
        drop_pending_updates=True
    )
    updater.idle()

if __name__ == "__main__":
    main()
