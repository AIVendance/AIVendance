# refactored/src/database/execution.py
from contextlib import contextmanager
from .connection import get_db_connection
from psycopg2.extras import RealDictCursor

@contextmanager
def get_db_cursor(commit=False):
    """
    Context manager to yield a database cursor.
    Handles commit/rollback and closing connection automatically.
    """
    conn = get_db_connection()
    if conn is None:
        raise Exception("Failed to connect to the database")
    
    # RealDictCursor allows accessing columns by name (row['id'])
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        yield cursor
        if commit:
            conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Database Query Error: {e}")
        raise e
    finally:
        cursor.close()
        conn.close()

def execute_query(query, params=None):
    """
    Executes a single query that modifies data (INSERT, UPDATE, DELETE).
    Returns: None
    """
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query, params)

def fetch_one(query, params=None):
    """
    Fetches a single row.
    Returns: Dictionary or None
    """
    with get_db_cursor(commit=False) as cursor:
        cursor.execute(query, params)
        return cursor.fetchone()

def fetch_all(query, params=None):
    """
    Fetches all rows.
    Returns: List of Dictionaries
    """
    with get_db_cursor(commit=False) as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()