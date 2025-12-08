from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
from refactored.src.database.connection import create_tables
# Import routers and config here as you build them
# from refactored.src.authentication.routers import router as auth_router 

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. APPLICATION STARTUP
    print("⏳ Running Database Setup...")
    # This calls the function you defined in refactored/src/database/connection.py
    await create_tables() 
    print("✅ Database is ready.")
    
    # 2. AI Engine Initialization (Will be added here later)
    yield
    # 3. APPLICATION SHUTDOWN (Clean up resources)

app = FastAPI(
    title="AIVendance System",
    description="Facial Recognition Attendance System",
    version="1.0",
    lifespan=lifespan
)

# --- Include Routers ---
# app.include_router(auth_router, prefix="/auth", tags=["Authentication"]) 
# Add your routers here

if __name__ == "__main__":
    # Note: Uvicorn will look for the object "app" in this file.
    uvicorn.run("refactored.main:app", host="0.0.0.0", port=8000, reload=True)