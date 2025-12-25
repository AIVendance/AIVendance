#C:\Users\user\Documents\Graduation project\AIVendance\refactored\src\admin\services.py
from uuid import uuid4
from database.execution import execute_query, fetch_one
from authentication.auth_dependence.token import get_password_hash

def create_admin_service(username, password, full_name, email):
    # 1. Check if username or email already exists
    check_query = "SELECT id FROM admin WHERE username = %s OR email = %s"
    existing_user = fetch_one(check_query, (username, email))
    
    if existing_user:
        return {"error": "Username or Email already exists"}

    # 2. Hash the password
    hashed_pwd = get_password_hash(password)
    
    # 3. Insert new admin
    insert_query = """
    INSERT INTO admin (id, username, password_hash, full_name, email)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id, username;
    """
    params = (str(uuid4()), username, hashed_pwd, full_name, email)
    
    try:
        execute_query(insert_query, params)
        return {"message": "Admin created successfully"}
    except Exception as e:
        return {"error": str(e)}

def get_admin_by_username(username: str):
    query = "SELECT * FROM admin WHERE username = %s"
    return fetch_one(query, (username,))