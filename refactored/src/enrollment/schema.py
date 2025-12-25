#C:\Users\user\Documents\Graduation project\AIVendance\refactored\src\enrollment\schema.py
from pydantic import BaseModel
from uuid import UUID

class EnrollmentCreate(BaseModel):
    student_id: UUID
    section_id: UUID # This is the ID from 'course_instructors'

class EnrollmentResponse(BaseModel):
    id: UUID
    student_id: UUID
    section_id: UUID