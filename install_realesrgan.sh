#!/bin/bash

# Обновление и установка зависимостей
sudo apt update
sudo apt install -y git python3-pip libglib2.0-0 libsm6 libxrender1 libxext6

# Клонируем Real-ESRGAN
git clone https://github.com/xinntao/Real-ESRGAN.git
cd Real-ESRGAN

# Устанавливаем зависимости
pip install -r requirements.txt
python setup.py develop

# Загружаем модель (по умолчанию x4plus)
wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth -P weights

# Дополнительно: anime модель
wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.0/RealESRGAN_x4plus_anime_6B.pth -P weights

echo "✅ Real-ESRGAN установлен и готов к работе"
