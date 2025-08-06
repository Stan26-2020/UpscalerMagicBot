import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
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

# Хендлер команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Бот успешно запущен!")

def main():
    try:
        app = ApplicationBuilder().token(TOKEN).build()

        app.add_handler(CommandHandler("start", start))

        logger.info("Бот запускается...")
        app.run_polling()

    except Exception as e:
        logger.critical(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
