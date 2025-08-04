import os
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InputFile
from PIL import Image
from realesrgan import RealESRGANer
import torch

# Настройки бота
TOKEN = ""
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Инициализация модели ESRGAN
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = RealESRGANer(device=device, scale=4)  # Модель для 4x апскейла

# Папка для загрузок
os.makedirs("downloads", exist_ok=True)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("🔍 Привет! Загрузи изображение, и я увеличу его качество в 2-4 раза!")

@dp.message_handler(content_types=['photo'])
async def handle_image(message: types.Message):
    user_id = message.from_user.id
    file_id = message.photo[-1].file_id
    file_path = f"downloads/{user_id}_input.jpg"
    
    # Скачиваем фото
    await message.photo[-1].download(file_path)
    await message.reply("🔄 Обрабатываю изображение...")

    # Апскейл
    try:
        img = Image.open(file_path)
        output = model.enhance(img, outscale=4)[0]  # Увеличиваем в 4 раза
        output_path = f"downloads/{user_id}_output.png"
        output.save(output_path)

        # Отправляем результат
        with open(output_path, 'rb') as photo:
            await message.reply_photo(photo, caption="✅ Готово! Улучшенное изображение (4x)")
    except Exception as e:
        await message.reply(f"❌ Ошибка: {e}")

if __name__ == '__main__':

    executor.start_polling(dp, skip_updates=True)
