from database.connection import create_connection

def add_equipment(name, code, category, description, quantity, condition):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        query = "INSERT INTO equipment (name, code, category, description, quantity, `condition`) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (name, code, category, description, quantity, condition))
        conn.commit()
        cursor.close()
        conn.close()
        return True

def get_all_equipment():
    conn = create_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM equipment")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    return []