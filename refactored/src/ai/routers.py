from fastapi import APIRouter, UploadFile, File, HTTPException, Form
import numpy as np
from database.execution import fetch_all, execute_query, fetch_one
from attendance.services import mark_attendance_service
from attendance.schema import AttendanceCreate
from .services import get_face_embedding

router = APIRouter()
SIMILARITY_THRESHOLD = 0.5 

def cosine_similarity(embedding1, embedding2):
    vec1 = np.array(embedding1)
    vec2 = np.array(embedding2)
    if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0: return 0.0
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

@router.post("/recognize")
def recognize_and_mark_attendance(section_id: str = Form(...), photo: UploadFile = File(...)):
    # ... (Your standard logic) ...
    pass

# --- DEBUG ENDPOINTS FOR TESTING ---

@router.post("/debug/enroll")
def debug_enroll_face(student_id: str = Form(...), photo: UploadFile = File(...)):
    image_bytes = photo.file.read()
    ai_result = get_face_embedding(image_bytes)
    if "error" in ai_result: raise HTTPException(400, ai_result["error"])
    
    check = fetch_one("SELECT id FROM students WHERE university_id = %s", (student_id,))
    if not check: raise HTTPException(404, f"Student ID {student_id} not found")

    execute_query("UPDATE students SET face_encoding = %s WHERE university_id = %s", (ai_result["embedding"], student_id))
    return {"message": "Enrolled", "id": student_id}

@router.post("/debug/recognize")
def debug_recognize(photo: UploadFile = File(...)):
    image_bytes = photo.file.read()
    ai_result = get_face_embedding(image_bytes)
    if "error" in ai_result: raise HTTPException(400, ai_result["error"])
    
    input_embedding = ai_result["embedding"]
    students = fetch_all("SELECT university_id, full_name, face_encoding FROM students WHERE face_encoding IS NOT NULL")
    
    best_match = None
    highest_score = -1.0

    for student in students:
        score = cosine_similarity(input_embedding, student['face_encoding'])
        if score > highest_score:
            highest_score = score
            best_match = student

    match = highest_score >= SIMILARITY_THRESHOLD
    return {
        "match": match,
        "student": best_match['full_name'] if best_match else "Unknown",
        "id": best_match['university_id'] if best_match else None,
        "score": round(float(highest_score), 4)
    }