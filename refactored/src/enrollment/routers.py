from fastapi import APIRouter, Depends, HTTPException, Body
from uuid import uuid4
from authentication.auth_dependence.token import verify_token
from fastapi.security import OAuth2PasswordBearer
from database.execution import execute_query, fetch_one

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if not payload: raise HTTPException(status_code=401, detail="Invalid Credentials")
    return payload

@router.post("/", summary="Enroll Student in Class")
def enroll_student(
    student_id: str = Body(..., embed=True), 
    section_id: str = Body(..., embed=True),
    user: dict = Depends(get_current_user)
):
    # 1. Check if valid Student & Section
    s_check = fetch_one("SELECT id FROM students WHERE id = %s", (student_id,))
    if not s_check: raise HTTPException(status_code=404, detail="Student not found")

    sec_check = fetch_one("SELECT id FROM course_instructors WHERE id = %s", (section_id,))
    if not sec_check: raise HTTPException(status_code=404, detail="Class Section not found")

    # 2. Check if already enrolled
    exists = fetch_one("""
        SELECT id FROM enrollments 
        WHERE student_id = %s AND course_instructors_id = %s
    """, (student_id, section_id))
    
    if exists:
        raise HTTPException(status_code=400, detail="Student already enrolled in this class")

    # 3. Enroll
    new_id = str(uuid4())
    execute_query("""
        INSERT INTO enrollments (id, student_id, course_instructors_id)
        VALUES (%s, %s, %s)
    """, (new_id, student_id, section_id))

    return {"message": "Student successfully enrolled!"}