import os
import cv2
import numpy as np
from typing import Optional, Tuple
import logging
from datetime import datetime
from modes.utils import FileUtils, Logger  # Используем улучшенные утилиты

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageProcessor:
    """Базовый класс для обработки изображений"""
    
    def __init__(self):
        self.file_utils = FileUtils()
        self.logger = Logger()
        self.temp_files = []

    async def _validate_image(self, img_path: str) -> Tuple[bool, Optional[np.ndarray]]:
        """Валидация входного изображения"""
        if not os.path.exists(img_path):
            logger.error(f"Файл не найден: {img_path}")
            return False, None
            
        try:
            img = cv2.imread(img_path)
            if img is None:
                raise ValueError("Не удалось загрузить изображение")
            return True, img
        except Exception as e:
            logger.error(f"Ошибка загрузки изображения: {e}")
            return False, None

    async def _save_result(self, image: np.ndarray, output_path: str) -> bool:
        """Сохранение результата с обработкой ошибок"""
        try:
            success = cv2.imwrite(output_path, image)
            if not success:
                raise ValueError("Ошибка сохранения изображения")
            
            self.temp_files.append(output_path)
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения: {e}")
            return False

    async def cleanup(self):
        """Очистка временных файлов"""
        removed = self.file_utils.safe_remove(self.temp_files)
        logger.info(f"Очищено временных файлов: {removed}/{len(self.temp_files)}")

class PosterProcessor(ImageProcessor):
    """Обработчик для создания постеров"""
    
    async def process_poster(self, input_path: str, output_path: str) -> bool:
        """
        Генерация постера с ControlNet обработкой
        
        Args:
            input_path: Путь к исходному изображению
            output_path: Путь для сохранения результата
            
        Returns:
            bool: Успешность операции
        """
        # Валидация изображения
        is_valid, img = await self._validate_image(input_path)
        if not is_valid:
            return False

        try:
            # Здесь будет реальная логика обработки через ControlNet
            logger.info("Начало обработки постера...")
            
            # Заглушка для примера - добавление эффекта постера
            modified = self._apply_poster_effect(img)
            
            # Сохранение результата
            if not await self._save_result(modified, output_path):
                return False
                
            # Логирование
            self.logger.log_event({
                "operation": "poster_generation",
                "input": input_path,
                "output": output_path,
                "status": "success",
                "processing_time": str(datetime.utcnow())
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обработки постера: {e}")
            self.logger.log_event({
                "operation": "poster_generation",
                "input": input_path,
                "status": "failed",
                "error": str(e)
            })
            return False

    def _apply_poster_effect(self, img: np.ndarray) -> np.ndarray:
        """Применение эффекта постера (заглушка)"""
        # Реальная реализация будет использовать ControlNet
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

class IllustrationProcessor(ImageProcessor):
    """Обработчик для стилизации изображений"""
    
    async def process_illustration(self, input_path: str, output_path: str) -> bool:
        """
        Стилизация изображения через Stable Diffusion
        
        Args:
            input_path: Путь к исходному изображению
            output_path: Путь для сохранения результата
            
        Returns:
            bool: Успешность операции
        """
        is_valid, img = await self._validate_image(input_path)
        if not is_valid:
            return False

        try:
            logger.info("Начало стилизации изображения...")
            
            # Заглушка для примера - здесь будет SD обработка
            stylized = self._apply_sd_style(img)
            
            if not await self._save_result(stylized, output_path):
                return False
                
            self.logger.log_event({
                "operation": "illustration_generation",
                "input": input_path,
                "output": output_path,
                "status": "success",
                "processing_time": str(datetime.utcnow())
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка стилизации: {e}")
            self.logger.log_event({
                "operation": "illustration_generation",
                "input": input_path,
                "status": "failed",
                "error": str(e)
            })
            return False

    def _apply_sd_style(self, img: np.ndarray) -> np.ndarray:
        """Применение стиля (заглушка)"""
        # Реальная реализация будет использовать Stable Diffusion
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hsv[:,:,1] = hsv[:,:,1]*1.5  # Увеличение насыщенности
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

# Пример использования
async def main():
    poster_processor = PosterProcessor()
    await poster_processor.process_poster("input.jpg", "poster_output.jpg")
    await poster_processor.cleanup()

    ill_processor = IllustrationProcessor()
    await ill_processor.process_illustration("input.jpg", "illustration_output.jpg")
    await ill_processor.cleanup()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())