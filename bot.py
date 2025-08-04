import os, time, asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

from modes.upscale import process_upscale
from modes.face_restore import process_face_restore
from modes.illustration import process_illustration
from modes.poster import process_poster

TOKEN = os.getenv("BOT_TOKEN", "fallback-token")
queue = asyncio.Queue()

async def set_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = update.message.text.split()[-1]
    if mode not in ["upscale", "face_restore", "illustration", "poster"]:
        await update.message.reply_text("❌ Неверный режим. Используй /mode upscale и т.п.")
    else:
        context.user_data["mode"] = mode
        await update.message.reply_text(f"✅ Режим установлен: {mode}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    qsize = queue.qsize()
    await update.message.reply_text(f"📦 В очереди: {qsize} задач")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("mode", "upscale")
    await update.message.reply_text(f"📥 Получено изображение. Режим: {mode}")
    await queue.put((update, context))

async def worker():
    while True:
        update, context = await queue.get()
        await update.message.reply_text(f"⚙️ Начинаю обработку...")
        photo = update.message.photo[-1]
        file = await photo.get_file()
        await file.download_to_drive("input.jpg")

        start = time.time()
        try:
            if context.user_data.get("mode") == "face_restore":
                await process_face_restore(update)
            elif context.user_data.get("mode") == "illustration":
                await process_illustration(update)
            elif context.user_data.get("mode") == "poster":
                await process_poster(update)
            else:
                await process_upscale(update)
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")

        end = round(time.time() - start, 2)
        await update.message.reply_text(f"✅ Готово за {end} секунд ⏱️")
        for f in ["input.jpg", "output.jpg"]:
            if os.path.exists(f): os.remove(f)
        queue.task_done()

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("mode", set_mode))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    asyncio.get_event_loop().create_task(worker())
    app.run_polling()

if __name__ == "__main__":
    main()