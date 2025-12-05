# database/users_db.py
from database.connection import create_connection
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_user_exists(username):
    conn = create_connection()
    cursor = None
    try:
        if conn and conn.is_connected():
            cursor = conn.cursor()
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
    if check_user_exists(username):
        return False, "Username already taken."

    conn = create_connection()
    cursor = None
    try:
        if conn and conn.is_connected():
            cursor = conn.cursor()
            query = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)"
            hashed_pw = hash_password(password)
            cursor.execute(query, (username, hashed_pw, role))
            conn.commit()
            return True, "User registered successfully."
        else:
            return False, "Could not connect to database."
    except Exception as e:
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
            
            # Ensure keys exist
            if user:
                for key in ['email', 'contact', 'department', 'profile_image']:
                    if user.get(key) is None: user[key] = ""
            return user
    except Exception as e:
        print(f"❌ Login Error: {e}")
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()
    return None

def update_user_profile(user_id, email, contact, department):
    conn = create_connection()
    cursor = None
    try:
        if conn and conn.is_connected():
            cursor = conn.cursor()
            query = "UPDATE users SET email=%s, contact=%s, department=%s WHERE user_id=%s"
            cursor.execute(query, (email, contact, department, user_id))
            conn.commit()
            return True
    except Exception as e:
        print(f"❌ Update Profile Error: {e}")
        return False
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()
    return False

# --- NEW FUNCTION FOR IMAGE ---
def update_profile_image(user_id, image_path):
    conn = create_connection()
    cursor = None
    try:
        if conn and conn.is_connected():
            cursor = conn.cursor()
            query = "UPDATE users SET profile_image=%s WHERE user_id=%s"
            cursor.execute(query, (image_path, user_id))
            conn.commit()
            return True
    except Exception as e:
        print(f"❌ Update Image Error: {e}")
        return False
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()
    return False