import os, asyncio, uuid
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import aiohttp

API_TOKEN = os.getenv("TELEGRAM_TOKEN")
API_URL = os.getenv("API_ENDPOINT", "http://localhost:8000/process")
MODES = ["upscale", "face_restore", "illustration", "poster"]
WORKER_COUNT = 3
queue = asyncio.Queue()

async def set_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = update.message.text.split()[-1]
    if mode not in MODES:
        await update.message.reply_text("❌ Неверный режим. Используй /mode upscale, /mode poster и т.п.")
    else:
        context.user_data["mode"] = mode
        await update.message.reply_text(f"✅ Режим установлен: {mode}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"📦 В очереди: {queue.qsize()} задач")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("mode", "upscale")
    await update.message.reply_text(f"📥 Получено изображение. Режим: {mode}")
    await queue.put((update, context))

async def worker(worker_id):
    while True:
        update, context = await queue.get()
        try:
            photo = update.message.photo[-1]
            file = await photo.get_file()
            filename = f"{uuid.uuid4().hex}.jpg"
            await file.download_to_drive(filename)

            mode = context.user_data.get("mode", "upscale")
            await update.message.reply_text("⚙️ Обработка...")

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                with open(filename, "rb") as image_file:
                    form = aiohttp.FormData()
                    form.add_field("file", image_file, filename=filename, content_type="image/jpeg")
                    async with session.post(f"{API_URL}/{mode}", data=form) as resp:
                        if resp.status == 200:
                            result = await resp.read()
                            await update.message.reply_photo(result)
                        else:
                            await update.message.reply_text(f"❌ Ошибка от API: {resp.status}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Ошибка: {str(e)}")
        finally:
            if os.path.exists(filename):
                os.remove(filename)
            queue.task_done()

def main():
    app = ApplicationBuilder().token(API_TOKEN).build()
    app.add_handler(CommandHandler("mode", set_mode))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    loop = asyncio.get_event_loop()
    for i in range(WORKER_COUNT):
        loop.create_task(worker(i))

    app.run_polling()

if __name__ == "__main__":
    main()
