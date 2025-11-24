# database/mock_db.py

# A central place for our data until your group adds SQLite
INVENTORY_DB = {
    "Safety Goggles": {"id": "PPE-001", "qty": 30, "status": "Available"},
    "Lab Coats (L)": {"id": "PPE-002", "qty": 5, "status": "Out of Stock"},
    "Beaker 500ml": {"id": "GLS-104", "qty": 12, "status": "Available"},
    "Test Tubes": {"id": "GLS-105", "qty": 50, "status": "Available"},
    "Flask": {"id": "GLS-106", "qty": 2, "status": "Broken"},
    "Digital Scale": {"id": "MEA-201", "qty": 4, "status": "Available"},
    "Microscope": {"id": "APP-301", "qty": 2, "status": "Available"},
    "Extension Cord": {"id": "UTL-401", "qty": 10, "status": "Available"}
}

def get_item_details(item_name):
    # Returns the details or a default empty dict if not found
    return INVENTORY_DB.get(item_name, {"id": "UNKNOWN", "qty": 0})
