
import sys
import os

# Add refactored/src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.execution import fetch_all
from authentication.auth_dependence.token import verify_password, get_password_hash

def debug_login():
    print("--- DEBUGGING LOGIN CREDENTIALS ---")
    
    # 1. Check Instructor/Admin in ADMIN table
    usernames = ['101120568', '100']
    
    for username in usernames:
        print(f"\nChecking Admin table for username: {username}")
        users = fetch_all(f"SELECT * FROM admin WHERE username = '{username}'")
        
        if not users:
            print(f"❌ User '{username}' NOT FOUND in 'admin' table.")
        else:
            for user in users:
                print(f"✅ User found: ID={user['id']}, Role={user.get('role', 'N/A')}, Dept={user.get('department')}")
                stored_hash = user['password_hash']
                
                # Test Password
                password_to_test = "321654" if username == '101120568' else "987654231"
                is_valid = verify_password(password_to_test, stored_hash)
                
                print(f"   Testing password '{password_to_test}': {'✅ MATCH' if is_valid else '❌ MISMATCH'}")
                if not is_valid:
                     print(f"   Stored Hash: {stored_hash[:20]}...")
                     # Print what the hash SHOULD be
                     correct_hash = get_password_hash(password_to_test)
                     print(f"   Expected Hash for '{password_to_test}': {correct_hash[:20]}...")

    # 2. Check DB content generally
    print("\n--- ALL ADMIN USERS ---")
    all_admins = fetch_all("SELECT username, full_name, department FROM admin")
    for a in all_admins:
        print(f"User: {a['username']} ({a['full_name']}) - {a.get('department')}")

if __name__ == "__main__":
    debug_login()
