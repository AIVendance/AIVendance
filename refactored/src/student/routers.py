#C:\Users\user\Documents\Graduation project\AIVendance\refactored\src\student\routers.py
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Body
from typing import List
import numpy as np
from fastapi.security import OAuth2PasswordBearer
from authentication.auth_dependence.token import verify_token, get_password_hash
from ai.services import get_face_embedding
from database.execution import execute_query, fetch_one, fetch_all
from uuid import uuid4

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if not payload: raise HTTPException(status_code=401, detail="Invalid Credentials")
    return payload

# --- 1. ADMIN: CREATE STUDENT (TEXT ONLY) ---
@router.post("/create", summary="Create Student Account (Admin)")
def create_student_account(
    university_id: str = Body(...),
    full_name: str = Body(...),
    major: str = Body(...),
    password: str = Body(...),
    enrollment_year: int = Body(...),
    user: dict = Depends(get_current_user)
):
    # Check Admin Role
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Only Admins can create students")

    # Check if exists
    check = fetch_one("SELECT id FROM students WHERE university_id = %s", (university_id,))
    if check:
        raise HTTPException(status_code=400, detail="Student ID already exists")

    # Insert
    hashed_pw = get_password_hash(password)
    new_id = str(uuid4())
    execute_query("""
        INSERT INTO students (id, university_id, full_name, major, enrollment_year, password_hash)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (new_id, university_id, full_name, major, enrollment_year, hashed_pw))

    return {"message": "Student created successfully", "id": new_id}

# --- 2. STUDENT: PROFILE & UPLOAD ---
@router.get("/me", summary="Get Profile")
def get_my_profile(user: dict = Depends(get_current_user)):
    return fetch_one("SELECT full_name, university_id, major, enrollment_year FROM students WHERE id = %s", (user['sub'],))

@router.post("/upload-face", summary="Enroll Face")
def upload_face(photos: List[UploadFile] = File(...), user: dict = Depends(get_current_user)): 
    if len(photos) > 10: raise HTTPException(status_code=400, detail="Max 10 images")
    
    valid_embeddings = []
    for photo in photos:
        res = get_face_embedding(photo.file.read())
        if "embedding" in res: valid_embeddings.append(res["embedding"])

    if not valid_embeddings: raise HTTPException(status_code=400, detail="No faces detected")
    
    avg = np.mean(valid_embeddings, axis=0).tolist()
    execute_query("UPDATE students SET face_encoding = %s WHERE id = %s", (avg, user['sub']))
    return {"message": "Face enrolled!", "count": len(valid_embeddings)}

@router.get("/", summary="List All Students")
def list_all_students(user: dict = Depends(get_current_user)):
    if user.get("role") != "admin": raise HTTPException(status_code=403, detail="Admin only")
    return fetch_all("SELECT id, full_name, university_id, major, enrollment_year FROM students ORDER BY university_id")

# --- 3. ACADEMIC DATA ---
@router.get("/my-classes", summary="Get Enrolled Classes")
def get_my_classes(user: dict = Depends(get_current_user)):
    return fetch_all("""
        SELECT c.name as course_name, c.code as course_code, ci.days, ci.lecture_time, ci.room_num, a.full_name as instructor_name
        FROM enrollments e
        JOIN course_instructors ci ON e.course_instructors_id = ci.id
        JOIN courses c ON ci.course_id = c.id
        JOIN admin a ON ci.instructor_id = a.id
        WHERE e.student_id = %s
    """, (user['sub'],))

@router.get("/my-stats", summary="Get Stats")
def get_my_stats(user: dict = Depends(get_current_user)):
    return fetch_all("""
        SELECT ar.status, ar.date, c.name as course_name, c.code as course_code
        FROM attendance_records ar
        JOIN course_instructors ci ON ar.course_instructors_id = ci.id
        JOIN courses c ON ci.course_id = c.id
        WHERE ar.student_id = %s
        ORDER BY ar.date DESC
    """, (user['sub'],))