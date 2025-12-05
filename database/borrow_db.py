# database/borrow_db.py
from database.connection import create_connection

def borrow_equipment(equipment_id, borrower_id, borrow_date, expected_return, purpose):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
            INSERT INTO borrow_transactions 
            (equipment_id, borrower_id, borrow_date, expected_return_date, purpose, status)
            VALUES (%s, %s, %s, %s, %s, 'Ongoing')
            """
            cursor.execute(query, (equipment_id, borrower_id, borrow_date, expected_return, purpose))
            
            # Decrease quantity
            cursor.execute("UPDATE equipment SET quantity = quantity - 1 WHERE equipment_id = %s", (equipment_id,))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error borrowing: {e}")
            return False
        finally:
            if conn.is_connected(): cursor.close(); conn.close()
    return False

def delete_borrow_transaction(borrow_id):
    """
    ADMIN FUNCTION: Deletes a borrow record and restores the quantity.
    Returns the equipment_id and quantity to restore.
    """
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # 1. Get the equipment ID (This is safe because we only delete ONGOING items)
            cursor.execute("SELECT equipment_id FROM borrow_transactions WHERE borrow_id = %s AND status = 'Ongoing'", (borrow_id,))
            result = cursor.fetchone()
            
            if not result:
                print(f"Borrow ID {borrow_id} not found or already returned.")
                return False
            
            equipment_id = result[0]

            # 2. Delete the transaction
            cursor.execute("DELETE FROM borrow_transactions WHERE borrow_id = %s", (borrow_id,))
            
            # 3. Restore quantity (always restore 1 since borrowing is 1-at-a-time logic)
            cursor.execute("UPDATE equipment SET quantity = quantity + 1 WHERE equipment_id = %s", (equipment_id,))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error deleting borrow transaction: {e}")
            return False
        finally:
            if conn.is_connected(): cursor.close(); conn.close()
    return False

def get_active_borrows(student_id_filter=None):
    """
    Fetches active borrows with Profile Images.
    """
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            query = """
            SELECT 
                t.borrow_id, 
                b.full_name, 
                b.student_id, 
                b.department, 
                e.name as item_name, 
                DATE_FORMAT(t.borrow_date, '%h:%i %p') as borrow_time,
                DATE_FORMAT(t.expected_return_date, '%b %d %h:%i %p') as due_time,
                CASE 
                    WHEN t.expected_return_date IS NOT NULL AND NOW() > t.expected_return_date THEN 'Overdue'
                    ELSE t.status 
                END as status,
                u.profile_image
            FROM borrow_transactions t
            JOIN borrowers b ON t.borrower_id = b.borrower_id
            JOIN equipment e ON t.equipment_id = e.equipment_id
            LEFT JOIN users u ON b.student_id = CONCAT(CASE WHEN u.role = 'Student' THEN 'STU-' ELSE 'STF-' END, LPAD(u.user_id, 5, '0'))
            WHERE t.status = 'Ongoing'
            """
            
            params = []
            if student_id_filter:
                query += " AND b.student_id = %s"
                params.append(student_id_filter)
            
            query += " ORDER BY t.borrow_date DESC"
            
            cursor.execute(query, tuple(params))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching active borrows: {e}")
            return []
        finally:
            if conn.is_connected(): cursor.close(); conn.close()
    return []