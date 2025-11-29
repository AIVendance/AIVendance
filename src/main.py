from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import attendance, enrollment, classrooms
from src.db.database import engine, Base

app = FastAPI(title="AIVendance API", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Force creation of tables
    print("⏳ Checking Database Tables...")
    async with engine.begin() as conn:
        # This command creates any table defined in models.py that doesn't exist in Postgres
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database Tables Ready")

app.include_router(attendance.router, tags=["Attendance"])
app.include_router(enrollment.router, tags=["Enrollment"])
app.include_router(classrooms.router, tags=["Classrooms"])

@app.get("/")
def root():
    return {"system": "AIVendance V3", "status": "Online"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)