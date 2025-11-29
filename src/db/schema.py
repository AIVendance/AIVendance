from pydantic import BaseModel
from typing import List, Optional

class StudentCreate(BaseModel):
    student_id: str
    full_name: str

class SessionStart(BaseModel):
    classroom_id: str

class RecognitionResponse(BaseModel):
    results: List[dict]