"""
Модуль modes - обработка изображений через нейросетевые модели

Содержит:
- upscale: Апскейл изображений (Real-ESRGAN)
- face_restore: Восстановление лиц (GFPGAN/CodeFormer)
- illustration: Стилизация изображений (Stable Diffusion)
- poster: Генерация постеров (ControlNet)
"""

import logging
from typing import Optional
from datetime import datetime

# Настройка логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Импорт основных обработчиков
from .upscale import ImageUpscaler, process_upscale
from .face_restore import FaceRestorer, process_face_restore
from .illustration import IllustrationProcessor, process_illustration
from .poster import PosterProcessor, process_poster

# Версия пакета
__version__ = "1.0.0"
__all__ = [
    'ImageUpscaler',
    'FaceRestorer', 
    'IllustrationProcessor',
    'PosterProcessor',
    'process_upscale',
    'process_face_restore',
    'process_illustration',
    'process_poster'
]

class ImageProcessor:
    """Универсальный обработчик изображений"""
    
    def __init__(self, device: str = "cpu"):
        """
        Инициализация обработчиков
        
        Args:
            device: Устройство для обработки (cpu/cuda)
        """
        self.upscaler = ImageUpscaler(device=device)
        self.face_restorer = FaceRestorer(device=device)
        self.illustrator = IllustrationProcessor()
        self.poster_maker = PosterProcessor()
        
        logger.info(f"Инициализирован ImageProcessor (device={device})")

    async def initialize(self):
        """Асинхронная инициализация моделей"""
        await asyncio.gather(
            self.upscaler.initialize_models(),
            self.face_restorer.initialize(),
            self.illustrator.initialize()
        )
        logger.info("Все модели загружены")

# Инициализация глобального процессора (ленивая)
_global_processor: Optional[ImageProcessor] = None

def get_processor(device: str = "cpu") -> ImageProcessor:
    """Получение глобального обработчика (синглтон)"""
    global _global_processor
    if _global_processor is None:
        _global_processor = ImageProcessor(device=device)
    return _global_processor

# Совместимость с Jupyter/Colab
def _print_welcome():
    """Приветственное сообщение"""
    print(f"Image Processing Module v{__version__}")
    print("Available processors: upscale, face_restore, illustration, poster")

if __name__ == "__main__":
    _print_welcome()