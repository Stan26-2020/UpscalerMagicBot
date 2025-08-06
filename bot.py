import os
import asyncio
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Конфигурация
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Токен не найден! Проверьте переменную BOT_TOKEN в Render")

# Обработчики команд
async def start(update, context):
    await update.message.reply_text("Бот запущен!")

async def error_handler(update, context):
    logger.error(f"Ошибка: {context.error}")

def main():
    # Создаем Application вместо Updater
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    
    # Обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()
