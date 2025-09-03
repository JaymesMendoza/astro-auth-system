import re
from typing import Optional
from fastapi import HTTPException, status


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength.
    Returns (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 100:
        return False, "Password must be less than 100 characters"
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for at least one digit
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, None


def validate_username(username: str) -> tuple[bool, Optional[str]]:
    """
    Validate username format.
    Returns (is_valid, error_message)
    """
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 100:
        return False, "Username must be less than 100 characters"
    
    # Only alphanumeric characters and underscores
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    # Cannot start with a number
    if username[0].isdigit():
        return False, "Username cannot start with a number"
    
    return True, None


def validate_name(name: str, field_name: str) -> tuple[bool, Optional[str]]:
    """
    Validate first/last name.
    Returns (is_valid, error_message)
    """
    if not name:
        return True, None  # Names are optional
    
    if len(name) > 100:
        return False, f"{field_name} must be less than 100 characters"
    
    # Only letters, spaces, hyphens, and apostrophes
    if not re.match(r"^[a-zA-Z\s\-']+$", name):
        return False, f"{field_name} can only contain letters, spaces, hyphens, and apostrophes"
    
    return True, None


def sanitize_input(text: str) -> str:
    """Sanitize text input to prevent XSS."""
    if not text:
        return text
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', '\0']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text.strip()


def validate_file_type(filename: str, allowed_types: list) -> bool:
    """Validate file type by extension."""
    if not filename:
        return False
    
    file_extension = filename.lower().split('.')[-1]
    return file_extension in allowed_types


def validate_image_file(filename: str) -> bool:
    """Validate image file type."""
    allowed_types = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    return validate_file_type(filename, allowed_types)