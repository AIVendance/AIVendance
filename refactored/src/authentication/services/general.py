from database.execution import fetch_one
from authentication.auth_dependence.token import verify_password, create_access_token

def authenticate_user(identifier: str, password: str, role: str = None):
    """
    Authenticates a user based on the selected role:
    - 'student': Checks students table
    - 'instructor' or 'admin': Checks admin table
    """
    
    # 1. Check STUDENTS Table if role is student or unspecified
    if role == "student" or role is None:
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
        # If role was explicitly student, don't check admin
        if role == "student":
            return None
    
    # 2. Check ADMIN Table (Instructors & Super Admins) if role is admin/instructor or unspecified
    if role in ["admin", "instructor"] or role is None:
        admin_query = "SELECT id, password_hash, full_name, username FROM admin WHERE username = %s"
        admin = fetch_one(admin_query, (identifier,))
        
        if admin and verify_password(password, admin['password_hash']):
            # Determine if Super Admin or Instructor
            # Username "1" or "100" are super_admin, others are instructors
            real_role = "super_admin" if admin['username'] in ("1", "100") else "instructor"
            
            # Allow login if roles match essentially (Admin vs Instructor distinction is loose here for now)
            # Both serve as 'admin' role token for now
            
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