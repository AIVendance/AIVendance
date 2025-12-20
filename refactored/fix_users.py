
import sys
import os

# Add refactored/src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.execution import execute_query, fetch_one
from database.execution import execute_query, fetch_one
import bcrypt
from uuid import uuid4

def get_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def upsert_user(username, password, full_name, department, email):
    print(f"Processing User: {username}")
    hashed = get_hash(password)
    
    # Check if exists
    user = fetch_one("SELECT id FROM admin WHERE username = %s", (username,))
    
    if user:
        print(f"   User found (ID: {user['id']}). Updating password...")
        execute_query(
            "UPDATE admin SET password_hash = %s WHERE id = %s",
            (hashed, user['id'])
        )
        print("   ✅ Password updated.")
    else:
        print("   User NOT found. Creating...")
        new_id = str(uuid4())
        execute_query(
            """
            INSERT INTO admin (id, username, password_hash, full_name, department, email)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (new_id, username, hashed, full_name, department, email)
        )
        print("   ✅ User created.")

def fix_accounts():
    print("--- FIXING USER ACCOUNTS ---")
    
    # 1. Instructor
    upsert_user(
        username="101120568",
        password="321654",
        full_name="Instructor One",
        department="Computer Science",
        email="instructor101120568@uni.edu"
    )
    
    # 2. Admin
    upsert_user(
        username="100",
        password="987654231",
        full_name="Super Admin",
        department="Administration",
        email="admin100@uni.edu"
    )

if __name__ == "__main__":
    fix_accounts()
