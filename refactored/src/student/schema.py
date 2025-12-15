from pydantic import BaseModel, EmailStr
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class StudentCreate(BaseModel):
    university_id: str  # e.g. "20231010"
    full_name: str
    email: EmailStr
    major: str
    enrollment_year: int
    password: str       # We will hash this before saving

class StudentResponse(BaseModel):
    id: UUID
    university_id: str
    full_name: str
    email: Optional[str] = None
    major: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True