import cv2, os
from modes.utils import log_event

async def process_illustration(input_path, output_path):
    img = cv2.imread(input_path)
    stylized = img  # Заглушка: SD генерация
    cv2.imwrite(output_path, stylized)
    log_event("illustration.jsonl", {"input": input_path, "status": "success"})

async def process_poster(input_path, output_path):
    img = cv2.imread(input_path)
    modified = img  # Заглушка: ControlNet обработка
    cv2.imwrite(output_path, modified)
    log_event("poster.jsonl", {"input": input_path, "status": "success"})
