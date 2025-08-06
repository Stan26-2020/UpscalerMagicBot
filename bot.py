import os
import logging
import httpx
from io import BytesIO
from enum import Enum
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
    ConversationHandler
)

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
TOKEN = os.getenv('TELEGRAM_TOKEN')
MAX_SIZE = 5 * 1024 * 1024  # 5MB

# Ключи API (задаются в .env)
API_KEYS = {
    'UPSCALE_MEDIA': os.getenv('UPSCALE_API_KEY'),
    'DEEP_IMAGE': os.getenv('DEEP_IMAGE_API_KEY'),
    'LETS_ENHANCE': os.getenv('LETS_ENHANCE_API_KEY')
}

# Состояния для ConversationHandler
CHOOSING_API, PROCESSING = range(2)

class ApiService(Enum):
    UPSCALE_MEDIA = {
        'name': 'Upscale Media',
        'url': 'https://api.upscale.media/v1/image',
        'headers': lambda key: {"Authorization": f"Bearer {key}"},
        'files_param': "image"
    }
    DEEP_IMAGE = {
        'name': 'Deep Image AI',
        'url': 'https://api.deep-image.ai/process',
        'headers': lambda _: {},
        'files_param': "image",
        'data': {"mode": "quality"}
    }
    LETS_ENHANCE = {
        'name': 'Let's Enhance',
        'url': 'https://api.letsenhance.io/enhance',
        'headers': lambda key: {"Authorization": f"Bearer {key}"},
        'files_param': "image"
    }

class ImageProcessor:
    """Класс для обработки изображений через различные API"""
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.current_api = None

    async def enhance_image(self, image_bytes: bytes, api_service: ApiService) -> BytesIO:
        """Улучшение качества изображения через выбранный API"""
        self.current_api = api_service
        config = api_service.value
        
        if not API_KEYS.get(api_service.name):
            logger.error(f"No API key for {api_service.name}")
            return None

        try:
            files = {config['files_param']: ("photo.jpg", image_bytes)}
            data = config.get('data', {})
            
            response = await self.client.post(
                config['url'],
                files=files,
                data=data,
                headers=config['headers'](API_KEYS[api_service.name])
            )
            
            if response.status_code == 200:
                return BytesIO(response.content)
            
            logger.error(f"{api_service.name} API error: {response.status_code}")
        
        except Exception as e:
            logger.error(f"{api_service.name} connection error: {e}")
        
        return None

# Инициализация процессора
processor = ImageProcessor()

async def start(update: Update, context: CallbackContext):
    """Обработчик команды /start"""
    await update.message.reply_text(
        "🌟 Добро пожаловать в Image Enhancer Bot!\n\n"
        "Я могу улучшить качество ваших фотографий с помощью разных нейросетевых API.\n\n"
        "Отправьте мне фотографию, и я предложу варианты улучшения.\n"
        "Поддерживаются JPG/PNG до 5MB.\n\n"
        "Примерное время обработки: 10-30 секунд"
    )
    return CHOOSING_API

async def handle_photo(update: Update, context: CallbackContext):
    """Обработчик входящих фото"""
    try:
        # Проверка размера файла
        photo = update.message.photo[-1]
        if photo.file_size > MAX_SIZE:
            await update.message.reply_text("⚠️ Файл слишком большой (максимум 5MB)")
            return ConversationHandler.END

        # Сохраняем фото в контексте
        context.user_data['photo'] = photo
        context.user_data['photo_file'] = await photo.get_file()
        
        # Предлагаем выбор API
        buttons = [
            [f"{service.value['name']} ({service.name})"] for service in ApiService 
            if API_KEYS.get(service.name)
        ]
        
        if not buttons:
            await update.message.reply_text("❌ Нет доступных API сервисов")
            return ConversationHandler.END
            
        await update.message.reply_text(
            "🔍 Выберите сервис для улучшения качества:",
            reply_markup={
                'keyboard': buttons,
                'resize_keyboard': True,
                'one_time_keyboard': True
            }
        )
        
        return PROCESSING

    except Exception as e:
        logger.error(f"Error processing photo: {e}")
        await update.message.reply_text("⚠️ Произошла ошибка")
        return ConversationHandler.END

async def process_with_api(update: Update, context: CallbackContext):
    """Обработка выбранного API"""
    try:
        choice = update.message.text
        selected_api = None
        
        # Определяем выбранный API
        for api in ApiService:
            if api.value['name'] in choice:
                selected_api = api
                break
        
        if not selected_api:
            await update.message.reply_text("❌ Неверный выбор сервиса")
            return ConversationHandler.END
        
        # Уведомление о начале обработки
        msg = await update.message.reply_text(
            f"🔄 Обработка с помощью {selected_api.value['name']}..."
        )
        
        # Скачивание фото
        photo_file = context.user_data['photo_file']
        image_bytes = await photo_file.download_as_bytearray()
        
        # Улучшение качества
        enhanced_image = await processor.enhance_image(image_bytes, selected_api)
        
        if enhanced_image:
            # Отправка результата
            await update.message.reply_photo(
                photo=enhanced_image,
                caption=f"✅ Готово! Обработано с помощью {selected_api.value['name']}"
            )
        else:
            await update.message.reply_text(
                f"❌ Не удалось обработать с помощью {selected_api.value['name']}"
            )
        
        # Удаление уведомления
        await msg.delete()
        
    except Exception as e:
        logger.error(f"Error in API processing: {e}")
        await update.message.reply_text("⚠️ Произошла ошибка при обработке")
    
    finally:
        # Очистка данных пользователя
        context.user_data.clear()
        return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext):
    """Отмена операции"""
    await update.message.reply_text("Операция отменена")
    context.user_data.clear()
    return ConversationHandler.END

def main():
    """Запуск бота"""
    try:
        logger.info("Starting bot...")
        
        # Создание и настройка приложения
        app = Application.builder().token(TOKEN).build()
        
        # Настройка ConversationHandler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", start),
                         MessageHandler(filters.PHOTO, handle_photo)],
            states={
                CHOOSING_API: [
                    MessageHandler(filters.PHOTO, handle_photo)
                ],
                PROCESSING: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, process_with_api)
                ]
            },
            fallbacks=[CommandHandler("cancel", cancel)]
        )
        
        app.add_handler(conv_handler)
        
        # Запуск бота
        logger.info("Bot is running...")
        app.run_polling()
        
    except Exception as e:
        logger.critical(f"Bot failed: {e}")

if __name__ == "__main__":
    main()
