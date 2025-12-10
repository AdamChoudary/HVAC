"""
Service Area Validation Utility.
Checks if a given zip code or city is within the Scott Valley HVAC service area.
"""
from typing import Optional, Tuple
from src.config.business_data import SERVICE_AREA_CONFIG

def is_in_service_area(zip_code: Optional[str] = None, city: Optional[str] = None) -> Tuple[bool, str]:
    """
    Check if a location is in the service area.
    
    Args:
        zip_code: The 5-digit zip code string.
        city: The city name.
        
    Returns:
        Tuple[bool, str]: (is_valid, reason)
    """
    # Normalize inputs
    if zip_code:
        zip_code = str(zip_code).strip()[:5]
    
    if city:
        city = str(city).strip().title()
        
    # Check Zip Code (Primary Method)
    if zip_code:
        if zip_code in SERVICE_AREA_CONFIG["primary_zip_codes"]:
            return True, f"Zip code {zip_code} is in our primary service area."
            
    # Check City (Secondary Method)
    if city:
        # Check for exact match or partial match in extended cities
        for served_city in SERVICE_AREA_CONFIG["extended_cities"]:
            if served_city.lower() in city.lower() or city.lower() in served_city.lower():
                return True, f"City {city} is in our service area."
                
    # If we have a zip code but it wasn't in the list
    if zip_code:
        return False, f"Zip code {zip_code} appears to be outside our standard service area."
        
    # If we only had city and it failed
    if city:
        return False, f"City {city} appears to be outside our standard service area."
        
    # No location provided
    return False, "No location information provided to validate."
