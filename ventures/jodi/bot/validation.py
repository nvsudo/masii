"""
Input Validation for JODI Onboarding
Validates user text inputs before saving
"""

from datetime import datetime
from typing import Tuple, Any


def validate_input(value: str, validation_type: str, rules: dict) -> Tuple[bool, str, Any]:
    """
    Validate user input based on validation type.
    
    Returns:
        (is_valid: bool, error_message: str, processed_value: Any)
    """
    
    if validation_type == "date_of_birth":
        return validate_date_of_birth(value, rules[validation_type])
    
    elif validation_type == "height_cm":
        return validate_height(value, rules[validation_type])
    
    elif validation_type == "email":
        return validate_email(value)
    
    elif validation_type == "phone":
        return validate_phone(value)
    
    # Default: accept as-is
    return True, "", value


def validate_date_of_birth(value: str, rule: dict) -> Tuple[bool, str, Any]:
    """
    Validate date of birth in DD/MM/YYYY format.
    Returns (is_valid, error_msg, iso_date_string)
    """
    try:
        # Parse date
        dob = datetime.strptime(value.strip(), "%d/%m/%Y")
        
        # Calculate age
        today = datetime.now()
        age = (today - dob).days // 365
        
        # Check age range
        min_age = rule['min_age']
        max_age = rule['max_age']
        
        if age < min_age or age > max_age:
            return False, rule['error_range'], None
        
        # Return ISO format date
        return True, "", dob.date().isoformat()
    
    except ValueError:
        return False, rule['error_format'], None


def validate_height(value: str, rule: dict) -> Tuple[bool, str, Any]:
    """
    Validate height in cm.
    Accepts: "170", "170cm", "5'8", "5'8\""
    Returns height in cm as integer.
    """
    try:
        # Clean input
        value = value.strip().lower().replace('cm', '').replace('"', '').strip()
        
        # Check if feet'inches format
        if "'" in value:
            parts = value.split("'")
            feet = int(parts[0])
            inches = int(parts[1]) if len(parts) > 1 and parts[1] else 0
            height_cm = int((feet * 12 + inches) * 2.54)
        else:
            # Direct cm value
            height_cm = int(value)
        
        # Validate range
        if height_cm < rule['min'] or height_cm > rule['max']:
            return False, rule['error'], None
        
        return True, "", height_cm
    
    except (ValueError, IndexError):
        return False, "Invalid height format. Use cm (e.g., 170) or feet'inches (e.g., 5'8)", None


def validate_email(value: str) -> Tuple[bool, str, Any]:
    """Basic email validation"""
    value = value.strip()
    
    if '@' not in value or '.' not in value:
        return False, "Please enter a valid email address.", None
    
    return True, "", value


def validate_phone(value: str) -> Tuple[bool, str, Any]:
    """Basic phone validation"""
    # Remove common separators
    cleaned = value.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # Check if starts with + (international format)
    if cleaned.startswith('+'):
        cleaned = cleaned[1:]
    
    # Check if all digits
    if not cleaned.isdigit():
        return False, "Please enter a valid phone number.", None
    
    # Check length (between 7 and 15 digits is reasonable)
    if len(cleaned) < 7 or len(cleaned) > 15:
        return False, "Phone number must be between 7 and 15 digits.", None
    
    return True, "", value  # Return original format


def sanitize_text(value: str, max_length: int = 500) -> str:
    """Sanitize free-form text input"""
    # Strip whitespace
    cleaned = value.strip()
    
    # Truncate if too long
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    
    # Remove potentially problematic characters (basic sanitization)
    # Allow unicode for international names, but remove control characters
    cleaned = ''.join(char for char in cleaned if ord(char) >= 32 or char in '\n\r\t')
    
    return cleaned


def calculate_age(dob_iso: str) -> int:
    """Calculate age from ISO date string"""
    dob = datetime.fromisoformat(dob_iso)
    today = datetime.now()
    return (today - dob).days // 365
