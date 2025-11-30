# utils/id_generator.py

def generate_formatted_id(role, db_id):
    """
    Converts database ID (e.g., 6) into a formatted String ID (e.g., STU-00006).
    This ensures the ID is unique and permanent because it comes from the DB.
    """
    prefix = "STU" if role == "Student" else "STF"
    # zfill(5) adds zeros to the left: 6 -> 00006
    return f"{prefix}-{str(db_id).zfill(5)}"

def format_contact_number(number_str):
    """
    Formats raw numbers like 09123456789 into 0912-345-6789.
    Removes any existing dashes first to ensure clean formatting.
    """
    if not number_str:
        return ""
        
    # Remove non-digits
    clean = ''.join(filter(str.isdigit, str(number_str)))
    
    # Standard PH Mobile Format (11 digits starting with 09)
    if len(clean) == 11 and clean.startswith("09"):
        return f"{clean[:4]}-{clean[4:7]}-{clean[7:]}"
    
    return clean # Return raw if it doesn't match standard format