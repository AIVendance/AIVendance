-- --- SETUP: Enable UUID generation ---
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- --- 1. CORE IDENTITY & ROLES ---

-- Core Role Definitions
CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) UNIQUE NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

-- Central Authentication Table (Unified Login)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(100) UNIQUE NOT NULL, -- Used for login (University ID/Employee ID)
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE,
    role_id UUID NOT NULL REFERENCES roles(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE
);

-- Permissions (For granular access)
CREATE TABLE IF NOT EXISTS permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role_id UUID NOT NULL REFERENCES roles(id),
    action VARCHAR(100) NOT NULL, -- e.g., 'create_course', 'delete_user'
    description TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    UNIQUE (role_id, action)
);

-- --- 2. PROFILE TABLES (Linked 1:1 to users.id) ---

-- Admin Profile
CREATE TABLE IF NOT EXISTS admins (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    full_name VARCHAR(100),
    phone VARCHAR(20),
    last_audit_log TIMESTAMP WITHOUT TIME ZONE
);

-- Instructor Profile
CREATE TABLE IF NOT EXISTS instructors (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    full_name VARCHAR(100),
    department VARCHAR(50),
    office_location VARCHAR(100)
);

-- Student Profile (Includes Face Data)
CREATE TABLE IF NOT EXISTS students (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    university_id VARCHAR(20) UNIQUE, 
    full_name VARCHAR(100) NOT NULL,
    major VARCHAR(50),
    enrollment_year INT,
    face_encoding FLOAT8[] NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

-- --- 3. ACADEMIC & SESSION STRUCTURE ---

-- Course Catalog
CREATE TABLE IF NOT EXISTS courses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL,
    hours INT,
    times VARCHAR(100),
    
    -- Audit Fields
    instructor_id UUID REFERENCES instructors(user_id),
    created_by_admin_id UUID REFERENCES admins(user_id),
    
    students_count INT DEFAULT 0,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE
);

-- Student Enrollment to a Course
CREATE TABLE IF NOT EXISTS enrollments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES students(user_id),
    course_id UUID NOT NULL REFERENCES courses(id),
    room_id VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE,
    UNIQUE (student_id, course_id)
);

-- Specific Instance of a Class on a Date
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID NOT NULL REFERENCES courses(id),
    date DATE NOT NULL,
    actual_start_time TIMESTAMP WITHOUT TIME ZONE,
    actual_end_time TIMESTAMP WITHOUT TIME ZONE,
    status VARCHAR(20) DEFAULT 'scheduled',
    
    -- Audit Field: Modified By Admin
    modified_by_admin_id UUID REFERENCES admins(user_id),
    
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

-- --- 4. ATTENDANCE TRACKING ---

-- Raw Data Logs
CREATE TABLE IF NOT EXISTS attendance_logs (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions(id),
    student_id UUID NOT NULL REFERENCES students(user_id),
    seen_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

-- Final Calculated Records
CREATE TABLE IF NOT EXISTS attendance_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id),
    student_id UUID NOT NULL REFERENCES students(user_id),
    
    arrival_time TIMESTAMP WITHOUT TIME ZONE,
    total_duration_minutes INT NOT NULL,
    status VARCHAR(20) NOT NULL,
    
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    UNIQUE (session_id, student_id)
);