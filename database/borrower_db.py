from database.connection import create_connection

def add_borrower(full_name, department, role):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        # Check if exists first (simple check)
        cursor.execute("SELECT borrower_id FROM borrowers WHERE full_name=%s", (full_name,))
        result = cursor.fetchone()
        
        if result:
            return result[0] # Return existing ID
            
        query = "INSERT INTO borrowers (full_name, department, role) VALUES (%s, %s, %s)"
        cursor.execute(query, (full_name, department, role))
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return new_id