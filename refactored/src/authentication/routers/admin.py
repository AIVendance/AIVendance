#C:\Users\user\Documents\Graduation project\AIVendance\refactored\src\authentication\routers\admin.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from authentication.services.admin import authenticate_admin

router = APIRouter()

# Schema for the login input
class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(request: LoginRequest):
    token = authenticate_admin(request.username, request.password)
    
    if not token:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    return {"access_token": token, "token_type": "bearer"}