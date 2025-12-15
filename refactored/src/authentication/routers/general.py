from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from authentication.services.general import authenticate_user
from authentication.auth_dependence.token import get_password_hash, verify_token
from database.execution import execute_query, fetch_all, fetch_one
from uuid import uuid4

router = APIRouter()

# --- LOGIN ---
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user: raise HTTPException(status_code=401, detail="Incorrect ID or Password")
    return user

# --- ADMIN: MANAGE INSTRUCTORS ---
def get_current_admin(token: str): # Simplified check
    pass 

@router.get("/instructors", summary="List Instructors")
def get_all_instructors():
    return fetch_all("SELECT id, username, full_name, department FROM admin WHERE username != '100'")

@router.post("/register-instructor", summary="Create Instructor")
def register_instructor(username: str, password: str, full_name: str, department: str):
    check = fetch_one("SELECT id FROM admin WHERE username = %s", (username,))
    if check: raise HTTPException(status_code=400, detail="ID already exists")

    new_id = str(uuid4())
    hashed = get_password_hash(password)
    execute_query("""
        INSERT INTO admin (id, username, password_hash, full_name, department, email)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (new_id, username, hashed, full_name, department, f"{username}@uni.edu"))
    
    return {"message": "Instructor created"}