# AIVendance Setup Guide

## Quick Start

### 1. Database Setup
First, ensure your PostgreSQL database is running and create the tables:
```bash
python create_tables.py
```

### 2. Create Admin Account (Username: 1, Password: 1)
Run the script to create the test admin account:
```bash
python create_admin_1.py
```

This will create an admin account with:
- **Username**: `1`
- **Password**: `1`
- **Role**: `super_admin`

### 3. Start the Server
```bash
python main.py
```

The server will start on `http://127.0.0.1:8000`

## User Roles

### Super Admin (Username: 1 or 100)
- Full access to all admin features
- Can create students, instructors, and courses
- Can assign instructors to courses
- Can enroll students in classes

### Instructor
- View assigned classes and schedules
- View student rosters
- View attendance statistics

### Student
- View personal information and schedule
- View attendance statistics
- Enroll face photos for recognition (max 10 photos)

## Testing Page

Access the testing page at: `http://127.0.0.1:8000/test`

Login credentials:
- **Username**: `1`
- **Password**: `1`

Features:
- Select a class section
- Start camera
- Test face recognition in real-time
- View recognition results

## API Endpoints

### Authentication
- `POST /auth/login` - Login (returns token and role)
- `GET /auth/instructors` - List all instructors (admin only)
- `POST /auth/register-instructor` - Create instructor (admin only)

### Students
- `POST /students/create` - Create student account (admin only)
- `GET /students/` - List all students (admin only)
- `GET /students/me` - Get current student profile
- `POST /students/upload-face` - Upload face photos for enrollment
- `GET /students/my-classes` - Get enrolled classes
- `GET /students/my-stats` - Get attendance statistics

### Courses
- `GET /classes/` - List all courses
- `POST /classes/` - Create course (admin only)
- `GET /classes/sections/all` - Get all class sections
- `POST /classes/sections` - Assign instructor to course (admin only)

### Enrollment
- `GET /enrollment/` - List all enrollments (admin only)
- `POST /enrollment/` - Enroll student in class

### Attendance
- `GET /attendance/history` - Get attendance history (filter by section_id or student_id)
- `POST /attendance/mark` - Manually mark attendance

### AI Recognition
- `POST /ai/recognize` - Recognize face and mark attendance

## Frontend Pages

- `/` - Login page
- `/dashboard/admin` - Admin dashboard
- `/dashboard/student` - Student dashboard
- `/dashboard/instructor` - Instructor dashboard
- `/test` - Face recognition testing page

## Notes

- All API endpoints require authentication via Bearer token (except `/auth/login`)
- Token is stored in `localStorage` after login
- Face recognition uses cosine similarity with threshold of 0.5
- Maximum 10 photos can be uploaded for face enrollment
- Attendance is marked automatically when a face is recognized

