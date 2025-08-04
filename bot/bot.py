import os, time, asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import aiohttp

API_TOKEN = os.getenv("TELEGRAM_TOKEN")
API_URL = os.getenv("API_ENDPOINT", "http://localhost:8000/process")
queue = asyncio.Queue()
MODES = ["upscale", "face_restore", "illustration", "poster"]

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

async def worker():
    while True:
        update, context = await queue.get()
        photo = update.message.photo[-1]
        file = await photo.get_file()
        await file.download_to_drive("input.jpg")

        mode = context.user_data.get("mode", "upscale")
        await update.message.reply_text("⚙️ Обработка...")

        try:
            async with aiohttp.ClientSession() as session:
                with open("input.jpg", "rb") as image_file:
                    form = aiohttp.FormData()
                    form.add_field("file", image_file, filename="input.jpg", content_type="image/jpeg")
                    async with session.post(f"{API_URL}/{mode}", data=form) as resp:
                        if resp.status == 200:
                            result = await resp.read()
                            await update.message.reply_photo(result)
                        else:
                            await update.message.reply_text("❌ Ошибка от API")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Ошибка: {str(e)}")

        for path in ["input.jpg", "output.jpg"]:
            if os.path.exists(path): os.remove(path)
        queue.task_done()

def main():
    app = ApplicationBuilder().token(API_TOKEN).build()
    app.add_handler(CommandHandler("mode", set_mode))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    asyncio.get_event_loop().create_task(worker())
    app.run_polling()

if __name__ == "__main__":
    main()
