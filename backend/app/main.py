from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.api.v1 import auth, student, instructor, admin


app = FastAPI(
    title="AIVendance API",
    version="1.0.0",
)

# Frontend origins you use:
# - localhost:5173 (Vite or other dev server)
# - 127.0.0.1:5173
# - "null" allows file:// HTML opened directly from disk
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "null",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],   # GET, POST, etc.
    allow_headers=["*"],   # Content-Type, Authorization, etc.
)


# Routers
app.include_router(auth.router)          # prefix="/auth" already in router
app.include_router(student.router)       # prefix="/student" in router
app.include_router(instructor.router)    # prefix="/instructor" in router
app.include_router(admin.router)         # prefix="/admin" in router


# Mount static files directory
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")


@app.get("/")
def root():
    """Serve the frontend HTML"""
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    index_file = os.path.join(static_dir, "index.html")
    return FileResponse(index_file)

