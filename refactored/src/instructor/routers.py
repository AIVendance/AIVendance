#C:\Users\user\Documents\Graduation project\AIVendance\refactored\src\instructor\routers.py
from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordBearer
from authentication.auth_dependence.token import verify_token, get_password_hash
from .services import get_instructor_classes_service
from database.execution import execute_query, fetch_one, fetch_all

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid Authentication Credentials")
    return payload

@router.post("/create", summary="Create Instructor (Admin)")
def create_instructor(
    username: str = Body(...),
    full_name: str = Body(...),
    password: str = Body(...),
    department: str = Body(default="General"),
    user: dict = Depends(get_current_user)
):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    # Check existence
    if fetch_one("SELECT id FROM admin WHERE username = %s", (username,)):
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed = get_password_hash(password)
    execute_query("""
        INSERT INTO admin (username, full_name, password_hash) 
        VALUES (%s, %s, %s)
    """, (username, full_name, hashed))
    
    return {"message": "Instructor created successfully"}

@router.get("/", summary="List All Instructors (Admin)")
def list_instructors(user: dict = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    # Filter out super admin "100" and "1"
    return fetch_all("SELECT id, username, full_name FROM admin WHERE username NOT IN ('1', '100')")

@router.get("/my-classes", summary="Get My Teaching Schedule")
def get_my_classes(user: dict = Depends(get_current_user)):
    # The token contains the user's ID in the 'sub' field
    instructor_id = user.get("sub")
    
    classes = get_instructor_classes_service(instructor_id)
    return classes