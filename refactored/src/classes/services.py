#C:\Users\user\Documents\Graduation project\AIVendance\refactored\src\classes\services.py
from uuid import uuid4
from database.execution import execute_query, fetch_all, fetch_one
from .schema import CourseCreate, SectionCreate

def create_course_service(course_data: CourseCreate, admin_id: str):
    """
    Inserts a new course into the database.
    """
    # 1. Check if course code already exists
    check_query = "SELECT id FROM courses WHERE code = %s"
    if fetch_one(check_query, (course_data.code,)):
        return {"error": "Course code already exists"}

    # 2. Insert new course
    insert_query = """
    INSERT INTO courses (id, code, name, status, created_by_admin_id)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id, code, name, status, created_at;
    """
    params = (
        str(uuid4()), 
        course_data.code, 
        course_data.name, 
        course_data.status, 
        admin_id
    )
    
    try:
        # We execute and fetch the result immediately to confirm creation
        # Note: execute_query normally returns None, so we might need a fetch_one wrapper 
        # for RETURNING clauses, but for now we will assume standard execution.
        execute_query(insert_query, params)
        return {"message": "Course created successfully", "code": course_data.code}
    except Exception as e:
        return {"error": str(e)}

def get_all_courses_service():
    """
    Retrieves all courses.
    """
    query = "SELECT id, code, name, status, created_at FROM courses"
    return fetch_all(query)

def create_section_service(section_data: SectionCreate):
    insert_query = """
    INSERT INTO course_instructors (id, course_id, instructor_id, room_num, lecture_time, days)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING id, course_id, room_num, days;
    """
    new_id = str(uuid4())
    params = (
        new_id,
        str(section_data.course_id),
        str(section_data.instructor_id),
        section_data.room_num,
        section_data.lecture_time,
        section_data.days
    )
    
    try:
        execute_query(insert_query, params)
        return {"message": "Section created", "id": new_id}
    except Exception as e:
        return {"error": str(e)}