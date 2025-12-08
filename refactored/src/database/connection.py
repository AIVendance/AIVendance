import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import text

# --- Configuration ---
# NOTE: Using the specified password (9548911)
DATABASE_URL = "postgresql+asyncpg://postgres:9548911@localhost:5432/aivendance_db"

# Create the asynchronous engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True to see SQL logs
    future=True
)

# Base class for SQLAlchemy models 
Base = declarative_base()

# Session maker setup
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# --- Dependency/Utility Function ---
async def get_db():
    """
    FastAPI dependency that provides an asynchronous database session.
    """
    async with AsyncSessionLocal() as session:
        yield session

# --- Table Creation from SQL File ---
async def create_tables():
    """
    Executes the schema.sql file to build the database structure.
    This should be called once on application startup (in main.py).
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sql_file_path = os.path.join(current_dir, "schema.sql")

    try:
        with open(sql_file_path, 'r') as f:
            sql_script = f.read()
        
        async with engine.begin() as conn:
            # Execute the entire SQL script
            await conn.execute(text(sql_script))
        
        print(" Database schema created successfully from schema.sql")
        
    except FileNotFoundError:
        print(f" Error: schema.sql not found at {sql_file_path}")
    except Exception as e:
        print(f" Database Schema Creation Error: {e}")