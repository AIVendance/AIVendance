from database.execution import fetch_all

def get_instructor_classes_service(instructor_id: str):
    """
    Fetches all class sections assigned to this instructor.
    Joins the 'course_instructors' table with 'courses' to get names.
    """
    query = """
    SELECT 
        ci.id as section_id,
        c.name as course_name,
        c.code as course_code,
        ci.room_num,
        ci.lecture_time,
        ci.days
    FROM course_instructors ci
    JOIN courses c ON ci.course_id = c.id
    WHERE ci.instructor_id = %s
    """
    return fetch_all(query, (instructor_id,))