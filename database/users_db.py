# database/users_db.py
from database.connection import create_connection
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_user_exists(username):
    """Returns True if username already exists."""
    conn = create_connection()
    cursor = None
    try:
        if conn and conn.is_connected():
            cursor = conn.cursor()
            # Match your SQL column name (user_id)
            query = "SELECT user_id FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            return result is not None
    except Exception as e:
        print(f"❌ Check User Error: {e}")
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()
    return False

def register_user(username, password, role):
    """Registers a new user. Returns (Success: bool, Message: str)"""
    print(f"[DB] Checking if {username} exists...")
    
    # 1. Check duplicates
    if check_user_exists(username):
        return False, "Username already taken."

    # 2. Register
    conn = create_connection()
    cursor = None
    try:
        if conn and conn.is_connected():
            print("[DB] Inserting new user...")
            cursor = conn.cursor()
            query = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)"
            hashed_pw = hash_password(password)
            cursor.execute(query, (username, hashed_pw, role))
            conn.commit()
            print(f"✅ Registered: {username}")
            return True, "User registered successfully."
        else:
            return False, "Could not connect to database."
            
    except Exception as e:
        print(f"❌ Register Error: {e}")
        return False, f"Database Error: {e}"
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

def login_user(username, password):
    conn = create_connection()
    cursor = None
    try:
        if conn and conn.is_connected():
            cursor = conn.cursor(dictionary=True)
            hashed_pw = hash_password(password)
            query = "SELECT * FROM users WHERE username=%s AND password=%s"
            cursor.execute(query, (username, hashed_pw))
            user = cursor.fetchone()
            return user
    except Exception as e:
        print(f"❌ Login Error: {e}")
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()
    return None