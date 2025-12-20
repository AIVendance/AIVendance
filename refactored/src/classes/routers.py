from fastapi import APIRouter, Depends, HTTPException
from uuid import uuid4
from authentication.auth_dependence.token import verify_token, get_password_hash
from fastapi.security import OAuth2PasswordBearer
from .schema import CourseCreate, SectionCreate
from .services import create_course_service, get_all_courses_service, create_section_service
from database.execution import execute_query, fetch_one

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# --- Dependencies ---
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    return payload

# --- Course Endpoints ---
@router.get("/", summary="List all Courses")
def list_courses(user: dict = Depends(get_current_user)):
    return get_all_courses_service()

@router.post("/", summary="Create a new Course")
def create_course(course: CourseCreate, user: dict = Depends(get_current_user)):
    result = create_course_service(course, user.get("sub"))
    if "error" in result: 
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.put("/{course_id}/cancel", summary="Cancel Course")
def cancel_course(course_id: str):
    execute_query("UPDATE courses SET status = 'cancelled' WHERE id = %s", (course_id,))
    return {"message": "Course cancelled"}

# --- Assignment Endpoint (Create Section) ---
@router.post("/sections", summary="Assign Instructor to Course")
def create_section(section: SectionCreate, user: dict = Depends(get_current_user)):
    """
    Links a Course to an Instructor with a specific Room and Time.
    """
    # 1. Validation
    c_check = fetch_one("SELECT id FROM courses WHERE id = %s", (section.course_id,))
    i_check = fetch_one("SELECT id FROM admin WHERE id = %s", (section.instructor_id,))
    
    if not c_check: raise HTTPException(status_code=404, detail="Course not found")
    if not i_check: raise HTTPException(status_code=404, detail="Instructor not found")

    # 2. Creation
    result = create_section_service(section)
    if "error" in result: 
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/sections/all", summary="Get All Active Sections")
def get_all_sections(user: dict = Depends(get_current_user)):
    """
    Returns a list of all scheduled class sections for the enrollment dropdown.
    """
    query = """
        SELECT ci.id, c.code, c.name, a.full_name as instructor, ci.days, ci.lecture_time, ci.room_num
        FROM course_instructors ci
        JOIN courses c ON ci.course_id = c.id
        JOIN admin a ON ci.instructor_id = a.id
    """
    # Note: We need to import fetch_all if not already there
    from database.execution import fetch_all
    return fetch_all(query)


# --- TEST GENERATOR (The Magic Button) ---
@router.post("/test-setup", summary="Generate Test Environment")
def generate_test_class(user: dict = Depends(get_current_user)):
    """
    Creates: 'TEST-101' Course + 'test_inst' Instructor + Links them.
    """
    # 1. Create Course
    course_id = str(uuid4())
    execute_query("""
        INSERT INTO courses (id, code, name, status) 
        VALUES (%s, 'TEST-101', 'Recognition Testing', 'active')
        ON CONFLICT (code) DO NOTHING
    """, (course_id,))
    
    # Fetch ID (in case it existed and ON CONFLICT ran)
    real_course = fetch_one("SELECT id FROM courses WHERE code = 'TEST-101'")
    course_id = real_course['id']

    # 2. Create Test Instructor
    inst_id = str(uuid4())
    inst_pass = get_password_hash("testpass")
    execute_query("""
        INSERT INTO admin (id, username, password_hash, full_name, department) 
        VALUES (%s, 'test_inst', %s, 'Test Instructor', 'QA')
        ON CONFLICT (username) DO NOTHING
    """, (inst_id, inst_pass))

    real_inst = fetch_one("SELECT id FROM admin WHERE username = 'test_inst'")
    inst_id = real_inst['id']

    # 3. Create Section (Assignment)
    section_id = str(uuid4())
    # We use a random time/room for the test
    execute_query("""
        INSERT INTO course_instructors (id, course_id, instructor_id, room_num, days, lecture_time)
        VALUES (%s, %s, %s, 'LAB-TEST', 'Daily', '09:00:00')
    """, (section_id, course_id, inst_id))

    return {
        "message": "Test Class Created Successfully!",
        "course": "TEST-101 (Recognition Testing)",
        "instructor_login": "test_inst",
        "instructor_pass": "testpass",
        "section_id": section_id
    }