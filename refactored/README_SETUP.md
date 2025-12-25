# AIVendance Setup Guide

## Quick Start

### 1. requirements.txt
First download the requirements file 
''' bash 
pip install -r requirements.txt
'''

### 2. create the connection to the database 
'''
in the pg admin create a server with the name aivendance_db and connect it to 
the server adress is 127.0.0.1 , the port is 5432 , and the password is optinal 
but mine is 9548911
'''

### 3. Database Setup
First, ensure your PostgreSQL database is running and create the tables:
this command in the bash runs a python file that creates the tabels from vs code 
```bash
python create_tables.py
```
### 3. basic accounts in the database 
this step is for creating the 3 basic accounts we are working with 
which are " 
studet : 202120473 - password : 9548911
instructor : 101120568 - password : 321654
admin  : 100 - password : 987654231

```bash
python seed_users.py
```

### 4. Start the Server
```bash
uvicorn main:app --reload
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

