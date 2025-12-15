import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 1. Add 'src' to path so imports work
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import Routers
from authentication.routers import general as auth_router # <--- Unified Login
from classes.routers import router as classes_router
from student.routers import router as student_router
from enrollment.routers import router as enrollment_router
from instructor.routers import router as instructor_router
from attendance.routers import router as attendance_router
from ai.routers import router as ai_router

# 2. Initialize the App
app = FastAPI(
    title="AIVendance API",
    description="Backend for Intelligent Vision-Based Attendance System",
    version="1.0.0"
)

# 3. Enable CORS (Crucial for your Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Register Routers

# Unified Authentication (Smart Login) - Matches your seeded users!
app.include_router(
    auth_router.router, 
    prefix="/auth", 
    tags=["Authentication"]
)

# Course Management
app.include_router(classes_router, prefix="/classes", tags=["Course Management"])

# Student Management
app.include_router(student_router, prefix="/students", tags=["Student Management"])

# Enrollment
app.include_router(enrollment_router, prefix="/enrollment", tags=["Enrollment"])

# Instructor Dashboard
app.include_router(instructor_router, prefix="/instructor", tags=["Instructor Dashboard"])

# Attendance Records
app.include_router(attendance_router, prefix="/attendance", tags=["Attendance Records"])

# AI Recognition
app.include_router(ai_router, prefix="/ai", tags=["AI Recognition"])

@app.get("/")
def root():
    return {"message": "AIVendance System is Running 🚀"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)