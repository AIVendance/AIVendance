import sys
import os
from uuid import uuid4

# Setup path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.execution import execute_query
from authentication.auth_dependence.token import get_password_hash

def seed_data():
    print("🌱 Seeding Database with specific test accounts...")

    # 1. Define the Passwords
    student_pass = get_password_hash("9548911")
    instructor_pass = get_password_hash("321654")
    admin_pass = get_password_hash("987654231")

    # 2. Insert Student (202120473)
    # Using your schema columns: university_id, password_hash, full_name, email, major, enrollment_year
    print("... Creating Student (202120473)")
    execute_query("""
        INSERT INTO students (id, university_id, password_hash, full_name, email, major, enrollment_year)
        VALUES (%s, '202120473', %s, 'Student User', 'student@uni.edu', 'CS', 2021)
        ON CONFLICT (university_id) DO NOTHING;
    """, (str(uuid4()), student_pass))

    # 3. Insert Instructor (101120568)
    # Using your schema columns: username, password_hash, full_name, email, department
    print("... Creating Instructor (101120568)")
    execute_query("""
        INSERT INTO admin (id, username, password_hash, full_name, email, department)
        VALUES (%s, '101120568', %s, 'Instructor User', 'inst@uni.edu', 'AI Dept')
        ON CONFLICT (username) DO NOTHING;
    """, (str(uuid4()), instructor_pass))

    # 4. Insert Super Admin (100)
    print("... Creating Admin (100)")
    execute_query("""
        INSERT INTO admin (id, username, password_hash, full_name, email, department)
        VALUES (%s, '100', %s, 'Super Admin', 'admin@uni.edu', 'IT')
        ON CONFLICT (username) DO NOTHING;
    """, (str(uuid4()), admin_pass))

    print("✅ Done! Users seeded into the NEW schema.")

if __name__ == "__main__":
    seed_data()