import cv2
import os
import numpy as np
from typing import Optional, Tuple
import logging
from datetime import datetime
from modes.utils import ImageUtils, Logger  # Используем улучшенные утилиты

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IllustrationProcessor:
    """Обработчик иллюстраций с интеграцией Stable Diffusion"""

    def __init__(self):
        self.utils = ImageUtils()
        self.logger = Logger()
        self.temp_files = []

    async def process_illustration(
        self,
        input_path: str,
        output_path: str,
        style: str = "fantasy",
        strength: float = 0.8
    ) -> bool:
        """
        Обработка изображения с применением стилизации
        
        Args:
            input_path: Путь к входному изображению
            output_path: Путь для сохранения результата
            style: Стиль обработки
            strength: Интенсивность эффекта (0.1-1.0)
            
        Returns:
            bool: Успешность операции
        """
        # Валидация входного файла
        is_valid, img = await self.utils.validate_image(input_path)
        if not is_valid:
            return False

        try:
            logger.info(f"Начало обработки иллюстрации (стиль: {style})...")
            
            # Препроцессинг
            processed_img = self._preprocess_image(img)
            
            # Здесь будет реальная интеграция с Stable Diffusion
            # Временная реализация:
            stylized = self._apply_style(processed_img, style, strength)
            
            # Постобработка
            final_img = self._postprocess_image(stylized)
            
            # Сохранение результата
            if not await self.utils.save_image(final_img, output_path):
                return False
                
            self.temp_files.append(output_path)
            
            # Логирование
            self.logger.log_event({
                "operation": "illustration",
                "input": input_path,
                "output": output_path,
                "style": style,
                "strength": strength,
                "status": "success",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обработки иллюстрации: {e}")
            self.logger.log_event({
                "operation": "illustration",
                "input": input_path,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
            return False

    def _preprocess_image(self, img: np.ndarray) -> np.ndarray:
        """Подготовка изображения для обработки"""
        # Ресайз до стандартного размера
        img = cv2.resize(img, (512, 512))
        # Нормализация
        return img.astype(np.float32) / 255.0

    def _postprocess_image(self, img: np.ndarray) -> np.ndarray:
        """Финализация обработанного изображения"""
        img = (img * 255).astype(np.uint8)
        return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    def _apply_style(self, img: np.ndarray, style: str, strength: float) -> np.ndarray:
        """Применение стиля к изображению (заглушка)"""
        # Эмуляция разных стилей
        if style == "fantasy":
            result = cv2.stylization(img, sigma_s=60, sigma_r=0.6)
        elif style == "anime":
            result = cv2.detailEnhance(img, sigma_s=10, sigma_r=0.15)
        else:  # default
            result = cv2.pencilSketch(img, sigma_s=60, sigma_r=0.07)[1]
        
        # Смешивание с оригиналом по силе эффекта
        return cv2.addWeighted(result, strength, img, 1-strength, 0)

    async def cleanup(self):
        """Очистка временных файлов"""
        removed = self.utils.safe_remove(self.temp_files)
        logger.info(f"Очищено временных файлов: {removed}/{len(self.temp_files)}")

# Адаптер для совместимости с оригинальным интерфейсом
async def process_illustration(input_path: str, output_path: str) -> bool:
    processor = IllustrationProcessor()
    result = await processor.process_illustration(input_path, output_path)
    await processor.cleanup()
    return result