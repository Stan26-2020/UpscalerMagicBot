import cv2, os
from modes.utils import log_event

async def process_face_restore(input_path, output_path):
    img = cv2.imread(input_path)
    # Заглушка: можно интегрировать GFPGAN или CodeFormer
    restored = img
    cv2.imwrite(output_path, restored)
    log_event("face_restore.jsonl", {"input": input_path, "status": "success"})
