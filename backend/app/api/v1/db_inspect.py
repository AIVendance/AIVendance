from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db_session
from app.db import schema as models

router = APIRouter(prefix="/db", tags=["database"])


@router.get("/inspect")
def inspect_db(db: Session = Depends(get_db_session)):
    return {
        "roles": db.query(models.Role).count(),
        "permissions": db.query(models.Permission).count(),
        "admins": db.query(models.Admin).count(),
        "admin_roles": db.query(models.AdminRole).count(),
        "role_permissions": db.query(models.RolePermission).count(),
        "students": db.query(models.Student).count(),
        "courses": db.query(models.Course).count(),
        "course_instructors": db.query(models.CourseInstructor).count(),
        "enrollments": db.query(models.Enrollment).count(),
        "attendance_records": db.query(models.AttendanceRecord).count(),
    }
# ============== End of API Definitions ==============