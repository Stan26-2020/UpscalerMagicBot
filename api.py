from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import shutil, os
from modes.upscale import process_upscale
from modes.face_restore import process_face_restore
from modes.illustration import process_illustration
from modes.poster import process_poster

app = FastAPI()

@app.post("/process/{mode}")
async def process_image(mode: str, file: UploadFile = File(...)):
    with open("input.jpg", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if mode == "face_restore":
        await process_face_restore()
    elif mode == "illustration":
        await process_illustration()
    elif mode == "poster":
        await process_poster()
    else:
        await process_upscale()

    output_path = "output.jpg"
    if os.path.exists(output_path):
        return FileResponse(output_path, media_type="image/jpeg", filename="enhanced.jpg")
    return {"error": "Output not found"}