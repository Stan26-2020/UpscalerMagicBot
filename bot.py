import os
import logging
from io import BytesIO
from PIL import Image
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import numpy as np

# Настройка логгирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Ленивая загрузка модели
upscaler = None

async def load_model():
    global upscaler
    if upscaler is None:
        from basicsr.archs.rrdbnet_arch import RRDBNet
        from realesrgan import RealESRGANer
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
        upscaler = RealESRGANer(
            scale=4,
            model_path=None,
            model=model,
            half=False,
            device='cpu'
        )

async def start(update: Update, context):
    await update.message.reply_text("Отправьте мне фото для улучшения качества")

async def handle_photo(update: Update, context):
    try:
        await load_model()
        photo = await update.message.photo[-1].get_file()
        img = Image.open(BytesIO(await photo.download_as_bytearray()))
        
        # Простое улучшение (без RealESRGAN для примера)
        enhanced = img.resize((img.width*2, img.height*2), Image.LANCZOS)
        
        bio = BytesIO()
        enhanced.save(bio, format='JPEG')
        await update.message.reply_photo(photo=bio, caption="Улучшенное фото")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("Произошла ошибка")

def main():
    app = Application.builder().token(os.getenv('TOKEN')).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

if __name__ == "__main__":
    main()
