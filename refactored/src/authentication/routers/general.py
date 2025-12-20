from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from authentication.services.general import authenticate_user
from authentication.auth_dependence.token import get_password_hash, verify_token
from database.execution import execute_query, fetch_all, fetch_one
from uuid import uuid4

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# --- LOGIN ---
@router.post("/login")
def login(
    role: str = Query("student"),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Unified login endpoint for students, instructors, and admins.
    Accepts username/ID, password, and role via OAuth2 form data and Query param.
    """
    user = authenticate_user(form_data.username, form_data.password, role)
    if not user:
        raise HTTPException(
            status_code=401, 
            detail="Incorrect ID or Password. Make sure the account exists in the database."
        )
    return user

# --- ADMIN: MANAGE INSTRUCTORS ---

def get_current_admin(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    # Check if user is admin (super_admin or instructor with admin privileges)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return payload

@router.get("/instructors", summary="List Instructors")
def get_all_instructors(user: dict = Depends(get_current_admin)):
    return fetch_all("SELECT id, username, full_name, department FROM admin WHERE username != '100'")

@router.post("/register-instructor", summary="Create Instructor")
def register_instructor(
    username: str, 
    password: str, 
    full_name: str, 
    department: str,
    user: dict = Depends(get_current_admin)
):
    check = fetch_one("SELECT id FROM admin WHERE username = %s", (username,))
    if check: raise HTTPException(status_code=400, detail="ID already exists")

    new_id = str(uuid4())
    hashed = get_password_hash(password)
    execute_query("""
        INSERT INTO admin (id, username, password_hash, full_name, department, email)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (new_id, username, hashed, full_name, department, f"{username}@uni.edu"))
    
    return {"message": "Instructor created"}