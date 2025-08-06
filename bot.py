import os
import logging
from io import BytesIO
import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Настройка
load_dotenv()
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TELEGRAM_TOKEN')
UPSCALE_API_KEY = os.getenv('UPSCALE_API_KEY')
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

class ImageUpscaler:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def upscale(self, image_bytes: bytes) -> BytesIO:
        """Улучшение качества через API"""
        try:
            response = await self.client.post(
                "https://api.upscale.media/v1/image",
                files={"image": ("photo.jpg", image_bytes)},
                headers={"Authorization": f"Bearer {UPSCALE_API_KEY}"}
            )
            if response.status_code == 200:
                return BytesIO(response.content)
        except Exception as e:
            logger.error(f"API error: {e}")
        return None

async def start(update: Update, context):
    await update.message.reply_text(
        "📷 Отправьте мне фото для улучшения качества!\n"
        "⚠️ Максимальный размер: 5MB\n"
        "⏱ Обработка занимает 10-20 секунд"
    )

async def handle_photo(update: Update, context):
    try:
        if update.message.photo[-1].file_size > MAX_FILE_SIZE:
            await update.message.reply_text("❌ Файл слишком большой (макс. 5MB)")
            return

        msg = await update.message.reply_text("🔍 Обрабатываю изображение...")
        photo = await update.message.photo[-1].get_file()
        image_bytes = await photo.download_as_bytearray()

        upscaler = ImageUpscaler()
        enhanced = await upscaler.upscale(image_bytes)

        if enhanced:
            await update.message.reply_photo(
                photo=enhanced,
                caption="✅ Готово! Улучшенная версия"
            )
        else:
            await update.message.reply_text("❌ Ошибка обработки, попробуйте позже")

        await msg.delete()

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("⚠️ Произошла ошибка")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    logger.info("Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
