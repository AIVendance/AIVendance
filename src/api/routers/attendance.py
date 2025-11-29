from fastapi import APIRouter, UploadFile, File, Depends, WebSocket
from src.db.database import get_db
from src.db.repository import AttendanceRepository
from src.services.attendance_service import attendance_service
from src.ml_engine.detector import FaceDetector
from src.ml_engine.recognizer import FaceRecognizer
from src.utils.image_processing import read_image_from_bytes

router = APIRouter()
# Initialize AI Engines once
print("🚀 Initializing AI Engines...")
detector = FaceDetector()
recognizer = FaceRecognizer()
print("✅ AI Engines Ready")

@router.post("/recognize")
async def recognize(classroom_id: str = "CS101", image: UploadFile = File(...), db=Depends(get_db)):
    # 1. Read Image
    img_bytes = await image.read()
    img = read_image_from_bytes(img_bytes)
    
    # DEBUG: Print image shape to terminal
    if img is None:
        print(f"❌ Error: Received Empty Image for {classroom_id}")
        return {"results": []}
    else:
        # print(f"📸 Received Image: {img.shape} for {classroom_id}") # Uncomment to see every frame
        pass

    repo = AttendanceRepository(db)
    
    # Pass detector AND recognizer
    results = await attendance_service.process_frame(repo, detector, recognizer, img, classroom_id)
    return {"results": results}

@router.websocket("/ws/classroom/{id}")
async def ws_endpoint(websocket: WebSocket, id: str):
    await attendance_service.connect_websocket(websocket, id)
    try:
        while True: await websocket.receive_text()
    except: pass