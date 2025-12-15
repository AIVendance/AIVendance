from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from typing import List
import numpy as np
from database.execution import fetch_all
from attendance.services import mark_attendance_service
from attendance.schema import AttendanceCreate
from .services import get_face_embedding

router = APIRouter()

# Threshold for Face Matching (0.0 to 1.0)
# Cosine Similarity: 1.0 is exact match. 0.5-0.6 is usually a good threshold for SFace.
SIMILARITY_THRESHOLD = 0.5 

def cosine_similarity(embedding1, embedding2):
    """
    Calculates the cosine similarity between two vectors.
    """
    vec1 = np.array(embedding1)
    vec2 = np.array(embedding2)
    
    # Calculate dot product and magnitudes
    dot_product = np.dot(vec1, vec2)
    norm_a = np.linalg.norm(vec1)
    norm_b = np.linalg.norm(vec2)
    
    return dot_product / (norm_a * norm_b)

@router.post("/recognize", summary="Identify Student from Face Image")
def recognize_and_mark_attendance(
    section_id: str = Form(...), 
    photo: UploadFile = File(...)
):
    """
    1. Receives an image.
    2. Generates an embedding.
    3. Compares it against students in the specific section.
    4. Marks attendance if a match is found.
    """
    # 1. Process Image -> Get Embedding from AI Service
    image_bytes = photo.file.read()
    ai_result = get_face_embedding(image_bytes)
    
    if "error" in ai_result:
        raise HTTPException(status_code=400, detail=ai_result["error"])
    
    input_embedding = ai_result["embedding"]

    # 2. Get all students enrolled in this specific section
    # Optimization: We only check students in this class, not the whole university.
    query = """
    SELECT s.id, s.full_name, s.face_encoding 
    FROM students s
    JOIN enrollments e ON s.id = e.student_id
    WHERE e.course_instructors_id = %s
    """
    students = fetch_all(query, (section_id,))
    
    if not students:
        raise HTTPException(status_code=404, detail="No students found for this section")

    # 3. Find the Best Match
    best_match_student = None
    highest_score = -1.0

    for student in students:
        db_embedding = student['face_encoding']
        
        # Skip students who don't have face data yet
        if not db_embedding:
            continue
            
        score = cosine_similarity(input_embedding, db_embedding)
        
        if score > highest_score:
            highest_score = score
            best_match_student = student

    # 4. Check against Threshold
    if highest_score < SIMILARITY_THRESHOLD:
        return {
            "message": "Face detected, but no matching student found.", 
            "score": float(highest_score)
        }

    # 5. Mark Attendance
    # We assume 'Present' (or Late) based on the logic in mark_attendance_service
    attendance_data = AttendanceCreate(
        student_id=best_match_student['id'],
        section_id=section_id
    )
    result = mark_attendance_service(attendance_data)

    return {
        "message": "Student Identified Successfully",
        "student": best_match_student['full_name'],
        "confidence_score": float(highest_score),
        "attendance_result": result
    }