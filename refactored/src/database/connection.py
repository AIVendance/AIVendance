# refactored/src/database/connection.py
import psycopg2
from psycopg2.extras import RealDictCursor
import sys
import os

# Adjust import based on your actual path to config.py
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.config import DB_CONFIG 

def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database.
    Returns a connection object.
    """
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG.get("host", "localhost"),
            database=DB_CONFIG.get("database", "aivendance_db"),
            user=DB_CONFIG.get("user", "postgres"),
            password=DB_CONFIG.get("password", "your_password"),
            port=DB_CONFIG.get("port", 5432)
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None