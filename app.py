from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os
import uuid

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

templates = Jinja2Templates(directory="templates")

# 1. Buat class kustom untuk menambahkan header
class CustomStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope: Scope) -> Response:
        response = await super().get_response(path, scope)
        # Tambahkan custom header di sini
        response.headers["Content-Type"] = "application/x-chrome-extension"
        return response

@app.get("/", response_class=HTMLResponse)
async def root_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="File not attached")
    
    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{file_id}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    download_url = f"/download/{filename}"
    return {"url": download_url}

@app.get("/download/{filename}")
async def return_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return RedirectResponse(url=f"/uploads/{filename}")

app.mount("/uploads", CustomStaticFiles(directory=UPLOAD_DIR), name=UPLOAD_DIR)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)
