from database.connection import create_connection

def borrow_equipment(equipment_id, borrower_id, borrow_date, expected_return, purpose):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        query = """
        INSERT INTO borrow_transactions 
        (equipment_id, borrower_id, borrow_date, expected_return_date, purpose, status)
        VALUES (%s, %s, %s, %s, %s, 'Ongoing')
        """
        cursor.execute(query, (equipment_id, borrower_id, borrow_date, expected_return, purpose))
        conn.commit()
        cursor.close()
        conn.close()
        return True

# --- NEW FUNCTION FOR DASHBOARD ---
def get_active_borrows():
    conn = create_connection()
    if conn:
        # Joins tables to get names instead of just IDs
        query = """
        SELECT t.borrow_id, b.full_name, e.name as item_name, t.status 
        FROM borrow_transactions t
        JOIN borrowers b ON t.borrower_id = b.borrower_id
        JOIN equipment e ON t.equipment_id = e.equipment_id
        WHERE t.status = 'Ongoing'
        """
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    return []