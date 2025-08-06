#!/bin/bash
# Установка Real-ESRGAN для Render.com (оптимизированная CPU-версия)
set -euo pipefail  # Безопасный режим выполнения

echo "🔄 Обновление пакетов и установка минимальных зависимостей..."
apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3-pip \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

echo "📦 Клонирование Real-ESRGAN (только необходимые файлы)..."
git clone --depth=1 --branch=master --single-branch \
    https://github.com/xinntao/Real-ESRGAN.git \
    && cd Real-ESRGAN

echo "🐍 Установка Python-зависимостей (CPU-версии)..."
pip install --no-cache-dir \
    torch==2.2.1 --index-url https://download.pytorch.org/whl/cpu \
    opencv-python-headless==4.9.0.80 \
    -r requirements.txt

echo "⚙️ Установка Real-ESRGAN в режиме разработки..."
python setup.py develop

echo "📥 Загрузка моделей (только x4plus)..."
mkdir -p weights
wget -q --show-progress \
    https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth \
    -P weights

# Очистка кеша
echo "🧹 Очистка ненужных файлов..."
find . -type d -name "__pycache__" -exec rm -rf {} +
rm -rf .git

echo -e "\n✅ Установка завершена!\n"
echo "Используемые модели:"
ls -lh weights/
