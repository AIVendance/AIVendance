from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, require_role
from app.db import schema as models

router = APIRouter(prefix="/student", tags=["student"])


@router.get("/dashboard")
def student_dashboard(
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("student")),
):
    """
    Student dashboard with profile info and course statistics.
    """
    student_id = current_user["sub"]
    
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    enrollments = (
        db.query(models.Enrollment)
        .filter(models.Enrollment.student_id == student_id)
        .all()
    )
    
    total_courses = len(enrollments)
    total_attendance_records = db.query(models.AttendanceRecord).filter(
        models.AttendanceRecord.student_id == student_id
    ).count()
    
    return {
        "student": {
            "id": str(student.id),
            "university_id": student.university_id,
            "full_name": student.full_name,
            "email": student.email,
            "major": student.major,
            "enrollment_year": student.enrollment_year,
            "is_active": student.is_active,
        },
        "statistics": {
            "total_enrolled_courses": total_courses,
            "total_attendance_records": total_attendance_records,
        }
    }


@router.get("/courses")
def get_my_courses(
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("student")),
):
    student_id = current_user["sub"]

    enrollments = (
        db.query(models.Enrollment)
        .join(models.CourseInstructor)
        .join(models.Course)
        .filter(models.Enrollment.student_id == student_id)
        .all()
    )

    result = []
    for e in enrollments:
        ci = e.course_instructor
        course = ci.course
        instructor = ci.instructor
        
        # Get attendance records for this course
        records = (
            db.query(models.AttendanceRecord)
            .filter(
                models.AttendanceRecord.student_id == student_id,
                models.AttendanceRecord.course_instructors_id == ci.id,
            )
            .all()
        )
        
        total_classes = len(records)
        attended_classes = sum(1 for r in records if r.status in ["Present", "Late"])
        attendance_percentage = (attended_classes / total_classes * 100) if total_classes > 0 else 0
        
        result.append(
            {
                "course_instructor_id": str(ci.id),
                "course_code": course.code,
                "course_name": course.name,
                "room": ci.room_num,
                "days": ci.days,
                "lecture_time": ci.lecture_time.isoformat()
                if ci.lecture_time
                else None,
                "instructor_name": instructor.full_name if instructor else None,
                "total_classes": total_classes,
                "attended_classes": attended_classes,
                "attendance_percentage": round(attendance_percentage, 2),
            }
        )

    return {"student_id": student_id, "courses": result}


@router.get("/attendance/summary")
def get_my_attendance_summary(
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("student")),
):
    """
    Per-course attendance summary for the logged-in student.
    """
    student_id = current_user["sub"]

    enrollments = (
        db.query(models.Enrollment)
        .join(models.CourseInstructor)
        .join(models.Course)
        .filter(models.Enrollment.student_id == student_id)
        .all()
    )

    summaries = []

    for e in enrollments:
        ci = e.course_instructor
        course = ci.course

        records = (
            db.query(models.AttendanceRecord)
            .filter(
                models.AttendanceRecord.student_id == student_id,
                models.AttendanceRecord.course_instructors_id == ci.id,
            )
            .all()
        )

        total_sessions = len(records)
        present = sum(1 for r in records if r.status == "Present")
        late = sum(1 for r in records if r.status == "Late")
        absent = sum(1 for r in records if r.status == "Absent")

        absence_rate = (absent / total_sessions) * 100 if total_sessions > 0 else 0.0

        summaries.append(
            {
                "course_instructor_id": str(ci.id),
                "course_code": course.code,
                "course_name": course.name,
                "total_sessions": total_sessions,
                "present": present,
                "late": late,
                "absent": absent,
                "absence_rate": round(absence_rate, 2),
            }
        )

    return {
        "student_id": student_id,
        "generated_on": date.today().isoformat(),
        "courses": summaries,
    }


@router.get("/attendance/history/{course_instructor_id}")
def get_attendance_history_for_course(
    course_instructor_id: str,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("student")),
):
    """
    Detailed attendance records for this student in a specific class.
    """
    student_id = current_user["sub"]

    records = (
        db.query(models.AttendanceRecord)
        .filter(
            models.AttendanceRecord.student_id == student_id,
            models.AttendanceRecord.course_instructors_id == course_instructor_id,
        )
        .order_by(models.AttendanceRecord.date)
        .all()
    )

    history = []
    for r in records:
        history.append(
            {
                "date": r.date.isoformat() if r.date else None,
                "status": r.status,
                "total_duration_minutes": r.total_duration_minutes,
            }
        )

    return {
        "student_id": student_id,
        "course_instructor_id": course_instructor_id,
        "records": history,
    }


@router.get("/profile")
def get_my_profile(
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("student")),
):
    """
    Get complete student profile with all personal details.
    """
    student_id = current_user["sub"]
    
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Calculate GPA (placeholder - would need grades system)
    # For now, return a calculated value based on attendance or default
    gpa = 3.8  # Default placeholder
    
    # Check if face is enrolled (has face_encoding data)
    has_face_enrolled = bool(student.face_encoding and len(student.face_encoding) > 0)
    
    return {
        "id": str(student.id),
        "university_id": student.university_id,
        "full_name": student.full_name,
        "email": student.email,
        "major": student.major,
        "enrollment_year": student.enrollment_year,
        "gpa": gpa,
        "face_encoding": student.face_encoding if has_face_enrolled else [],
        "is_active": student.is_active,
        "created_at": student.created_at.isoformat() if student.created_at else None,
    }


@router.get("/enrollments/detailed")
def get_detailed_enrollments(
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("student")),
):
    """
    Get all enrollments with complete course and instructor details.
    """
    student_id = current_user["sub"]

    enrollments = (
        db.query(models.Enrollment)
        .join(models.CourseInstructor)
        .join(models.Course)
        .filter(models.Enrollment.student_id == student_id)
        .all()
    )

    detailed_enrollments = []
    for e in enrollments:
        ci = e.course_instructor
        course = ci.course
        instructor = ci.instructor
        
        # Get attendance stats for this enrollment
        records = (
            db.query(models.AttendanceRecord)
            .filter(
                models.AttendanceRecord.student_id == student_id,
                models.AttendanceRecord.course_instructors_id == ci.id,
            )
            .all()
        )
        
        total_sessions = len(records)
        present = sum(1 for r in records if r.status == "Present")
        late = sum(1 for r in records if r.status == "Late")
        absent = sum(1 for r in records if r.status == "Absent")
        absence_rate = (absent / total_sessions) * 100 if total_sessions > 0 else 0.0
        
        detailed_enrollments.append({
            "enrollment_id": str(e.id),
            "course": {
                "id": str(course.id),
                "code": course.code,
                "name": course.name,
                "status": course.status,
            },
            "instructor": {
                "id": str(instructor.id),
                "full_name": instructor.full_name,
                "email": instructor.email,
                "department": instructor.department,
            },
            "class_details": {
                "course_instructor_id": str(ci.id),
                "room": ci.room_num,
                "days": ci.days,
                "lecture_time": ci.lecture_time.isoformat() if ci.lecture_time else None,
            },
            "attendance_stats": {
                "total_sessions": total_sessions,
                "present": present,
                "late": late,
                "absent": absent,
                "absence_rate": round(absence_rate, 2),
            }
        })

    return {
        "student_id": student_id,
        "total_enrollments": len(detailed_enrollments),
        "enrollments": detailed_enrollments,
    }

