import cv2
import numpy as np
import os
import logging
from typing import Optional, Tuple
from datetime import datetime
from realesrgan import RealESRGANer
from modes.utils import ImageUtils, Logger, ModelLoader

logger = logging.getLogger(__name__)

class ImageUpscaler:
    """Класс для апскейла изображений с Real-ESRGAN"""

    def __init__(self, models_dir: str = "weights", device: str = "cpu"):
        self.utils = ImageUtils()
        self.logger = Logger()
        self.models_dir = models_dir
        self.device = device
        self.upsamplers = {}
        self.temp_files = []

    async def initialize_models(self):
        """Предварительная загрузка моделей"""
        try:
            os.makedirs(self.models_dir, exist_ok=True)
            
            models = {
                "RealESRGAN_x4plus": {
                    "url": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",
                    "scale": 4
                },
                "RealESRGAN_x4plus_anime_6B": {
                    "url": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.0/RealESRGAN_x4plus_anime_6B.pth",
                    "scale": 4
                }
            }

            for model_name, config in models.items():
                model_path = os.path.join(self.models_dir, f"{model_name}.pth")
                if not os.path.exists(model_path):
                    await ModelLoader.download_model(config["url"], model_path)
                
                self.upsamplers[model_name] = RealESRGANer(
                    scale=config["scale"],
                    model_path=model_path,
                    device=self.device
                )

            logger.info("Модели Real-ESRGAN инициализированы")
            return True
        except Exception as e:
            logger.error(f"Ошибка инициализации моделей: {e}")
            return False

    def _is_anime_image(self, img: np.ndarray) -> bool:
        """Определение аниме-стиля изображения"""
        try:
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            saturation = np.mean(hsv[:, :, 1])
            value = np.mean(hsv[:, :, 2])
            return saturation > 100 and value > 130
        except Exception as e:
            logger.warning(f"Ошибка определения стиля: {e}")
            return False

    async def upscale_image(
        self,
        input_path: str,
        output_path: str,
        scale: int = 4,
        tile_size: int = 400,
        tile_pad: int = 10
    ) -> bool:
        """
        Апскейл изображения с автоматическим выбором модели
        
        Args:
            input_path: Путь к исходному изображению
            output_path: Путь для сохранения результата
            scale: Масштаб увеличения
            tile_size: Размер тайлов для обработки
            tile_pad: Отступы вокруг тайлов
            
        Returns:
            bool: Успешность операции
        """
        # Валидация входного файла
        is_valid, img = await self.utils.validate_image(input_path)
        if not is_valid:
            return False

        try:
            # Выбор модели
            model_name = "RealESRGAN_x4plus_anime_6B" if self._is_anime_image(img) else "RealESRGAN_x4plus"
            
            if model_name not in self.upsamplers:
                raise ValueError(f"Модель {model_name} не загружена")

            logger.info(f"Начало апскейла (модель: {model_name}, scale: {scale})...")

            # Обработка с настройкой тайлов
            upsampler = self.upsamplers[model_name]
            result, _ = upsampler.enhance(
                img,
                outscale=scale,
                tile_size=tile_size,
                tile_pad=tile_pad
            )

            # Сохранение результата
            if not await self.utils.save_image(result, output_path):
                return False
                
            self.temp_files.append(output_path)
            
            # Логирование
            self.logger.log_event({
                "operation": "upscale",
                "input": input_path,
                "output": output_path,
                "model": model_name,
                "params": {
                    "scale": scale,
                    "tile_size": tile_size,
                    "tile_pad": tile_pad
                },
                "status": "success",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка апскейла: {e}")
            self.logger.log_event({
                "operation": "upscale",
                "input": input_path,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
            return False

    async def cleanup(self):
        """Очистка временных файлов"""
        removed = self.utils.safe_remove(self.temp_files)
        logger.info(f"Очищено временных файлов: {removed}/{len(self.temp_files)}")

# Адаптер для совместимости
async def process_upscale(input_path: str, output_path: str, scale: int = 4) -> bool:
    upscaler = ImageUpscaler()
    if not await upscaler.initialize_models():
        return False
        
    result = await upscaler.upscale_image(input_path, output_path, scale)
    await upscaler.cleanup()
    return result