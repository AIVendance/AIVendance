#C:\Users\user\Documents\Graduation project\AIVendance\refactored\src\authentication\auth_dependence\token.py
from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import jwt, JWTError
import bcrypt
import sys
import os

# Add parent directory to path to find utils
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from utils.config import SecurityConfig

# 1. PASSWORD HASHING SETUP
# Removed CryptContext due to compatibility issues with bcrypt 4.0+

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks if the typed password matches the stored hash."""
    # Ensure bytes
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

def get_password_hash(password: str) -> str:
    """Converts a plain password into a secure hash."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# 2. TOKEN GENERATION (JWT)
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT token containing user data (sub) and expiration time.
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=SecurityConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Sign the token using the secret key from config.py
    encoded_jwt = jwt.encode(to_encode, SecurityConfig.SECRET_KEY, algorithm=SecurityConfig.ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """
    Decodes and validates a token. Returns the payload (data) if valid.
    """
    try:
        payload = jwt.decode(token, SecurityConfig.SECRET_KEY, algorithms=[SecurityConfig.ALGORITHM])
        return payload
    except JWTError:
        return None