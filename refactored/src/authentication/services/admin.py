from database.execution import fetch_one
from authentication.auth_dependence.token import verify_password, create_access_token

def authenticate_admin(username, password):
    # 1. Fetch the admin user by username
    query = "SELECT * FROM admin WHERE username = %s"
    user = fetch_one(query, (username,))
    
    # 2. Check if user exists
    if not user:
        return False
    
    # 3. Verify the password
    if not verify_password(password, user['password_hash']):
        return False
    
    # 4. Generate Access Token (JWT)
    # We store the user's ID and Role in the token
    token_data = {"sub": str(user['id']), "role": "admin"}
    access_token = create_access_token(token_data)
    
    return access_token