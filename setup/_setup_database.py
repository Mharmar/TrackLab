import mysql.connector
from mysql.connector import Error

def create_database():
    """Creates the database and tables in MySQL (XAMPP)."""
    try:
        # 1. Connect to MySQL Server (No Database yet)
        print("🔌 Connecting to MySQL...")
        conn = mysql.connector.connect(
            host="127.0.0.1",
            port=3307,          # CHECK THIS: Use 3306 if XAMPP is default
            user="root",
            password=""
        )
        
        if conn.is_connected():
            cursor = conn.cursor()
            
            # 2. Create Database
            cursor.execute("CREATE DATABASE IF NOT EXISTS tracklab")
            print("✅ Database 'tracklab' checked/created.")
            
            # 3. Connect to the new Database
            conn.database = "tracklab"
            
            # 4. Create Tables
            tables = {
                "users": """
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        role VARCHAR(20) DEFAULT 'Student',
                        email VARCHAR(100),
                        contact VARCHAR(20),
                        department VARCHAR(100),
                        profile_image VARCHAR(255)
                    );
                """,
                "equipment": """
                    CREATE TABLE IF NOT EXISTS equipment (
                        equipment_id INT AUTO_INCREMENT PRIMARY KEY,
                        code VARCHAR(50) UNIQUE NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        category VARCHAR(50),
                        quantity INT DEFAULT 0,
                        `condition` VARCHAR(50) DEFAULT 'Good'
                    );
                """,
                "borrowers": """
                    CREATE TABLE IF NOT EXISTS borrowers (
                        borrower_id INT AUTO_INCREMENT PRIMARY KEY,
                        student_id VARCHAR(50) UNIQUE NOT NULL,
                        full_name VARCHAR(100) NOT NULL,
                        contact VARCHAR(50),
                        department VARCHAR(100)
                    );
                """,
                "borrow_transactions": """
                    CREATE TABLE IF NOT EXISTS borrow_transactions (
                        borrow_id INT AUTO_INCREMENT PRIMARY KEY,
                        equipment_id INT NOT NULL,
                        borrower_id INT NOT NULL,
                        borrow_date DATETIME,
                        expected_return_date DATETIME,
                        purpose TEXT,
                        status VARCHAR(50) DEFAULT 'Ongoing',
                        FOREIGN KEY (borrower_id) REFERENCES borrowers(borrower_id),
                        FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id)
                    );
                """,
                "return_transactions": """
                    CREATE TABLE IF NOT EXISTS return_transactions (
                        return_id INT AUTO_INCREMENT PRIMARY KEY,
                        borrow_id INT NOT NULL,
                        return_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                        `condition` VARCHAR(50),
                        remarks TEXT,
                        FOREIGN KEY (borrow_id) REFERENCES borrow_transactions(borrow_id)
                    );
                """,
                 "activity_logs": """
                    CREATE TABLE IF NOT EXISTS activity_logs (
                        log_id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT,
                        action VARCHAR(255),
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    );
                """
            }
            
            for name, query in tables.items():
                try:
                    cursor.execute(query)
                    print(f"   - Table '{name}' is ready.")
                except Error as e:
                    print(f"   ❌ Error creating table '{name}': {e}")
            
            # 5. Insert Default Admin User
            try:
                # Password is 'admin123' hashed (SHA256)
                admin_pass = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
                cursor.execute(f"INSERT IGNORE INTO users (username, password, role) VALUES ('admin', '{admin_pass}', 'Staff')")
                print("✅ Default user 'admin' (pass: admin123) ensured.")
            except Error as e:
                print(f"   ⚠️ Could not create default admin: {e}")

            conn.commit()
            print("\n🚀 Database Setup Complete! You can now run main.py.")

    except Error as e:
        print(f"❌ Critical Connection Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_database()