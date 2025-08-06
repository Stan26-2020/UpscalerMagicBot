import os
import logging
import threading
import time
from queue import Queue
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext
)

# --- Настройка ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ Токен не найден! Задайте BOT_TOKEN в настройках Render")

# --- Очередь задач ---
task_queue = Queue()

# --- Воркеры ---
def worker():
    while True:
        try:
            update, context = task_queue.get()
            file = update.message.photo[-1].get_file()
            
            update.message.reply_text("⏳ Обрабатываю изображение...")
            time.sleep(2)  # Имитация обработки
            
            update.message.reply_text("✅ Готово!")
            task_queue.task_done()
            
        except Exception as e:
            logger.error(f"Ошибка воркера: {e}")
            update.message.reply_text("⚠️ Ошибка обработки")

# --- Обработчики ---
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "📸 Бот для обработки фото\n"
        "Просто отправьте мне изображение!"
    )

def handle_photo(update: Update, context: CallbackContext):
    task_queue.put((update, context))
    update.message.reply_text("📥 Задача добавлена в очередь")

# --- Запуск ---
def main():
    # Запускаем 3 воркера
    for _ in range(3):
        threading.Thread(target=worker, daemon=True).start()

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))
    
    logger.info("Бот запущен")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
