#C:\Users\user\Documents\Graduation project\AIVendance\refactored\src\attendance\schema.py
from pydantic import BaseModel
from uuid import UUID
from datetime import date, datetime
from typing import Optional

class AttendanceCreate(BaseModel):
    student_id: UUID
    section_id: UUID # Maps to 'course_instructors_id' in DB

class AttendanceResponse(BaseModel):
    id: UUID
    student_name: str
    course_name: str
    date: date
    status: str # 'Present', 'Late', 'Absent'
    created_at: datetime

    class Config:
        from_attributes = True