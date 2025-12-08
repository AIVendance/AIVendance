from sqlalchemy import text
from refactored.src.database.connection import engine

async def execute_raw_sql(sql_command: str, parameters: dict = None):
    """
    Executes a raw SQL command directly against the database (e.g., TRUNCATE).
    """
    async with engine.connect() as conn:
        result = await conn.execute(text(sql_command), parameters)
        await conn.commit()
        return result

async def fetch_one(sql_command: str, parameters: dict = None):
    """Executes a query and returns a single row."""
    async with engine.connect() as conn:
        result = await conn.execute(text(sql_command), parameters)
        return result.first()

async def fetch_all(sql_command: str, parameters: dict = None):
    """Executes a query and returns all matching rows."""
    async with engine.connect() as conn:
        result = await conn.execute(text(sql_command), parameters)
        return result.fetchall()