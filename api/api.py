from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import os, shutil
from modes.upscale import process_upscale
from modes.face_restore import process_face_restore
from modes.illustration import process_illustration
from modes.poster import process_poster
from modes.utils import clear_temp

app = FastAPI()

MODES = {
    "upscale": process_upscale,
    "face_restore": process_face_restore,
    "illustration": process_illustration,
    "poster": process_poster
}

@app.post("/process/{mode}")
async def process_image(mode: str, file: UploadFile = File(...)):
    if mode not in MODES:
        return {"error": f"❌ Неверный режим: {mode}"}

    input_path, output_path = "input.jpg", "output.jpg"
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        await MODES[mode](input_path, output_path)
    except Exception as e:
        clear_temp([input_path, output_path])
        return {"error": f"⚠️ Ошибка: {str(e)}"}

    if os.path.exists(output_path):
        response = FileResponse(output_path, media_type="image/jpeg", filename="enhanced.jpg")
        clear_temp([input_path, output_path])
        return response
    return {"error": "⚠️ Файл результата не найден"}

@app.get("/ping")
async def ping():
    return {"status": "ok"}
