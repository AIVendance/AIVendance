from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.db import schema as models

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/ping")
def ping(db: Session = Depends(get_db_session)):
    """
    Simple endpoint to verify DB connectivity and that Admin/Student models work.
    """
    admin_count = db.query(models.Admin).count()
    student_count = db.query(models.Student).count()
    return {
        "status": "ok",
        "admins": admin_count,
        "students": student_count,
    }
