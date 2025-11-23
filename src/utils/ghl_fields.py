"""
Utility functions for GHL custom field key normalization.
GHL auto-generates field keys as "contact.{key}" format.
"""
from typing import Dict, Any, List


def normalize_ghl_field_key(key: str) -> str:
    """
    Normalize custom field key to GHL format.
    GHL generates keys as "contact.{key}" for contact custom fields.
    
    Args:
        key: Field key (with or without "contact." prefix)
    
    Returns:
        Normalized field key in "contact.{key}" format
    """
    if key.startswith("contact."):
        return key
    return f"contact.{key}"


def build_custom_fields_array(fields: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Build GHL custom fields array format from dictionary.
    
    Args:
        fields: Dictionary of field keys and values
    
    Returns:
        Array of custom field objects in GHL format
    """
    custom_fields_array = []
    for key, value in fields.items():
        normalized_key = normalize_ghl_field_key(key)
        custom_fields_array.append({
            "key": normalized_key,
            "field_value": str(value) if value is not None else ""
        })
    return custom_fields_array

