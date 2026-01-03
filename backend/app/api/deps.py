from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.connection import get_db
from app.core.security import decode_access_token

# Swagger will use this to know that endpoints expect a Bearer token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db_session(db: Session = Depends(get_db)) -> Session:
    """
    Provides a SQLAlchemy Session to path operations.
    """
    return db


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Decodes the JWT access token and returns its payload.
    Raises 401 if the token is missing or invalid.
    """
    try:
        payload = decode_access_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload  # contains sub, role, exp


def require_role(*allowed_roles: str):
    """
    Dependency factory to restrict access by role.

    Usage in endpoints:
        current_user = Depends(require_role("student"))
        current_user = Depends(require_role("instructor", "admin"))
        current_user = Depends(require_role("admin"))  # admin only
    """
    allowed = {r.lower() for r in allowed_roles}

    def _checker(current_user: dict = Depends(get_current_user)) -> dict:
        role = str(current_user.get("role", "")).lower()
        if role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This operation requires one of the following roles: {', '.join(allowed_roles)}",
            )
        return current_user

    return _checker


def require_admin_role():
    """
    Dependency to restrict access to ADMIN ONLY.
    
    Usage:
        current_user = Depends(require_admin_role())
    """
    def _checker(current_user: dict = Depends(get_current_user)) -> dict:
        role = str(current_user.get("role", "")).lower()
        if role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This operation requires administrator privileges",
            )
        return current_user
    
    return _checker


def require_instructor_role():
    """
    Dependency to restrict access to INSTRUCTOR ONLY.
    
    Usage:
        current_user = Depends(require_instructor_role())
    """
    def _checker(current_user: dict = Depends(get_current_user)) -> dict:
        role = str(current_user.get("role", "")).lower()
        if role != "instructor":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This operation requires instructor privileges",
            )
        return current_user
    
    return _checker


def require_student_role():
    """
    Dependency to restrict access to STUDENT ONLY.
    
    Usage:
        current_user = Depends(require_student_role())
    """
    def _checker(current_user: dict = Depends(get_current_user)) -> dict:
        role = str(current_user.get("role", "")).lower()
        if role != "student":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This operation is only available to students",
            )
        return current_user
    
    return _checker
