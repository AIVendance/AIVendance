from fastapi import APIRouter, UploadFile, File, Form, Depends
from typing import List
from src.db.database import get_db
from src.db.repository import AttendanceRepository
from src.ml_engine.detector import FaceDetector
from src.ml_engine.recognizer import FaceRecognizer
from src.services.enrollment_service import enrollment_service

router = APIRouter()
detector = FaceDetector()
rec_engine = FaceRecognizer()

@router.post("/enroll")
async def enroll(student_id: str=Form(...), full_name: str=Form(...), files: List[UploadFile]=File(...), db=Depends(get_db)):
    repo = AttendanceRepository(db)
    count = await enrollment_service.enroll_student(repo, detector, rec_engine, student_id, full_name, files)
    return {"status": "enrolled", "count": count}