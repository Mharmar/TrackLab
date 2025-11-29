# database/connection.py
import mysql.connector
from mysql.connector import Error

def create_connection():
    """
    Connects to XAMPP using 'use_pure=True' to prevent Driver Crashes.
    """
    try:
        print("[DB] Connecting (Pure Python Mode)...")
        connection = mysql.connector.connect(
            host="127.0.0.1",    # Force IPv4
            port=3307,           # Your XAMPP Port
            user="root",
            password="",
            database="tracklab",
            use_pure=True,       # <--- CRITICAL FIX: Prevents the crash
            connection_timeout=5
        )
        
        if connection.is_connected():
            print(f"✅ Connected to MySQL!")
            return connection
            
    except Error as e:
        print(f"❌ Connection Error: {e}")
        return None