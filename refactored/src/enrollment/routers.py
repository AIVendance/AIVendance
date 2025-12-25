#C:\Users\user\Documents\Graduation project\AIVendance\refactored\src\enrollment\routers.py
from fastapi import APIRouter, Depends, HTTPException, Body
from uuid import uuid4
from authentication.auth_dependence.token import verify_token
from fastapi.security import OAuth2PasswordBearer
from database.execution import execute_query, fetch_one, fetch_all

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if not payload: raise HTTPException(status_code=401, detail="Invalid Credentials")
    return payload

@router.get("/", summary="List All Enrollments (Admin)")
def list_all_enrollments(user: dict = Depends(get_current_user)):
    """Get all student enrollments with course and instructor details"""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    query = """
        SELECT 
            s.full_name as student_name,
            s.university_id,
            c.code as course_code,
            c.name as course_name,
            a.full_name as instructor_name,
            ci.days,
            ci.lecture_time,
            ci.room_num
        FROM enrollments e
        JOIN students s ON e.student_id = s.id
        JOIN course_instructors ci ON e.course_instructors_id = ci.id
        JOIN courses c ON ci.course_id = c.id
        JOIN admin a ON ci.instructor_id = a.id
        ORDER BY c.code, s.full_name
    """
    return fetch_all(query)

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

@router.get("/{section_id}/students", summary="Get Students in Section")
def get_students_for_section(section_id: str, user: dict = Depends(get_current_user)):
    """
    Returns list of students enrolled in a specific class section.
    """
    # Allow admin or the instructor of that course
    if user.get("role") not in ["admin", "instructor", "super_admin"]:
         raise HTTPException(status_code=403, detail="Not authorized")
    
    query = """
        SELECT s.id, s.full_name, s.university_id, s.face_encoding
        FROM enrollments e
        JOIN students s ON e.student_id = s.id
        WHERE e.course_instructors_id = %s
        ORDER BY s.full_name
    """
    return fetch_all(query, (section_id,))

