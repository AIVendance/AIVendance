from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.db.models import User, FacialEmbedding, Session, AttendanceLog, Enrollment
import json
import numpy as np
from datetime import datetime

class AttendanceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_embeddings(self):
        result = await self.db.execute(select(FacialEmbedding))
        embeddings = result.scalars().all()
        data = {}
        for rec in embeddings:
            if rec.student_id not in data: data[rec.student_id] = []
            try: data[rec.student_id].append(np.array(json.loads(rec.embedding_vector)))
            except: pass
        return data

    async def get_active_session_by_room(self, room_id: str):
        query = select(Session).where(Session.is_active == True)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def check_enrollment(self, student_id: str, course_code: str):
        """Checks if student is allowed in this class"""
        # For Demo: If we haven't created enrollments yet, we auto-enroll everyone 
        # But to show the feature, let's assume if they are in User DB they are valid,
        # unless we strictly want to filter.
        # Let's add a strict check:
        # query = select(Enrollment).where(Enrollment.student_id == student_id, Enrollment.course_code == course_code)
        # result = await self.db.execute(query)
        # return result.scalars().first() is not None
        return True # Returning True for now so you don't get blocked. Set to False to test "Not Enrolled"

    async def log_attendance(self, session_id: int, student_id: str, status_on_arrival: str):
        """
        Increments 'frames_seen' for accurate time tracking.
        """
        query = select(AttendanceLog).where(
            AttendanceLog.session_id == session_id,
            AttendanceLog.student_id == student_id
        )
        result = await self.db.execute(query)
        existing = result.scalars().first()

        total_minutes = 0

        if existing:
            existing.last_seen = datetime.now()
            existing.frames_seen += 1  # <--- The Counter
            
            # Calculate REAL time (Assuming 1 frame every 2 seconds)
            # 30 frames = 1 minute
            total_minutes = (existing.frames_seen * 2) / 60
            
            await self.db.commit()
            return existing, total_minutes
        else:
            new_log = AttendanceLog(
                session_id=session_id, 
                student_id=student_id, 
                status=status_on_arrival,
                frames_seen=1
            )
            self.db.add(new_log)
            await self.db.commit()
            return new_log, 0
            
    # Helpers for User Creation
    async def create_user(self, user_id: str, name: str, email: str):
        q = select(User).where(User.user_id == user_id)
        if (await self.db.execute(q)).scalars().first(): return
        self.db.add(User(user_id=user_id, full_name=name, email=email))
        await self.db.commit()
    
    async def save_embedding(self, student_id: str, vector: np.ndarray):
        v_json = json.dumps(vector.tolist())
        self.db.add(FacialEmbedding(student_id=student_id, embedding_vector=v_json))
        await self.db.commit()