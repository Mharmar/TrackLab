from database.connection import create_connection

def get_or_create_borrower(student_id_code, full_name, contact="", department=""):
    """
    Checks if a borrower exists by their Student/Staff ID (e.g., STU-00001).
    If yes, returns their DB primary key (borrower_id).
    If no, creates them and returns the new ID.
    """
    conn = create_connection()
    if not conn:
        return None
    
    borrower_pk = None
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # 1. Try to find the borrower by their Unique Code (STU-XXXXX)
        query_check = "SELECT borrower_id FROM borrowers WHERE student_id = %s"
        cursor.execute(query_check, (student_id_code,))
        result = cursor.fetchone()
        
        if result:
            borrower_pk = result['borrower_id']
            # Optional: Update contact/dept if they changed
            update_q = "UPDATE borrowers SET contact=%s, department=%s WHERE borrower_id=%s"
            cursor.execute(update_q, (contact, department, borrower_pk))
            conn.commit()
        else:
            # 2. If not found, create new borrower
            print(f"[DB] Creating new borrower: {full_name} ({student_id_code})")
            query_insert = """
            INSERT INTO borrowers (student_id, full_name, contact, department) 
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query_insert, (student_id_code, full_name, contact, department))
            conn.commit()
            borrower_pk = cursor.lastrowid
            
    except Exception as e:
        print(f"❌ Error in get_or_create_borrower: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
        
    return borrower_pk

def get_all_borrowers():
    """Retrieves all borrowers from MySQL."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM borrowers ORDER BY full_name")
            return cursor.fetchall()
        except Exception as e:
            print(f"❌ Error fetching borrowers: {e}")
            return []
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
    return []