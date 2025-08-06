import os
import hashlib
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileUtils:
    """Утилиты для работы с файлами"""
    
    @staticmethod
    def hash_file(path: str, algorithm: str = "sha256", chunk_size: int = 8192) -> Optional[str]:
        """
        Вычисляет хеш файла с защитой от больших файлов
        
        Args:
            path: Путь к файлу
            algorithm: Алгоритм хеширования (md5, sha1, sha256)
            chunk_size: Размер блока для чтения
            
        Returns:
            Хеш-сумма или None при ошибке
        """
        if not os.path.exists(path):
            logger.warning(f"Файл не найден: {path}")
            return None
            
        hasher = hashlib.new(algorithm)
        
        try:
            with open(path, "rb") as f:
                while chunk := f.read(chunk_size):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Ошибка хеширования файла {path}: {e}")
            return None

    @staticmethod
    def safe_remove(files: List[str]) -> int:
        """
        Безопасное удаление файлов с подсчётом успешных операций
        
        Args:
            files: Список путей к файлам
            
        Returns:
            Количество успешно удалённых файлов
        """
        success = 0
        for path in files:
            try:
                if os.path.exists(path):
                    os.remove(path)
                    success += 1
                    logger.debug(f"Удалён файл: {path}")
            except Exception as e:
                logger.error(f"Ошибка удаления файла {path}: {e}")
        return success

class Logger:
    """Усовершенствованная система логирования"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
    def log_event(self, event_data: Dict[str, Any], log_file: str = "events.log") -> bool:
        """
        Логирование события в JSONL формате
        
        Args:
            event_data: Данные для логирования
            log_file: Имя файла лога
            
        Returns:
            True если запись успешна
        """
        try:
            entry = {
                "timestamp": datetime.utcnow().isoformat(),
                **event_data
            }
            log_path = os.path.join(self.log_dir, log_file)
            
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                
            return True
        except Exception as e:
            logger.error(f"Ошибка записи лога: {e}")
            return False

    def rotate_logs(self, max_size_mb: int = 10, backup_count: int = 3) -> None:
        """
        Ротация лог-файлов при превышении размера
        
        Args:
            max_size_mb: Максимальный размер файла в MB
            backup_count: Количество бэкапов
        """
        for log_name in os.listdir(self.log_dir):
            log_path = os.path.join(self.log_dir, log_name)
            if os.path.getsize(log_path) > max_size_mb * 1024 * 1024:
                self._perform_rotation(log_path, backup_count)

    def _perform_rotation(self, log_path: str, backup_count: int) -> None:
        """Внутренний метод для ротации логов"""
        try:
            for i in range(backup_count - 1, 0, -1):
                src = f"{log_path}.{i}"
                dst = f"{log_path}.{i+1}"
                if os.path.exists(src):
                    os.rename(src, dst)
            
            if os.path.exists(log_path):
                os.rename(log_path, f"{log_path}.1")
                
            open(log_path, "a").close()
        except Exception as e:
            logger.error(f"Ошибка ротации логов: {e}")

# Пример использования
if __name__ == "__main__":
    # Инициализация
    file_utils = FileUtils()
    logger = Logger()
    
    # Пример хеширования
    file_hash = file_utils.hash_file("example.txt")
    print(f"Хеш файла: {file_hash}")
    
    # Пример логирования
    logger.log_event({
        "event": "file_processed",
        "status": "success",
        "file": "example.txt",
        "hash": file_hash
    })
    
    # Очистка временных файлов
    temp_files = ["temp1.txt", "temp2.jpg"]
    removed_count = file_utils.safe_remove(temp_files)
    print(f"Удалено файлов: {removed_count}")