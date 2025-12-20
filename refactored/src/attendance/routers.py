from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from authentication.auth_dependence.token import verify_token
from fastapi.security import OAuth2PasswordBearer
from .schema import AttendanceCreate
from .services import mark_attendance_service, get_attendance_history_service

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return payload

@router.post("/mark", summary="Manually Mark Attendance")
def mark_attendance(data: AttendanceCreate, user: dict = Depends(get_current_user)):
    result = mark_attendance_service(data)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/history", summary="View Attendance Logs")
def view_attendance(
    section_id: Optional[str] = None, 
    student_id: Optional[str] = None, 
    user: dict = Depends(get_current_user)
):
    return get_attendance_history_service(student_id, section_id)