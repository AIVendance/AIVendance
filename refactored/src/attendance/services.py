from uuid import uuid4
from datetime import datetime, timedelta
from database.execution import execute_query, fetch_one, fetch_all
from .schema import AttendanceCreate

def mark_attendance_service(data: AttendanceCreate):
    # 1. Check if already marked for THIS section on THIS date
    # We prevent duplicate entries for the same day [cite: 29]
    check_query = """
    SELECT id FROM attendance_records 
    WHERE student_id = %s AND course_instructors_id = %s AND date = CURRENT_DATE
    """
    if fetch_one(check_query, (str(data.student_id), str(data.section_id))):
        return {"message": "Student already marked present today"}

    # 2. Get Class Schedule to calculate 'Late' status
    # We need the lecture_time for this section
    schedule_query = "SELECT lecture_time FROM course_instructors WHERE id = %s"
    section = fetch_one(schedule_query, (str(data.section_id),))
    
    if not section:
        return {"error": "Section not found"}

    # 3. Calculate Status (Logic)
    class_time = section['lecture_time'] # e.g., 09:00:00
    current_time = datetime.now().time()
    
    # Simple Logic: If arrival is > 15 mins after start, mark 'Late'
    # Convert times to minutes for comparison
    class_minutes = class_time.hour * 60 + class_time.minute
    current_minutes = current_time.hour * 60 + current_time.minute
    
    if current_minutes > (class_minutes + 15):
        status = "Late"
    else:
        status = "Present"

    # 4. Insert Record
    insert_query = """
    INSERT INTO attendance_records (id, student_id, course_instructors_id, date, status, total_duration_minutes)
    VALUES (%s, %s, %s, CURRENT_DATE, %s, 0)
    RETURNING id
    """
    new_id = str(uuid4())
    params = (new_id, str(data.student_id), str(data.section_id), status)
    
    try:
        execute_query(insert_query, params)
        return {"message": f"Marked as {status}", "id": new_id, "status": status}
    except Exception as e:
        return {"error": str(e)}

def get_attendance_history_service(student_id: str = None, section_id: str = None):
    """
    Fetches history. Can filter by student OR section.
    """
    query = """
    SELECT 
        ar.id, 
        s.full_name as student_name, 
        c.name as course_name, 
        ar.date, 
        ar.status, 
        ar.created_at
    FROM attendance_records ar
    JOIN students s ON ar.student_id = s.id
    JOIN course_instructors ci ON ar.course_instructors_id = ci.id
    JOIN courses c ON ci.course_id = c.id
    WHERE 1=1
    """
    params = []
    
    if student_id:
        query += " AND ar.student_id = %s"
        params.append(student_id)
        
    if section_id:
        query += " AND ar.course_instructors_id = %s"
        params.append(section_id)
        
    query += " ORDER BY ar.created_at DESC"
    
    return fetch_all(query, tuple(params))