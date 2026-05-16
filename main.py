import os
import shutil
import uuid
import uvicorn
from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="FKG STUDIOS API")

UPLOAD_DIR = "uploaded_assets"
STATIC_DIR = "static"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

assets_db = []

ADMIN_USER = "fahad_admin"
ADMIN_PASS = "fkg_secure_password_2026"

@app.post("/api/login")
async def api_login(username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USER and password == ADMIN_PASS:
        return JSONResponse(content={"message": "Login successful", "status": "success"}, status_code=200)
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/upload")
async def api_upload(
    username: str = Form(...),
    password: str = Form(...),
    title: str = Form(...),
    asset_type: str = Form(...),
    description: str = Form(...),
    file: UploadFile = File(...)
):
    if username != ADMIN_USER and password != ADMIN_PASS:
        raise HTTPException(status_code=401, detail="Unauthorized request")
    
    secure_filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, secure_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    asset = {
        "id": str(uuid.uuid4()),
        "title": title,
        "type": asset_type,
        "description": description,
        "filename": secure_filename,
        "download_url": f"/api/download/{secure_filename}"
    }
    
    assets_db.append(asset)
    return JSONResponse(content={"message": "Upload successful", "asset": asset}, status_code=200)

@app.get("/api/assets")
async def get_assets():
    return JSONResponse(content=assets_db, status_code=200)

@app.get("/api/download/{filename}")
async def download_asset(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename=filename, media_type='application/octet-stream')
    raise HTTPException(status_code=404, detail="File not found on server")

app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
