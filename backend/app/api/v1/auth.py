from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, get_current_user
from app.db import schema as models
from app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
)
from .auth_schemas import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/ping")
def ping(db: Session = Depends(get_db_session)):
    admin_count = db.query(models.Admin).count()
    student_count = db.query(models.Student).count()
    return {"status": "ok", "admins": admin_count, "students": student_count}


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db_session)):
    """
    Unified login endpoint.
    Uses pbkdf2_sha256 to verify passwords against stored hashes.
    Validates that the selected role matches the user's actual role.
    """
    role = data.role.lower()

    # Student login by university_id
    if role == "student":
        user = (
            db.query(models.Student)
            .filter(models.Student.university_id == data.user_id)
            .first()
        )
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid student credentials",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Student account is inactive",
            )
        token = create_access_token(subject=str(user.id), role="student")
        return TokenResponse(
            access_token=token,
            role="student",
            user_id=user.university_id,
            full_name=user.full_name,
        )

    # Instructor/Admin login by username
    if role in {"instructor", "admin"}:
        user = (
            db.query(models.Admin)
            .filter(models.Admin.username == data.user_id)
            .first()
        )
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid {role} credentials",
            )
        
        # Validate that user's actual role matches the selected role
        if user.role.lower() != role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"This account is registered as {user.role}, not {role}. Please select the correct role.",
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{role.capitalize()} account is inactive",
            )
        
        token = create_access_token(subject=str(user.id), role=role)
        return TokenResponse(
            access_token=token,
            role=role,
            user_id=user.username,
            full_name=user.full_name,
        )

    # Should not reach here because of Pydantic validation
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unsupported role",
    )


@router.get("/me")
def read_me(current_user: dict = Depends(get_current_user)):
    """
    Simple protected endpoint to verify JWT works.
    """
    return {
        "user_id": current_user.get("sub"),
        "role": current_user.get("role"),
    }


# ---- Debug utilities (for development only) ----
# NOTE: Remove the following debug endpoints in production!
# These endpoints should only be used during development for debugging purposes.

@router.get("/debug/student/{university_id}")
def debug_student(university_id: str, db: Session = Depends(get_db_session)):
    """
    Returns basic info and stored password_hash for a student.
    Useful only for debugging during development.
    REMOVE THIS ENDPOINT IN PRODUCTION!
    """
    student = (
        db.query(models.Student)
        .filter(models.Student.university_id == university_id)
        .first()
    )
    if not student:
        return {"exists": False}
    return {
        "exists": True,
        "university_id": student.university_id,
        "full_name": student.full_name,
        "stored_password_hash": student.password_hash,
    }


@router.post("/debug/hash-passwords")
def debug_hash_passwords(db: Session = Depends(get_db_session)):
    """
    One-time helper to hash known plain-text passwords using pbkdf2_sha256.
    After running once and confirming, you can delete this endpoint.
    REMOVE THIS ENDPOINT IN PRODUCTION!
    """
    # Student
    student = (
        db.query(models.Student)
        .filter(models.Student.university_id == "202120473")
        .first()
    )
    if student:
        student.password_hash = get_password_hash("9548911")

    # Instructor
    instructor = (
        db.query(models.Admin)
        .filter(models.Admin.username == "101120568")
        .first()
    )
    if instructor:
        instructor.password_hash = get_password_hash("321654")

    # Admin
    admin = (
        db.query(models.Admin)
        .filter(models.Admin.username == "100")
        .first()
    )
    if admin:
        admin.password_hash = get_password_hash("987654231")

    db.commit()
    return {"status": "updated"}
