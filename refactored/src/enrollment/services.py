from uuid import uuid4
from database.execution import execute_query
from .schema import EnrollmentCreate

def enroll_student_service(data: EnrollmentCreate):
    # 1. Check if already enrolled (Optional but recommended)
    # For now, we rely on the Database UNIQUE constraint to catch duplicates.

    # 2. Insert Record
    insert_query = """
    INSERT INTO enrollments (id, student_id, course_instructors_id)
    VALUES (%s, %s, %s)
    """
    params = (str(uuid4()), str(data.student_id), str(data.section_id))

    try:
        execute_query(insert_query, params)
        return {"message": "Student successfully enrolled!"}
    except Exception as e:
        return {"error": str(e)}