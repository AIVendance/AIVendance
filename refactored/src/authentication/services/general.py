#C:\Users\user\Documents\Graduation project\AIVendance\refactored\src\authentication\services\general.py
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
            # Determine role logic
            # If the user selected 'instructor', we trust that flow if checking the same table.
            # But we should ensure super admins (100) are always 'admin'.
            
            db_role = "admin" # Default token role
            frontend_role = "instructor" # Default frontend redirect
            
            if admin['username'] in ("1", "100", "admin"):
                frontend_role = "admin"
            
            # If the user explicitly requested 'admin' but isn't a super admin, we might want to restrict it?
            # For now, let's respect the requested role if valid, or default to what the user essentially is.
            
            if role == "admin" and frontend_role == "admin":
                final_role = "admin"
            else:
                final_role = "instructor"

            # IMPORTANT: The token role determines permissions. 
            # Instructors need to be able to access endpoints guarded by `get_current_user` which usually checks for "admin" or "student".
            # If your routers require role="admin" for instructors, keep db_role="admin".
            
            token_data = {
                "sub": str(admin['id']), 
                "role": db_role, 
                "name": admin['full_name']
            }
            return {
                "access_token": create_access_token(token_data), 
                "token_type": "bearer", 
                "role": final_role, # Frontend uses this to redirect: /dashboard/instructor vs /dashboard/admin
                "name": admin['full_name'],
                "id": admin['username']
            }

    return None