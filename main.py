from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.exception_handlers import http_exception_handler
from sqlalchemy.orm import Session
import cv2
import time
import threading

from backend.vision.camera import VideoProcessor
from backend.vision.detector import BarcodeDetector
from backend.service import BarcodeService
from backend.schemas import ErrorResponse, ScannedCodeCreate, ScannedCodeResponse
from backend.database import models, crud, database

# Initialize Database Tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Global Error Handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"},
    )

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Templates
templates = Jinja2Templates(directory="frontend/templates")

# Initialize global singletons
video_stream = VideoProcessor(src=0)
barcode_detector = BarcodeDetector()
barcode_service = BarcodeService()
detected_codes_buffer = []

@app.on_event("startup")
def startup_event():
    try:
        video_stream.start()
    except Exception as e:
        print(f"Failed to start camera: {e}")

@app.on_event("shutdown")
def shutdown_event():
    video_stream.stop()

def generate_frames():
    """Video streaming generator function."""
    while True:
        try:
            frame = video_stream.read()
            if frame is None:
                time.sleep(0.01)
                continue
            
            # Process frame
            processed_frame, codes = barcode_detector.detect(frame)
            
            # Use Service to Validate/Dedup
            global detected_codes_buffer
            if codes:
                # Use a fresh DB session for the background thread
                db = database.SessionLocal()
                try:
                    def metadata_helper(barcode):
                        return crud.get_barcode_metadata(db, barcode)
                    
                    unique_codes = barcode_service.process_frame_codes(codes, db_metadata_func=metadata_helper)
                    new_codes = [c for c in unique_codes if c.get('is_new')]
                    if new_codes:
                        detected_codes_buffer.extend(new_codes)
                finally:
                    db.close()
            
            # Encode
            ret, buffer = cv2.imencode('.jpg', processed_frame)
            if not ret: continue
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except Exception as e:
            print(f"Stream error: {e}")
            time.sleep(1)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(generate_frames(), 
                            media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/api/latest_codes", response_model=list)
async def get_latest_codes():
    global detected_codes_buffer
    codes = detected_codes_buffer
    detected_codes_buffer = [] 
    return JSONResponse(content=codes)

# Database Endpoints

@app.post("/api/codes", response_model=ScannedCodeResponse)
async def create_code(code: ScannedCodeCreate, db: Session = Depends(database.get_db)):
    return crud.create_code(db=db, code=code)

@app.get("/api/codes", response_model=list[ScannedCodeResponse])
async def read_codes(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    codes = crud.get_codes(db, skip=skip, limit=limit)
    return codes

@app.delete("/api/codes/all")
async def delete_all_codes(db: Session = Depends(database.get_db)):
    crud.delete_all_codes(db)
    return {"status": "success"}

@app.delete("/api/codes/{code_id}")
async def delete_code(code_id: int, db: Session = Depends(database.get_db)):
    success = crud.delete_code(db, code_id)
    if not success:
        raise HTTPException(status_code=404, detail="Code not found")
    return {"status": "success"}

@app.get("/api/stats/hourly")
async def get_hourly_stats(db: Session = Depends(database.get_db)):
    # Simple hourly grouping for today
    today = time.strftime("%Y-%m-%d")
    scans = db.query(models.ScannedCode).filter(models.ScannedCode.timestamp.like(f"{today}%")).all()
    
    hourly = [0] * 24
    for s in scans:
        try:
            # Assumes ISO format from SQLite
            hour = int(s.timestamp.split("T")[1].split(":")[0])
            hourly[hour] += 1
        except:
            continue
    return JSONResponse(content={"labels": [f"{h:02d}:00" for h in range(24)], "data": hourly})

# Re-initialize DB if needed (migration hack for dev)
# models.Base.metadata.create_all(bind=database.engine) is already at top.
# But it won't add columns.

# Export Endpoints
from fastapi.responses import Response
from backend.database import backup

@app.get("/api/export/csv")
async def export_csv(db: Session = Depends(database.get_db)):
    csv_content = backup.export_to_csv(db)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=codes_{timestamp}.csv"}
    )

@app.get("/api/export/json")
async def export_json(db: Session = Depends(database.get_db)):
    data = backup.export_to_json(db)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    return JSONResponse(
        content=data,
        headers={"Content-Disposition": f"attachment; filename=codes_{timestamp}.json"}
    )

import shutil
import os

# Automatic Backup
def backup_loop():
    while True:
        try:
            time.sleep(600) # Backup every 10 minutes
            if os.path.exists("barcodes.db"):
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                backup_path = f"backups/barcodes_{timestamp}.db"
                shutil.copy2("barcodes.db", backup_path)
                print(f"[INFO] Automatic backup created: {backup_path}")
        except Exception as e:
            print(f"[ERROR] Backup failed: {e}")

@app.on_event("startup")
def startup_event():
    try:
        video_stream.start()
        # Start backup thread
        backup_thread = threading.Thread(target=backup_loop, daemon=True)
        backup_thread.start()
    except Exception as e:
        print(f"Failed to start camera or backup: {e}")

@app.on_event("shutdown")
def shutdown_event():
    video_stream.stop()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
