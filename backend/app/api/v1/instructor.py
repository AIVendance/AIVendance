from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, require_role
from app.db import schema as models

router = APIRouter(prefix="/instructor", tags=["instructor"])


# ---------- Pydantic models for attendance ----------

class AttendanceItem(BaseModel):
    student_id: str
    status: str  # "Present", "Absent", "Late"
    total_duration_minutes: int | None = None


class MarkAttendanceRequest(BaseModel):
    date: date
    records: List[AttendanceItem]


# ---------- Dashboard and Summary Endpoints ----------

@router.get("/dashboard")
def instructor_dashboard(
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("instructor")),
):
    """
    Instructor dashboard with profile info and teaching statistics.
    """
    instructor_id = current_user["sub"]
    
    instructor = db.query(models.Admin).filter(models.Admin.id == instructor_id).first()
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor not found")
    
    # Get teaching statistics
    assignments = (
        db.query(models.CourseInstructor)
        .filter(models.CourseInstructor.instructor_id == instructor_id)
        .all()
    )
    
    total_courses = len(assignments)
    total_students = 0
    total_attendance_records = 0
    
    for ci in assignments:
        enrollments = (
            db.query(models.Enrollment)
            .filter(models.Enrollment.course_instructors_id == ci.id)
            .all()
        )
        total_students += len(enrollments)
        
        records = (
            db.query(models.AttendanceRecord)
            .filter(models.AttendanceRecord.course_instructors_id == ci.id)
            .all()
        )
        total_attendance_records += len(records)
    
    return {
        "instructor": {
            "id": str(instructor.id),
            "username": instructor.username,
            "full_name": instructor.full_name,
            "email": instructor.email,
            "department": instructor.department,
            "is_active": instructor.is_active,
        },
        "statistics": {
            "total_courses_teaching": total_courses,
            "total_students_teaching": total_students,
            "total_attendance_records_created": total_attendance_records,
        }
    }


@router.get("/profile")
def get_instructor_profile(
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("instructor")),
):
    """
    Get complete instructor profile with all personal details.
    """
    instructor_id = current_user["sub"]
    
    instructor = db.query(models.Admin).filter(models.Admin.id == instructor_id).first()
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor not found")
    
    return {
        "id": str(instructor.id),
        "username": instructor.username,
        "full_name": instructor.full_name,
        "email": instructor.email,
        "department": instructor.department,
        "is_active": instructor.is_active,
        "created_at": instructor.created_at.isoformat() if instructor.created_at else None,
    }


# ---------- Existing endpoints ----------

@router.get("/courses")
def get_my_courses(
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("instructor")),
):
    instructor_id = current_user["sub"]

    assignments = (
        db.query(models.CourseInstructor)
        .join(models.Course)
        .filter(models.CourseInstructor.instructor_id == instructor_id)
        .all()
    )

    result = []
    for ci in assignments:
        course = ci.course
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
            }
        )

    return {"instructor_id": instructor_id, "courses": result}


@router.get("/courses/{course_instructor_id}/students")
def get_course_students(
    course_instructor_id: str,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("instructor")),
):
    """
    Students enrolled in this class with their attendance summary.
    """
    instructor_id = current_user["sub"]

    ci = (
        db.query(models.CourseInstructor)
        .filter(
            models.CourseInstructor.id == course_instructor_id,
            models.CourseInstructor.instructor_id == instructor_id,
        )
        .first()
    )
    if not ci:
        raise HTTPException(status_code=404, detail="Course not found")

    enrollments = (
        db.query(models.Enrollment)
        .join(models.Student)
        .filter(models.Enrollment.course_instructors_id == course_instructor_id)
        .all()
    )

    students_data = []

    for e in enrollments:
        student = e.student

        records = (
            db.query(models.AttendanceRecord)
            .filter(
                models.AttendanceRecord.student_id == student.id,
                models.AttendanceRecord.course_instructors_id == course_instructor_id,
            )
            .all()
        )

        total_sessions = len(records)
        present = sum(1 for r in records if r.status == "Present")
        late = sum(1 for r in records if r.status == "Late")
        absent = sum(1 for r in records if r.status == "Absent")
        absence_rate = (absent / total_sessions) * 100 if total_sessions > 0 else 0.0

        students_data.append(
            {
                "student_id": str(student.id),
                "university_id": student.university_id,
                "full_name": student.full_name,
                "email": student.email,
                "total_sessions": total_sessions,
                "present": present,
                "late": late,
                "absent": absent,
                "absence_rate": round(absence_rate, 2),
            }
        )

    return {
        "course_instructor_id": course_instructor_id,
        "students": students_data,
    }


@router.get("/attendance/statistics")
def get_attendance_statistics(
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("instructor")),
):
    """
    Get comprehensive attendance statistics across all instructor's courses.
    """
    instructor_id = current_user["sub"]

    courses = (
        db.query(models.CourseInstructor)
        .filter(models.CourseInstructor.instructor_id == instructor_id)
        .all()
    )

    all_statistics = []

    for ci in courses:
        course = ci.course
        records = (
            db.query(models.AttendanceRecord)
            .filter(models.AttendanceRecord.course_instructors_id == ci.id)
            .all()
        )

        if not records:
            all_statistics.append({
                "course_instructor_id": str(ci.id),
                "course_code": course.code,
                "course_name": course.name,
                "total_attendance_records": 0,
                "summary": {
                    "present": 0,
                    "late": 0,
                    "absent": 0,
                    "average_absence_rate": 0.0
                }
            })
            continue

        present = sum(1 for r in records if r.status == "Present")
        late = sum(1 for r in records if r.status == "Late")
        absent = sum(1 for r in records if r.status == "Absent")

        all_statistics.append({
            "course_instructor_id": str(ci.id),
            "course_code": course.code,
            "course_name": course.name,
            "total_attendance_records": len(records),
            "summary": {
                "present": present,
                "late": late,
                "absent": absent,
                "average_absence_rate": round((absent / len(records)) * 100, 2) if records else 0.0
            }
        })

    return {
        "instructor_id": instructor_id,
        "total_courses": len(courses),
        "courses_statistics": all_statistics,
    }


@router.get("/courses/{course_instructor_id}/attendance/summary")
def get_course_attendance_summary(
    course_instructor_id: str,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("instructor")),
):
    """
    Get attendance summary by date for a specific course.
    """
    instructor_id = current_user["sub"]

    ci = (
        db.query(models.CourseInstructor)
        .filter(
            models.CourseInstructor.id == course_instructor_id,
            models.CourseInstructor.instructor_id == instructor_id,
        )
        .first()
    )
    if not ci:
        raise HTTPException(status_code=404, detail="Course not found")

    records = (
        db.query(models.AttendanceRecord)
        .filter(models.AttendanceRecord.course_instructors_id == course_instructor_id)
        .order_by(models.AttendanceRecord.date.desc())
        .all()
    )

    # Group by date
    from collections import defaultdict
    by_date = defaultdict(lambda: {"present": 0, "late": 0, "absent": 0, "total": 0})

    for r in records:
        date_str = r.date.isoformat() if r.date else "unknown"
        by_date[date_str][r.status.lower()] += 1
        by_date[date_str]["total"] += 1

    attendance_by_date = []
    for date_str in sorted(by_date.keys(), reverse=True):
        stats = by_date[date_str]
        attendance_by_date.append({
            "date": date_str,
            "present": stats.get("present", 0),
            "late": stats.get("late", 0),
            "absent": stats.get("absent", 0),
            "total_marked": stats["total"],
        })

    return {
        "course_instructor_id": course_instructor_id,
        "course_code": ci.course.code,
        "course_name": ci.course.name,
        "attendance_by_date": attendance_by_date,
    }


# ---------- NEW: mark attendance for one session ----------

@router.post("/courses/{course_instructor_id}/attendance")
def mark_attendance_for_session(
    course_instructor_id: str,
    payload: MarkAttendanceRequest = Body(...),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("instructor")),
):
    """
    Mark or update attendance for a specific date in this class.
    """
    instructor_id = current_user["sub"]

    # 1) Make sure this course belongs to this instructor
    ci = (
        db.query(models.CourseInstructor)
        .filter(
            models.CourseInstructor.id == course_instructor_id,
            models.CourseInstructor.instructor_id == instructor_id,
        )
        .first()
    )
    if not ci:
        raise HTTPException(status_code=404, detail="Course not found")

    # 2) Process each attendance item
    for item in payload.records:
        existing = (
            db.query(models.AttendanceRecord)
            .filter(
                and_(
                    models.AttendanceRecord.student_id == item.student_id,
                    models.AttendanceRecord.course_instructors_id
                    == course_instructor_id,
                    models.AttendanceRecord.date == payload.date,
                )
            )
            .first()
        )

        if existing:
            existing.status = item.status
            existing.total_duration_minutes = item.total_duration_minutes
        else:
            new_record = models.AttendanceRecord(
                student_id=item.student_id,
                course_instructors_id=course_instructor_id,
                date=payload.date,
                status=item.status,
                total_duration_minutes=item.total_duration_minutes,
            )
            db.add(new_record)

    db.commit()

    return {
        "course_instructor_id": course_instructor_id,
        "date": payload.date.isoformat(),
        "processed_records": len(payload.records),
    }
