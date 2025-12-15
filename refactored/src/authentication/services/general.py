from database.execution import fetch_one
from authentication.auth_dependence.token import verify_password, create_access_token

def authenticate_user(identifier: str, password: str):
    """
    Authenticates a user and determines their specific role:
    - 'student'
    - 'instructor' (Admin with normal ID)
    - 'super_admin' (Admin with ID '100')
    """
    
    # 1. Check STUDENTS Table
    student_query = "SELECT id, password_hash, full_name, university_id FROM students WHERE university_id = %s"
    student = fetch_one(student_query, (identifier,))
    
    if student and verify_password(password, student['password_hash']):
        token_data = {
            "sub": str(student['id']), 
            "role": "student", 
            "name": student['full_name']
        }
        return {
            "access_token": create_access_token(token_data), 
            "token_type": "bearer", 
            "role": "student",
            "name": student['full_name'],
            "id": student['university_id']
        }
    
    # 2. Check ADMIN Table (Instructors & Super Admins)
    admin_query = "SELECT id, password_hash, full_name, username FROM admin WHERE username = %s"
    admin = fetch_one(admin_query, (identifier,))
    
    if admin and verify_password(password, admin['password_hash']):
        # Determine if Super Admin or Instructor
        real_role = "super_admin" if admin['username'] == "100" else "instructor"
        
        token_data = {
            "sub": str(admin['id']), 
            "role": "admin", # Token role remains 'admin' for backend permission checks
            "name": admin['full_name']
        }
        return {
            "access_token": create_access_token(token_data), 
            "token_type": "bearer", 
            "role": real_role, # Frontend uses this to pick the dashboard
            "name": admin['full_name'],
            "id": admin['username']
        }

    return None