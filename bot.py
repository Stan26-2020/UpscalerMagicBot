import os
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN", "your-telegram-bot-token")  # Задай переменную BOT_TOKEN в Render Dashboard

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот для апскейлинга изображений. Пришли мне фото 📸")

# Обработка изображений
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]  # Самое большое фото
    file = await photo.get_file()
    file_path = "input.jpg"
    await file.download_to_drive(file_path)

    # Заглушка: апскейлинг пока не выполняется — просто пересылаем
    await update.message.reply_photo(photo=open(file_path, "rb"), caption="Вот твоё изображение. Апскейлинг скоро ✨")

# Запуск приложения
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
