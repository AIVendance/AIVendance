# Quick Start Guide

## Step 1: Create Database Tables
```bash
python create_tables.py
```

## Step 2: Create Admin Account (Username: 1, Password: 1)
**Option A - Using Python:**
```bash
python create_admin_1.py
```

**Option B - Using Batch File (Windows):**
Double-click `setup_admin.bat`

## Step 3: Start the Server
```bash
python main.py
```

## Step 4: Login
1. Go to `http://127.0.0.1:8000`
2. Select "Admin" role
3. Enter:
   - **Username**: `1`
   - **Password**: `1`
4. Click "Sign In"

## Troubleshooting Login Issues

If login fails with "1/1":
1. Make sure you ran `create_admin_1.py` successfully
2. Check database connection in `src/database/connection.py`
3. Verify the admin table has a row with `username = '1'`
4. Check server console for error messages

## Testing the System
- Admin Dashboard: `http://127.0.0.1:8000/dashboard/admin`
- Test Page: `http://127.0.0.1:8000/test` (login with 1/1)

