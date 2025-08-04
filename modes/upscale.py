import cv2
from realesrgan import RealESRGANer
import numpy as np, os
from modes.utils import log_event

def is_anime_image(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    return np.mean(hsv[:, :, 1]) > 100 and np.mean(hsv[:, :, 2]) > 130

async def process_upscale(input_path, output_path, scale=4):
    img = cv2.imread(input_path)
    model = "RealESRGAN_x4plus_anime_6B" if is_anime_image(img) else "RealESRGAN_x4plus"
    model_path = f"models/{model}.pth"
    if not os.path.exists(model_path): raise FileNotFoundError(f"❌ Модель {model} не найдена")

    upsampler = RealESRGANer(scale=scale, model_path=model_path)
    result, _ = upsampler.enhance(img)
    cv2.imwrite(output_path, result)
    log_event("upscale.jsonl", {"input": input_path, "model": model, "status": "success"})
