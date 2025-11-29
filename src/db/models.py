from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, Text, Time, Date
from sqlalchemy.sql import func
from src.db.database import Base

class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, default="Student")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Enrollment(Base):
    """Links Students to Courses"""
    __tablename__ = "enrollments"
    enrollment_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("users.user_id"))
    course_code = Column(String, nullable=False) # e.g. CS101

class FacialEmbedding(Base):
    __tablename__ = "facial_embeddings"
    embedding_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    embedding_vector = Column(Text, nullable=False) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Course(Base):
    __tablename__ = "courses"
    course_id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String, nullable=False)
    title = Column(String, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_active = Column(Boolean, default=True)

class Session(Base):
    __tablename__ = "sessions"
    session_id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.course_id"))
    # We store course_code here too for easier lookup
    course_code = Column(String, nullable=False) 
    actual_start_time = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

class AttendanceLog(Base):
    __tablename__ = "attendance_logs"
    log_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.session_id"))
    student_id = Column(String, ForeignKey("users.user_id"))
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), onupdate=func.now())
    
    # NEW: The counter for exact time tracking
    frames_seen = Column(Integer, default=1) 
    
    status = Column(String, default="Present")