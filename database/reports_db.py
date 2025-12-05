from database.connection import create_connection

def get_borrowing_history(start_date, end_date):
    """Fetches all borrow transactions (Ongoing & Returned) within a date range."""
    conn = create_connection()
    if not conn: return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        # We append time to end_date to include the full day
        query = """
        SELECT 
            e.name AS item_name, 
            b.full_name AS borrower, 
            DATE_FORMAT(t.borrow_date, '%Y-%m-%d %h:%i %p') AS date_borrowed,
            IFNULL(DATE_FORMAT(t.expected_return_date, '%Y-%m-%d'), 'Ongoing') AS due_date,
            t.status
        FROM borrow_transactions t
        JOIN equipment e ON t.equipment_id = e.equipment_id
        JOIN borrowers b ON t.borrower_id = b.borrower_id
        WHERE t.borrow_date BETWEEN %s AND %s
        ORDER BY t.borrow_date DESC
        """
        cursor.execute(query, (start_date + " 00:00:00", end_date + " 23:59:59"))
        return cursor.fetchall()
    finally:
        if conn.is_connected(): cursor.close(); conn.close()

def get_damage_reports(start_date, end_date):
    """Fetches items returned with damage."""
    conn = create_connection()
    if not conn: return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT 
            e.name AS item_name, 
            b.full_name AS reported_by, 
            DATE_FORMAT(r.return_date, '%Y-%m-%d') AS date_returned,
            r.condition AS severity,
            r.remarks
        FROM return_transactions r
        JOIN borrow_transactions t ON r.borrow_id = t.borrow_id
        JOIN borrowers b ON t.borrower_id = b.borrower_id
        JOIN equipment e ON t.equipment_id = e.equipment_id
        WHERE r.return_date BETWEEN %s AND %s 
        AND r.condition != 'Good'
        ORDER BY r.return_date DESC
        """
        cursor.execute(query, (start_date + " 00:00:00", end_date + " 23:59:59"))
        return cursor.fetchall()
    finally:
        if conn.is_connected(): cursor.close(); conn.close()

def get_overdue_items():
    """
    Fetches ongoing borrows that are past their expected return date.
    """
    conn = create_connection()
    if not conn: return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT 
            e.name AS item_name, 
            b.full_name AS borrower, 
            DATE_FORMAT(t.borrow_date, '%Y-%m-%d') AS date_borrowed,
            IFNULL(DATE_FORMAT(t.expected_return_date, '%Y-%m-%d'), 'N/A') AS due_date,
            DATEDIFF(NOW(), t.expected_return_date) AS days_overdue
        FROM borrow_transactions t
        JOIN equipment e ON t.equipment_id = e.equipment_id
        JOIN borrowers b ON t.borrower_id = b.borrower_id
        WHERE t.status = 'Ongoing' 
        AND t.expected_return_date IS NOT NULL 
        AND t.expected_return_date < NOW()
        ORDER BY days_overdue DESC
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        if conn.is_connected(): cursor.close(); conn.close()

def get_inventory_status():
    """Fetches current stock levels."""
    conn = create_connection()
    if not conn: return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT 
            code, name, category, quantity, 
            CASE 
                WHEN quantity = 0 THEN 'Out of Stock'
                WHEN `condition` = 'Broken' THEN 'Broken'
                ELSE 'Available'
            END as status
        FROM equipment
        ORDER BY category, name
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        if conn.is_connected(): cursor.close(); conn.close()

def get_analytics_chart_data(start_date, end_date):
    """Aggregates borrow counts by day for the visual chart."""
    conn = create_connection()
    if not conn: return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT 
            DATE_FORMAT(borrow_date, '%Y-%m-%d') as day, 
            COUNT(*) as count
        FROM borrow_transactions
        WHERE borrow_date BETWEEN %s AND %s
        GROUP BY day
        ORDER BY day ASC
        """
        cursor.execute(query, (start_date + " 00:00:00", end_date + " 23:59:59"))
        return cursor.fetchall()
    finally:
        if conn.is_connected(): cursor.close(); conn.close()