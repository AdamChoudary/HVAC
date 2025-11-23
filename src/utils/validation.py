import re
from typing import Optional
from src.utils.errors import APIError


def validate_phone_number(phone: str) -> str:
    """Validate and normalize phone number to E.164 format"""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Check if it's a valid length
    if len(digits) == 10:
        # US number without country code
        return f"+1{digits}"
    elif len(digits) == 11 and digits[0] == '1':
        # US number with country code
        return f"+{digits}"
    elif len(digits) > 11:
        # International number
        return f"+{digits}"
    else:
        raise APIError(
            f"Invalid phone number format: {phone}",
            status_code=400
        )


def validate_email(email: Optional[str]) -> Optional[str]:
    """Validate email format"""
    if not email:
        return None
    
    # Strip whitespace
    email = email.strip()
    
    # Return None for empty string after stripping
    if not email:
        return None
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise APIError(
            f"Invalid email format: {email}",
            status_code=400
        )
    
    return email.lower()


def validate_zip_code(zip_code: Optional[str]) -> Optional[str]:
    """Validate US ZIP code format"""
    if not zip_code:
        return None
    
    # US ZIP code: 5 digits or 5+4 format
    pattern = r'^\d{5}(-\d{4})?$'
    if not re.match(pattern, zip_code):
        raise APIError(
            f"Invalid ZIP code format: {zip_code}",
            status_code=400
        )
    
    return zip_code

