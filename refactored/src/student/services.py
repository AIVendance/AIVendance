#C:\Users\user\Documents\Graduation project\AIVendance\refactored\src\student\services.py
from uuid import uuid4
from database.execution import execute_query, fetch_all, fetch_one
from authentication.auth_dependence.token import get_password_hash
from .schema import StudentCreate

def create_student_service(student: StudentCreate):
    # 1. Check if university_id or email already exists
    check_query = "SELECT id FROM students WHERE university_id = %s OR email = %s"
    if fetch_one(check_query, (student.university_id, student.email)):
        return {"error": "Student ID or Email already exists"}

    # 2. Hash the password
    hashed_pwd = get_password_hash(student.password)

    # 3. Insert into DB
    insert_query = """
    INSERT INTO students (id, university_id, full_name, email, major, enrollment_year, password_hash)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    new_id = str(uuid4())
    params = (
        new_id,
        student.university_id,
        student.full_name,
        student.email,
        student.major,
        student.enrollment_year,
        hashed_pwd
    )

    try:
        execute_query(insert_query, params)
        return {"message": "Student registered successfully", "id": new_id}
    except Exception as e:
        return {"error": str(e)}

def get_all_students_service():
    query = "SELECT id, university_id, full_name, email, major, is_active, created_at FROM students"
    return fetch_all(query)