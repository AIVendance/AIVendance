import sys
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Setup Path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import Routers
from authentication.routers import general as auth_router
from classes.routers import router as classes_router
from student.routers import router as student_router
from enrollment.routers import router as enrollment_router
from instructor.routers import router as instructor_router
from attendance.routers import router as attendance_router
from ai.routers import router as ai_router

app = FastAPI()

# 1. API Routers
app.include_router(auth_router.router, prefix="/auth", tags=["Authentication"])
app.include_router(classes_router, prefix="/classes", tags=["Classes"])
app.include_router(student_router, prefix="/students", tags=["Students"])
app.include_router(enrollment_router, prefix="/enrollment", tags=["Enrollment"])
app.include_router(instructor_router, prefix="/instructor", tags=["Instructor"])
app.include_router(attendance_router, prefix="/attendance", tags=["Attendance"])
app.include_router(ai_router, prefix="/ai", tags=["AI"])

# 2. Serve Static Files
frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
if not os.path.exists(frontend_dir):
    os.makedirs(frontend_dir)
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# 3. Page Routes

@app.get("/")
async def read_login():
    return FileResponse(os.path.join(frontend_dir, 'login.html'))

# --- Admin Pages ---
@app.get("/dashboard/admin")
async def admin_dashboard():
    return FileResponse(os.path.join(frontend_dir, 'admin.html'))

@app.get("/dashboard/admin/students")
async def admin_students_dashboard():
    return FileResponse(os.path.join(frontend_dir, 'admin_students.html'))

@app.get("/dashboard/admin/instructors")
async def admin_instructors_dashboard():
    return FileResponse(os.path.join(frontend_dir, 'admin_instructors.html'))

@app.get("/dashboard/admin/courses")
async def admin_courses_dashboard():
    return FileResponse(os.path.join(frontend_dir, 'admin_courses.html'))

@app.get("/dashboard/admin/enrollment")
async def admin_enrollment_dashboard():
    return FileResponse(os.path.join(frontend_dir, 'admin_enrollment.html'))

# --- Instructor Pages ---
@app.get("/dashboard/instructor")
async def instructor_dashboard():
    return FileResponse(os.path.join(frontend_dir, 'instructor.html'))

# --- Student Pages ---
@app.get("/dashboard/student")
async def student_dashboard():
    return FileResponse(os.path.join(frontend_dir, 'student.html'))

# --- NEW TESTING ROUTE (Strictly points to AItest.html) ---
@app.get("/testing", tags=["Debug"])
async def debug_page():
    return FileResponse(os.path.join(frontend_dir, 'AItest.html'))

if __name__ == "__main__":
    import uvicorn
    import platform
    # Disable reloader on Windows to avoid DLL loading issues with cv2 if needed
    use_reload = platform.system() != "Windows"
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=use_reload)