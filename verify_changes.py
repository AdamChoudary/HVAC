import asyncio
import sys
import os
from datetime import datetime, time

# Add src to path
sys.path.append(os.getcwd())

from src.utils.service_area import is_in_service_area
from src.utils.business_hours import check_business_hours, OfficeHours
from src.config.business_data import STAFF_DIRECTORY

def test_service_area():
    print("\n--- Testing Service Area ---")
    
    test_cases = [
        ("97301", True),   # Salem (Primary)
        ("97201", True),   # Portland (Extended)
        ("90210", False),  # Beverly Hills (Invalid)
        ("10001", False),  # NY (Invalid)
    ]
    
    for zip_code, expected in test_cases:
        result, msg = is_in_service_area(zip_code=zip_code)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"{status} Zip {zip_code}: {result} ({msg})")

def test_business_hours():
    print("\n--- Testing Business Hours ---")
    
    # Mock times for testing
    # Monday at 5:00 PM (17:00) - Closed for Field, Open for Office
    monday_5pm = datetime(2025, 11, 24, 17, 0, 0) # Nov 24 2025 is a Monday
    
    # Test Field Hours (Should be closed)
    field_status = check_business_hours(reference_time=monday_5pm, schedule_type="field")
    print(f"Field Hours at 5PM: {field_status['isBusinessHours']} (Expected: False)")
    
    # Test Office Hours (Should be open)
    office_status = check_business_hours(reference_time=monday_5pm, schedule_type="office")
    print(f"Office Hours at 5PM: {office_status['isBusinessHours']} (Expected: True)")

def test_staff_directory():
    print("\n--- Testing Staff Directory ---")
    
    scott = STAFF_DIRECTORY.get("scott")
    if scott and scott["phone"] == "+15034772696":
        print("✅ PASS: Scott found with correct phone")
    else:
        print("❌ FAIL: Scott not found or wrong phone")

if __name__ == "__main__":
    test_service_area()
    test_business_hours()
    test_staff_directory()
