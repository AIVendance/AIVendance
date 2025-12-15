from pydantic import BaseModel
from datetime import time
from typing import Optional
from uuid import UUID
from datetime import datetime

# 1. Input: What the Admin sends to create a course
class CourseCreate(BaseModel):
    code: str         # e.g., "CS101"
    name: str         # e.g., "Introduction to AI"
    status: str = "active" 

# 2. Output: What the API returns to the user
class CourseResponse(BaseModel):
    id: UUID
    code: str
    name: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
        
        # NEW: For creating a Class Section
class SectionCreate(BaseModel):
    course_id: UUID
    instructor_id: UUID  # This links to the 'admin' table (the professor)
    room_num: str        # e.g. "Lab 308"
    lecture_time: str    # Pass as string "09:30:00" for simplicity
    days: str            # e.g. "Mon,Wed"

class SectionResponse(BaseModel):
    id: UUID  # We need this ID to enroll students later!
    course_id: UUID
    room_num: str
    days: str

    class Config:
        from_attributes = True