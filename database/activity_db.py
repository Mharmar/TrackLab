from database.connection import create_connection

def log_activity(user_id, action):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "INSERT INTO activity_logs (user_id, ACTION) VALUES (%s, %s)"
            cursor.execute(query, (user_id, action))
            conn.commit()
            print(f"✅ Activity logged: {action}")
        except Exception as e:
            print(f"❌ Log Activity Error: {e}")
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()