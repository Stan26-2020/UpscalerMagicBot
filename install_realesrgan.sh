#!/bin/bash
pyenv install 3.12.3
pyenv global 3.12.3
pip install -r requirements.txt
git lfs install

# Скачивание моделей SD и ControlNet
git clone https://huggingface.co/runwayml/stable-diffusion-v1-5 models/sd15
git clone https://huggingface.co/lllyasviel/sd-controlnet-canny models/controlnet_canny

# Реал-ESRGAN
wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4.pth