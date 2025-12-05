from database.connection import create_connection

def add_equipment(name, code, category, quantity, condition):
    """Adds new equipment (No description)."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Using backticks for condition as it is a keyword
            query = "INSERT INTO equipment (name, code, category, quantity, `condition`) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (name, code, category, quantity, condition))
            conn.commit()
            print(f"✅ Added Equipment: {name}")
            return True
        except Exception as e:
            print(f"❌ Add Equipment Error: {e}")
            return False
        finally:
            if conn.is_connected(): cursor.close(); conn.close()
    return False

def get_all_equipment():
    """Fetches all equipment ordered by Code (EQ-XXXXX)."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM equipment ORDER BY code ASC")
            return cursor.fetchall()
        except Exception as e:
            print(f"❌ Fetch Equipment Error: {e}")
            return []
        finally:
            if conn.is_connected(): cursor.close(); conn.close()
    return []

def update_equipment(eq_id, category, quantity, condition):
    """Updates ONLY category, quantity, and condition. Name/ID are locked."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "UPDATE equipment SET category=%s, quantity=%s, `condition`=%s WHERE equipment_id=%s"
            cursor.execute(query, (category, quantity, condition, eq_id))
            conn.commit()
            print(f"✅ Updated Equipment ID: {eq_id}")
            return True
        except Exception as e:
            print(f"❌ Update Equipment Error: {e}")
            return False
        finally:
            if conn.is_connected(): cursor.close(); conn.close()
    return False

def delete_equipment(eq_id):
    """Deletes an equipment item."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM equipment WHERE equipment_id=%s", (eq_id,))
            conn.commit()
            print(f"✅ Deleted Equipment ID: {eq_id}")
            return True
        except Exception as e:
            print(f"❌ Delete Equipment Error: {e}")
            return False
        finally:
            if conn.is_connected(): cursor.close(); conn.close()
    return False