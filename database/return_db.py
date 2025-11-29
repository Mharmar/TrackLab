from connection import create_connection

def return_equipment(borrow_id, return_date, condition, damage_notes=None, damage_image=None):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        query = """
        INSERT INTO return_transactions 
        (borrow_id, return_date, CONDITION, damage_notes, damage_image)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (borrow_id, return_date, condition, damage_notes, damage_image))
        cursor.execute("UPDATE borrow_transactions SET STATUS='Returned' WHERE borrow_id=%s", (borrow_id,))
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Return transaction completed.")
