import os
import asyncio
import uuid
import logging
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import aiohttp
from aiohttp import FormData, ClientTimeout

# --- Конфигурация ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Настройки из переменных окружения
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Токен бота не найден!")

API_URL = os.getenv("API_URL", "")
WEBHOOK_MODE = os.getenv("WEBHOOK_MODE", "false").lower() == "true"
SECRET_TOKEN = os.getenv("SECRET_TOKEN", "")

# Константы
MODES = ["upscale", "face_restore", "illustration", "poster"]
WORKER_COUNT = int(os.getenv("WORKER_COUNT", 3))
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
API_TIMEOUT = 30  # seconds

# Глобальная очередь
queue = asyncio.Queue()

# --- Обработчики команд ---
async def set_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        mode = context.args[0] if context.args else "upscale"
        if mode not in MODES:
            await update.message.reply_text(
                "❌ Неверный режим. Доступные режимы:\n" + 
                "\n".join(f"/mode {m}" for m in MODES)
            )
            return
        
        context.user_data["mode"] = mode
        await update.message.reply_text(f"✅ Режим установлен: {mode}")
    except Exception as e:
        logger.error(f"Error in set_mode: {e}")
        await update.message.reply_text("⚠️ Произошла ошибка при установке режима")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📊 Статус:\n"
        f"• В очереди: {queue.qsize()} задач\n"
        f"• Текущий режим: {context.user_data.get('mode', 'upscale')}"
    )

# --- Обработка изображений ---
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        photo = update.message.photo[-1]
        if photo.file_size > MAX_FILE_SIZE:
            await update.message.reply_text("❌ Файл слишком большой (макс. 10MB)")
            return

        mode = context.user_data.get("mode", "upscale")
        logger.info(f"New photo received in {mode} mode")
        
        await update.message.reply_text(f"📥 Изображение принято. Режим: {mode}")
        await queue.put((update, context))
    except Exception as e:
        logger.error(f"Error in handle_photo: {e}")
        await update.message.reply_text("⚠️ Ошибка при обработке изображения")

# --- Worker-ы для обработки очереди ---
async def worker(worker_id: int):
    logger.info(f"Worker {worker_id} started")
    async with aiohttp.ClientSession(timeout=ClientTimeout(total=API_TIMEOUT)) as session:
        while True:
            try:
                update, context = await queue.get()
                filename = f"temp_{uuid.uuid4().hex}.jpg"
                
                try:
                    # Скачивание фото
                    photo = update.message.photo[-1]
                    file = await context.bot.get_file(photo.file_id)
                    await file.download_to_drive(filename)
                    
                    # Подготовка запроса к API
                    mode = context.user_data.get("mode", "upscale")
                    form = FormData()
                    form.add_field(
                        "file",
                        open(filename, "rb"),
                        filename=filename,
                        content_type="image/jpeg"
                    )
                    
                    await update.message.reply_text("⚙️ Обрабатываю изображение...")
                    
                    # Отправка в API
                    if not API_URL:
                        raise ValueError("API_URL не задан")
                        
                    async with session.post(
                        f"{API_URL}/{mode}",
                        data=form
                    ) as response:
                        if response.status == 200:
                            result = await response.read()
                            await update.message.reply_photo(result)
                            logger.info(f"Worker {worker_id}: Image processed successfully")
                        else:
                            error = await response.text()
                            await update.message.reply_text(f"❌ Ошибка API: {error}")
                            logger.error(f"API error: {error}")
                            
                except asyncio.TimeoutError:
                    await update.message.reply_text("⌛ Таймаут при обработке изображения")
                    logger.warning(f"Worker {worker_id}: Timeout occurred")
                    
                except Exception as e:
                    await update.message.reply_text(f"⚠️ Ошибка: {str(e)}")
                    logger.error(f"Worker {worker_id} error: {e}")
                    
                finally:
                    # Очистка временных файлов
                    try:
                        if os.path.exists(filename):
                            os.remove(filename)
                    except:
                        pass
                    
                    queue.task_done()
                    
            except Exception as e:
                logger.critical(f"Worker {worker_id} crashed: {e}")

# --- Инициализация приложения ---
def setup_application():
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Регистрация обработчиков
    app.add_handler(CommandHandler("mode", set_mode))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    return app

def run_workers():
    """Запуск worker'ов в отдельном event loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    for i in range(WORKER_COUNT):
        asyncio.create_task(worker(i))
    return loop

# --- Главная функция ---
def main():
    worker_loop = run_workers()
    app = setup_application()
    
    try:
        if WEBHOOK_MODE:
            PORT = int(os.getenv("PORT", 5000))
            app.run_webhook(
                listen="0.0.0.0",
                port=PORT,
                webhook_url="https://upscalermagicbot.onrender.com",
                secret_token=SECRET_TOKEN
            )
        else:
            app.run_polling(drop_pending_updates=True)
    except Exception as e:
        logger.critical(f"Application failed: {e}")
    finally:
        worker_loop.close()

if __name__ == "__main__":
    main()
