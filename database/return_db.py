from database.connection import create_connection

def return_equipment(borrow_id, condition, remarks):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # 1. Insert into return_transactions
            query = "INSERT INTO return_transactions (borrow_id, `condition`, remarks) VALUES (%s, %s, %s)"
            cursor.execute(query, (borrow_id, condition, remarks))
            
            # 2. Update borrow_transactions status
            cursor.execute("UPDATE borrow_transactions SET status='Returned' WHERE borrow_id=%s", (borrow_id,))
            
            # 3. Restore Quantity if Good
            if condition == "Good":
                cursor.execute("SELECT equipment_id FROM borrow_transactions WHERE borrow_id=%s", (borrow_id,))
                result = cursor.fetchone()
                if result:
                    eq_id = result[0]
                    cursor.execute("UPDATE equipment SET quantity = quantity + 1 WHERE equipment_id=%s", (eq_id,))

            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Return Error: {e}")
            return False
        finally:
            if conn.is_connected(): cursor.close(); conn.close()
    return False

def get_return_history():
    """Fetches history with separated Date and Time."""
    conn = create_connection()
    if conn:
        try:
            # DATE_FORMAT splits the timestamp
            query = """
            SELECT 
                r.return_id, 
                e.name AS item_name, 
                e.code AS item_code,
                b.full_name AS returned_by, 
                DATE_FORMAT(r.return_date, '%Y-%m-%d') AS ret_date,
                DATE_FORMAT(r.return_date, '%h:%i %p') AS ret_time,
                r.`condition`, 
                r.remarks
            FROM return_transactions r
            JOIN borrow_transactions t ON r.borrow_id = t.borrow_id
            JOIN equipment e ON t.equipment_id = e.equipment_id
            JOIN borrowers b ON t.borrower_id = b.borrower_id
            ORDER BY r.return_date DESC
            """
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"❌ History Error: {e}")
            return []
        finally:
            if conn.is_connected(): cursor.close(); conn.close()
    return []