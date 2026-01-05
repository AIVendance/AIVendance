from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from app.core.security import get_password_hash

from app.api.deps import get_db_session, require_role
from app.db import schema as models

router = APIRouter(prefix="/admin", tags=["admin"])


# Request schemas for POST endpoints
class CreateStudentRequest(BaseModel):
    full_name: str
    university_id: str
    email: str
    password: str
    major: str


class CreateInstructorRequest(BaseModel):
    full_name: str
    username: str
    email: str
    password: str
    department: str


class CreateCourseRequest(BaseModel):
    code: str
    name: str


class AssignScheduleRequest(BaseModel):
    room_num: str
    days: str
    start_time: str
    end_time: str


class AssignInstructorRequest(BaseModel):
    instructor_id: str


class BulkEnrollItem(BaseModel):
    university_id: str
    course_code: str


class BulkEnrollRequest(BaseModel):
    enrollments: list[BulkEnrollItem]


@router.get("/dashboard")
def admin_dashboard(
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("admin")),
):
    """
    Admin dashboard with system overview and key statistics.
    """
    admin_id = current_user["sub"]
    
    admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    students_count = db.query(models.Student).count()
    instructors_count = db.query(models.Admin).filter(models.Admin.id != admin_id).count()
    courses_count = db.query(models.Course).count()
    offerings_count = db.query(models.CourseInstructor).count()
    attendance_records_count = db.query(models.AttendanceRecord).count()
    
    return {
        "admin": {
            "id": str(admin.id),
            "username": admin.username,
            "full_name": admin.full_name,
            "email": admin.email,
            "department": admin.department,
            "is_active": admin.is_active,
        },
        "system_statistics": {
            "students": students_count,
            "instructors": instructors_count,
            "courses": courses_count,
            "course_offerings": offerings_count,
            "attendance_records": attendance_records_count,
        }
    }


@router.get("/profile")
def get_admin_profile(
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("admin")),
):
    """
    Get complete admin profile with all personal details.
    """
    admin_id = current_user["sub"]
    
    admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    return {
        "id": str(admin.id),
        "username": admin.username,
        "full_name": admin.full_name,
        "email": admin.email,
        "department": admin.department,
        "is_active": admin.is_active,
        "created_at": admin.created_at.isoformat() if admin.created_at else None,
    }


@router.get("/summary")
def admin_summary(
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("admin")),
):
    students_count = db.query(models.Student).count()
    instructors_count = db.query(models.Admin).count()
    courses_count = db.query(models.Course).count()
    offerings_count = db.query(models.CourseInstructor).count()
    attendance_records_count = db.query(models.AttendanceRecord).count()

    return {
        "students": students_count,
        "instructors": instructors_count,
        "courses": courses_count,
        "course_offerings": offerings_count,
        "attendance_records": attendance_records_count,
    }


@router.get("/students")
def list_students(
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("admin")),
):
    students = db.query(models.Student).order_by(models.Student.university_id).all()
    return [
        {
            "id": str(s.id),
            "university_id": s.university_id,
            "full_name": s.full_name,
            "email": s.email,
            "major": s.major,
            "enrollment_year": s.enrollment_year,
            "is_active": s.is_active,
        }
        for s in students
    ]


@router.post("/students")
def create_student(
    request: CreateStudentRequest,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("admin")),
):
    """Create a new student."""
    # Check if university_id already exists
    existing = db.query(models.Student).filter(models.Student.university_id == request.university_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student with this university ID already exists")
    
    # Check if email already exists
    email_existing = db.query(models.Student).filter(models.Student.email == request.email).first()
    if email_existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_student = models.Student(
        id=uuid4(),
        full_name=request.full_name,
        university_id=request.university_id,
        email=request.email,
        password_hash=get_password_hash(request.password),
        major=request.major,
        enrollment_year=2024,
        is_active=True,
    )
    
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    
    return {
        "id": str(new_student.id),
        "university_id": new_student.university_id,
        "full_name": new_student.full_name,
        "email": new_student.email,
        "major": new_student.major,
        "is_active": new_student.is_active,
    }


@router.delete("/students/{student_id}")
def delete_student(
    student_id: str,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("admin")),
):
    """Delete a student."""
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db.delete(student)
    db.commit()
    
    return {"message": "Student deleted successfully"}


@router.get("/instructors")
def list_instructors(
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("admin")),
):
    admins = db.query(models.Admin).order_by(models.Admin.username).all()
    return [
        {
            "id": str(a.id),
            "username": a.username,
            "full_name": a.full_name,
            "email": a.email,
            "department": a.department,
            "is_active": a.is_active,
        }
        for a in admins
    ]


@router.post("/instructors")
def create_instructor(
    request: CreateInstructorRequest,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("admin")),
):
    """Create a new instructor."""
    # Check if username already exists
    existing = db.query(models.Admin).filter(models.Admin.username == request.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email already exists
    email_existing = db.query(models.Admin).filter(models.Admin.email == request.email).first()
    if email_existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_instructor = models.Admin(
        id=uuid4(),
        username=request.username,
        full_name=request.full_name,
        email=request.email,
        password_hash=get_password_hash(request.password),
        department=request.department,
        is_active=True,
    )
    
    db.add(new_instructor)
    db.commit()
    db.refresh(new_instructor)
    
    return {
        "id": str(new_instructor.id),
        "username": new_instructor.username,
        "full_name": new_instructor.full_name,
        "email": new_instructor.email,
        "department": new_instructor.department,
        "is_active": new_instructor.is_active,
    }


@router.delete("/instructors/{instructor_id}")
def delete_instructor(
    instructor_id: str,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("admin")),
):
    """Delete an instructor."""
    instructor = db.query(models.Admin).filter(models.Admin.id == instructor_id).first()
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor not found")
    
    db.delete(instructor)
    db.commit()
    
    return {"message": "Instructor deleted successfully"}


@router.get("/courses")
def list_courses(
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("admin")),
):
    # Get all courses
    courses = db.query(models.Course).all()
    result = []
    
    for course in courses:
        # Get all CourseInstructor records for this course
        course_instructors = db.query(models.CourseInstructor).filter(
            models.CourseInstructor.course_id == course.id
        ).all()
        
        if course_instructors:
            # If course has instructors, add each one
            for ci in course_instructors:
                instructor = ci.instructor
                enroll_count = (
                    db.query(models.Enrollment)
                    .filter(models.Enrollment.course_instructors_id == ci.id)
                    .count()
                )
                
                result.append(
                    {
                        "id": str(course.id),
                        "course_instructor_id": str(ci.id),
                        "course_code": course.code,
                        "course_name": course.name,
                        "room": ci.room_num,
                        "days": ci.days,
                        "lecture_time": ci.lecture_time.isoformat()
                        if ci.lecture_time
                        else None,
                        "instructor_name": instructor.full_name if instructor else "Unassigned",
                        "instructor_id": str(instructor.id) if instructor else None,
                        "enrolled_count": enroll_count,
                        "capacity": 50,
                        "status": "Active",
                    }
                )
        else:
            # Course with no instructors
            result.append(
                {
                    "id": str(course.id),
                    "course_instructor_id": None,
                    "course_code": course.code,
                    "course_name": course.name,
                    "room": "TBA",
                    "days": "TBA",
                    "lecture_time": None,
                    "instructor_name": "Unassigned",
                    "instructor_id": None,
                    "enrolled_count": 0,
                    "capacity": 50,
                    "status": "Active",
                }
            )

    return result


@router.post("/courses")
def create_course(
    request: CreateCourseRequest,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("admin")),
):
    """Create a new course."""
    # Check if course code already exists
    existing = db.query(models.Course).filter(models.Course.code == request.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Course with this code already exists")
    
    # Create the course
    new_course = models.Course(
        id=uuid4(),
        code=request.code,
        name=request.name,
        status="Active",
    )
    
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    
    return {
        "id": str(new_course.id),
        "code": new_course.code,
        "name": new_course.name,
        "status": new_course.status,
    }


@router.delete("/courses/{course_id}")
def delete_course(
    course_id: str,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("admin")),
):
    """Delete a course."""
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    db.delete(course)
    db.commit()
    
    return {"message": "Course deleted successfully"}


@router.post("/courses/{course_id}/schedule")
def assign_schedule(
    course_id: str,
    request: AssignScheduleRequest,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("admin")),
):
    """Assign a schedule and room to a course."""
    # Find the course
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check if CourseInstructor exists for this course
    course_instructor = db.query(models.CourseInstructor).filter(
        models.CourseInstructor.course_id == course_id
    ).first()
    
    if course_instructor:
        # Update existing CourseInstructor
        course_instructor.room_num = request.room_num
        course_instructor.days = request.days
        course_instructor.lecture_time = request.start_time  # Store start time
        db.commit()
        return {"message": "Schedule updated successfully"}
    else:
        # Cannot create CourseInstructor without an instructor
        # User should assign an instructor first via the Enrollments page
        raise HTTPException(
            status_code=400, 
            detail="Course must have an instructor assigned before assigning a schedule. Please use the Enrollments page to assign an instructor first."
        )


@router.post("/courses/{course_id}/assign-instructor")
def assign_instructor_to_course(
    course_id: str,
    request: AssignInstructorRequest,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("admin")),
):
    """Assign an instructor to a course."""
    # Find the course
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Find the instructor (which is an Admin)
    instructor = db.query(models.Admin).filter(models.Admin.id == request.instructor_id).first()
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor not found")
    
    # Check if CourseInstructor already exists for this course
    course_instructor = db.query(models.CourseInstructor).filter(
        models.CourseInstructor.course_id == course_id,
        models.CourseInstructor.instructor_id == request.instructor_id
    ).first()
    
    if course_instructor:
        # Already assigned
        return {"message": "Instructor already assigned to this course"}
    
    # Check if there's already a CourseInstructor for this course (different instructor)
    existing_ci = db.query(models.CourseInstructor).filter(
        models.CourseInstructor.course_id == course_id
    ).first()
    
    if existing_ci:
        # Update existing assignment
        existing_ci.instructor_id = request.instructor_id
        db.commit()
        return {"message": "Instructor assignment updated successfully"}
    else:
        # Create new CourseInstructor
        new_course_instructor = models.CourseInstructor(
            id=uuid4(),
            course_id=course_id,
            instructor_id=request.instructor_id,
            room_num="TBA",
            days="TBA"
        )
        db.add(new_course_instructor)
        db.commit()
        return {"message": "Instructor assigned successfully"}



@router.get("/statistics")
def get_system_statistics(
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("admin")),
):
    """
    Get comprehensive system statistics and analytics.
    """
    students_count = db.query(models.Student).count()
    active_students = db.query(models.Student).filter(models.Student.is_active == True).count()
    
    instructors_count = db.query(models.Admin).count()
    active_instructors = db.query(models.Admin).filter(models.Admin.is_active == True).count()
    
    courses_count = db.query(models.Course).count()
    offerings_count = db.query(models.CourseInstructor).count()
    
    enrollments_count = db.query(models.Enrollment).count()
    attendance_records_count = db.query(models.AttendanceRecord).count()
    
    # Calculate average absence rate
    records = db.query(models.AttendanceRecord).all()
    if records:
        absent_count = sum(1 for r in records if r.status == "Absent")
        average_absence_rate = (absent_count / len(records)) * 100
    else:
        average_absence_rate = 0.0
    
    return {
        "users": {
            "students": {
                "total": students_count,
                "active": active_students,
                "inactive": students_count - active_students,
            },
            "instructors": {
                "total": instructors_count,
                "active": active_instructors,
                "inactive": instructors_count - active_instructors,
            }
        },
        "academic": {
            "courses": courses_count,
            "course_offerings": offerings_count,
            "total_enrollments": enrollments_count,
        },
        "attendance": {
            "total_records": attendance_records_count,
            "average_absence_rate": round(average_absence_rate, 2),
        }
    }


@router.get("/inactive-students")
def get_inactive_students(
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("admin")),
):
    """
    Get list of inactive students.
    """
    inactive = db.query(models.Student).filter(models.Student.is_active == False).all()
    
    return [
        {
            "id": str(s.id),
            "university_id": s.university_id,
            "full_name": s.full_name,
            "email": s.email,
            "major": s.major,
            "enrollment_year": s.enrollment_year,
        }
        for s in inactive
    ]


@router.get("/inactive-instructors")
def get_inactive_instructors(
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("admin")),
):
    """
    Get list of inactive instructors.
    """
    inactive = db.query(models.Admin).filter(models.Admin.is_active == False).all()
    
    return [
        {
            "id": str(a.id),
            "username": a.username,
            "full_name": a.full_name,
            "email": a.email,
            "department": a.department,
        }
        for a in inactive
    ]

class EnrollStudentRequest(BaseModel):
    course_id: str
    student_id: str


@router.post("/enroll-student")
def enroll_student(
    request: EnrollStudentRequest,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("admin")),
):
    """Enroll a student in a course."""
    # Find the student
    student = db.query(models.Student).filter(models.Student.id == request.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Find the course instructor (enrollment is tied to CourseInstructor, not just Course)
    course_instructor = db.query(models.CourseInstructor).filter(
        models.CourseInstructor.course_id == request.course_id
    ).first()
    
    if not course_instructor:
        raise HTTPException(
            status_code=400,
            detail="This course has no instructor assigned yet. Please assign an instructor first."
        )
    
    # Check if student is already enrolled
    existing_enrollment = db.query(models.Enrollment).filter(
        models.Enrollment.student_id == request.student_id,
        models.Enrollment.course_instructors_id == course_instructor.id
    ).first()
    
    if existing_enrollment:
        raise HTTPException(
            status_code=400,
            detail="Student is already enrolled in this course"
        )
    
    # Create enrollment
    new_enrollment = models.Enrollment(
        id=uuid4(),
        student_id=request.student_id,
        course_instructors_id=course_instructor.id
    )
    db.add(new_enrollment)
    db.commit()
    
    return {"message": "Student enrolled successfully"}


@router.post("/bulk-enroll")
def bulk_enroll(
    request: BulkEnrollRequest,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("admin")),
):
    """Bulk enroll students in courses by university_id and course_code."""
    success = 0
    fail = 0
    details = []
    
    for item in request.enrollments:
        # Find student by university_id
        student = db.query(models.Student).filter(models.Student.university_id == item.university_id).first()
        if not student:
            fail += 1
            details.append({"university_id": item.university_id, "course_code": item.course_code, "reason": "Student not found"})
            continue
        
        # Find course by code
        course = db.query(models.Course).filter(models.Course.code == item.course_code).first()
        if not course:
            fail += 1
            details.append({"university_id": item.university_id, "course_code": item.course_code, "reason": "Course not found"})
            continue
        
        # Find course instructor
        course_instructor = db.query(models.CourseInstructor).filter(models.CourseInstructor.course_id == course.id).first()
        if not course_instructor:
            fail += 1
            details.append({"university_id": item.university_id, "course_code": item.course_code, "reason": "No instructor assigned"})
            continue
        
        # Check if already enrolled
        existing = db.query(models.Enrollment).filter(
            models.Enrollment.student_id == student.id,
            models.Enrollment.course_instructors_id == course_instructor.id
        ).first()
        if existing:
            fail += 1
            details.append({"university_id": item.university_id, "course_code": item.course_code, "reason": "Already enrolled"})
            continue
        
        # Create enrollment
        new_enrollment = models.Enrollment(
            id=uuid4(),
            student_id=student.id,
            course_instructors_id=course_instructor.id
        )
        db.add(new_enrollment)
        success += 1
    
    db.commit()
    return {"success_count": success, "fail_count": fail, "details": details}