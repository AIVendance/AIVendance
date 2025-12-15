# src/utils/config.py
import os

# 1. DATABASE SETTINGS
DB_CONFIG = {
    "host": "127.0.0.1",
    "database": "aivendance_db",
    "user": "postgres",
    "password": "9548911", # <--- Make sure your real password is here!
    "port": 5432
}

# 2. SECURITY SETTINGS (Crucial for Login)
class SecurityConfig:
    # This key is used to sign JWT tokens.
    SECRET_KEY = "super_secret_key_change_this_in_production" 
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 Hours

# 3. EMAIL SETTINGS
class EmailConfig:
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = "your_email@gmail.com"
    SENDER_PASSWORD = "your_app_password"