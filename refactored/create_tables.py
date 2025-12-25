#C:\Users\user\Documents\Graduation project\AIVendance\refactored\create_tables.py
import sys
import os

# Setup path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.execution import execute_query

def create_tables():
    print("🔨 Applying YOUR Custom Database Schema...")

    # 1. Enable UUID Extension (Crucial for your schema)
    print("... Enabling UUID extension")
    execute_query('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

    queries = [
        # ==========================================
        # 1. USERS & ROLES (Admin Side)
        # ==========================================
        """
        CREATE TABLE IF NOT EXISTS roles (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            name VARCHAR(50) NOT NULL UNIQUE,
            slug VARCHAR(50) NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS permissions (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            action VARCHAR(100) NOT NULL,
            access_type VARCHAR(20),
            description TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS admin (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            username VARCHAR(50) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE,
            department VARCHAR(100),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS admin_roles (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            admin_id UUID NOT NULL REFERENCES admin(id) ON DELETE CASCADE,
            role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(admin_id, role_id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS role_permissions (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
            permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(role_id, permission_id)
        );
        """,

        # ==========================================
        # 2. STUDENTS
        # ==========================================
        """
        CREATE TABLE IF NOT EXISTS students (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            university_id VARCHAR(50) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE,
            major VARCHAR(100),
            enrollment_year INT,
            face_encoding FLOAT8[],
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """,

        # ==========================================
        # 3. ACADEMIC STRUCTURE
        # ==========================================
        """
        CREATE TABLE IF NOT EXISTS courses (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            code VARCHAR(20) UNIQUE,
            name VARCHAR(100),
            status VARCHAR(20),
            created_by_admin_id UUID REFERENCES admin(id) ON DELETE SET NULL,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS course_instructors (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
            instructor_id UUID REFERENCES admin(id) ON DELETE CASCADE,
            room_num VARCHAR(20),
            lecture_time TIME,
            days VARCHAR(50),
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS enrollments (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            student_id UUID REFERENCES students(id) ON DELETE CASCADE,
            course_instructors_id UUID REFERENCES course_instructors(id) ON DELETE CASCADE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(student_id, course_instructors_id)
        );
        """,

        # ==========================================
        # 4. ATTENDANCE
        # ==========================================
        """
        CREATE TABLE IF NOT EXISTS attendance_records (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            student_id UUID REFERENCES students(id) ON DELETE CASCADE,
            course_instructors_id UUID REFERENCES course_instructors(id) ON DELETE CASCADE,
            date DATE DEFAULT CURRENT_DATE,
            status VARCHAR(20),
            total_duration_minutes INTEGER,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """
    ]

    for q in queries:
        try:
            execute_query(q)
        except Exception as e:
            print(f"⚠️ Error creating table: {e}")
            # Raise error so we know if something failed
            raise e

    print("✅ All tables created successfully using YOUR schema!")

if __name__ == "__main__":
    create_tables()