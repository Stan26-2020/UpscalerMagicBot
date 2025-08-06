import os
from io import BytesIO
from PIL import Image
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from realesrgan import RealESRGANer
import cv2
import numpy as np

TOKEN = os.getenv('TELEGRAM_TOKEN')

# Инициализация ESRGAN
# Выбор модели (доступны: 2x, 4x, 8x)
upscaler_2x = RealESRGANer(scale=2, model_path='weights/RealESRGAN_x2plus.pth')
upscaler_4x = RealESRGANer(scale=4)  # По умолчанию
upscaler_8x = RealESRGANer(scale=8, model_path='weights/RealESRGAN_x8.pth')

# Добавьте кнопки для выбора масштаба
async def ask_scale(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("2x", callback_data='2x')],
        [InlineKeyboardButton("4x", callback_data='4x')],
        [InlineKeyboardButton("8x", callback_data='8x')]
    ]
    await update.message.reply_text("Выберите масштаб:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_photo(update: Update, context):
    try:
        msg = await update.message.reply_text("🔍 Обрабатываю изображение (это займет 10-30 сек)...")
        
        # Получаем фото
        photo = await update.message.photo[-1].get_file()
        image_stream = BytesIO()
        await photo.download_to_memory(out=image_stream)
        image_stream.seek(0)
        
        # Конвертируем в формат OpenCV
        pil_img = Image.open(image_stream)
        cv_img = np.array(pil_img)
        cv_img = cv2.cvtColor(cv_img, cv2.COLOR_RGB2BGR)
        
        # Улучшаем качество с ESRGAN
        output, _ = upscaler.enhance(cv_img)
        
        # Конвертируем обратно в PIL Image
        output = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
        enhanced_img = Image.fromarray(output)
        
        # Отправляем результат
        result_stream = BytesIO()
        enhanced_img.save(result_stream, format='JPEG', quality=95)
        result_stream.seek(0)
        
        await update.message.reply_photo(
            photo=result_stream,
            caption="✅ Готово! Улучшенная версия (4x)"
        )
        await msg.delete()
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

if __name__ == "__main__":
    main()
