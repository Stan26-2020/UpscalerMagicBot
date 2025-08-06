import os
import cv2
import numpy as np
from io import BytesIO
from PIL import Image, ImageEnhance
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

TOKEN = os.getenv('TELEGRAM_TOKEN')

async def start(update: Update, context):
    await update.message.reply_text(
        "📷 Отправьте мне фото, и я улучшу его качество!\n"
        "Поддерживаются JPG/PNG до 10MB."
    )

def enhance_image(input_path):
    """Улучшение изображения с помощью PIL и OpenCV"""
    img = Image.open(input_path)
    
    # Увеличение резкости
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(2.0)
    
    # Улучшение цвета
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.2)
    
    # Увеличение разрешения (2x) через интерполяцию
    width, height = img.size
    img = img.resize((width*2, height*2), Image.LANCZOS)
    
    # Уменьшение шумов через OpenCV
    cv_img = np.array(img)
    cv_img = cv2.fastNlMeansDenoisingColored(cv_img, None, 10, 10, 7, 21)
    
    return Image.fromarray(cv_img)

async def handle_photo(update: Update, context):
    try:
        msg = await update.message.reply_text("🔍 Обрабатываю изображение...")
        
        # Получаем фото
        photo = await update.message.photo[-1].get_file()
        image_stream = BytesIO()
        await photo.download_to_memory(out=image_stream)
        image_stream.seek(0)
        
        # Улучшаем качество
        enhanced_img = enhance_image(image_stream)
        
        # Отправляем результат
        result_stream = BytesIO()
        enhanced_img.save(result_stream, format='JPEG', quality=95)
        result_stream.seek(0)
        
        await update.message.reply_photo(
            photo=result_stream,
            caption="✅ Готово! Улучшенная версия"
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
