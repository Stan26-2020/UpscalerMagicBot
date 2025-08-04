import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from PIL import Image
import torch
import cv2
import numpy as np
import subprocess

TOKEN = os.getenv("BOT_TOKEN", "fallback-token")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пришли мне фото, и я его апскейлю 🔧")

def upscale_image(input_path, output_path):
    model_path = "RealESRGAN_x4.pth"
    if not os.path.exists(model_path):
        subprocess.run(["wget", "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4.pth"])

    from realesrgan import RealESRGANer
    upsampler = RealESRGANer(
        scale=4,
        model_path=model_path,
        model=None,
        tile=0,
        tile_pad=10,
        pre_pad=0,
        half=False
    )
    img = cv2.imread(input_path, cv2.IMREAD_COLOR)
    output, _ = upsampler.enhance(img)
    cv2.imwrite(output_path, output)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    await file.download_to_drive("input.jpg")

    await update.message.reply_text("Обрабатываю изображение... ⏳")
    upscale_image("input.jpg", "output.jpg")
    await update.message.reply_photo(photo=open("output.jpg", "rb"), caption="Вот улучшенная версия!")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

if __name__ == "__main__":
    main()
