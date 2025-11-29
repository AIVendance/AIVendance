from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.db.database import get_db
from src.db.models import Session, Course
from datetime import time

router = APIRouter()

@router.post("/classroom/{classroom_id}/start")
async def start_class(classroom_id: str, db: AsyncSession = Depends(get_db)):
    """
    Starts a new session for a specific classroom.
    """
    # 1. Check if there is a course in this room
    # In a real app, you would filter by room_id or time. 
    # For this demo, we pick the first course or create a dummy one.
    result = await db.execute(select(Course))
    course = result.scalars().first()
    
    if not course:
        # Create a dummy course if none exists
        # NOTE: We use time(8, 0, 0) to avoid "str has no attribute hour" errors
        course = Course(
            course_code="CS101", 
            title="Intro to Computer Science", 
            start_time=time(8, 0, 0),
            end_time=time(10, 0, 0),
            is_active=True
        )
        db.add(course)
        await db.commit()
        await db.refresh(course)

    # 2. Create the Session
    # We now include course_code because the new Session model requires it
    new_session = Session(
        course_id=course.course_id,
        course_code=course.course_code, # <--- CRITICAL UPDATE
        is_active=True
    )
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)

    return {
        "message": f"Class session started in {classroom_id}",
        "session_id": new_session.session_id,
        "course": course.title,
        "course_code": course.course_code
    }

@router.post("/classroom/{classroom_id}/stop")
async def stop_class(classroom_id: str, db: AsyncSession = Depends(get_db)):
    """
    Stops the active session.
    """
    # Find active session
    result = await db.execute(select(Session).where(Session.is_active == True))
    active_sessions = result.scalars().all()
    
    count = 0
    for session in active_sessions:
        session.is_active = False
        count += 1
    
    await db.commit()
    
    return {"message": "Class stopped", "sessions_closed": count}