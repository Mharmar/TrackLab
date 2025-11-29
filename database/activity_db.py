from connection import create_connection

def log_activity(user_id, action):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        query = "INSERT INTO activity_logs (user_id, ACTION) VALUES (%s, %s)"
        cursor.execute(query, (user_id, action))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Activity logged: {action}")
