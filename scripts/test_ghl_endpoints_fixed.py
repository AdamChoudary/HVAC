"""
Test script to verify GHL API endpoints are working correctly.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.integrations.ghl import GHLClient
from src.utils.logging import logger


async def test_ghl_endpoints():
    """Test all GHL API endpoints"""
    ghl = GHLClient()
    
    print("=" * 60)
    print("Testing GHL API Endpoints")
    print("=" * 60)
    
    # Test 1: Get Calendars
    print("\n1. Testing get_calendars()...")
    try:
        calendars = await ghl.get_calendars()
        print(f"   ✅ Success: Found {len(calendars)} calendars")
        if calendars:
            print(f"   Sample calendar: {calendars[0].get('name', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 2: Search Contact by Phone (non-existent)
    print("\n2. Testing get_contact() with phone search (non-existent)...")
    try:
        contact = await ghl.get_contact(phone="+15551234567")
        if contact:
            print(f"   ✅ Found contact: {contact.get('id', 'N/A')}")
        else:
            print(f"   ✅ No contact found (expected for non-existent phone)")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 3: Create Test Contact
    print("\n3. Testing create_contact()...")
    try:
        test_contact = {
            "firstName": "Test",
            "lastName": "User",
            "phone": "+15551234567",
            "email": "test@example.com"
        }
        result = await ghl.create_contact(test_contact)
        contact_id = result.get("id", "")
        print(f"   ✅ Success: Created contact {contact_id}")
        
        # Test 4: Get Contact by ID
        print("\n4. Testing get_contact() by ID...")
        try:
            retrieved = await ghl.get_contact(contact_id=contact_id)
            if retrieved:
                print(f"   ✅ Success: Retrieved contact {retrieved.get('id', 'N/A')}")
                print(f"   Name: {retrieved.get('firstName', '')} {retrieved.get('lastName', '')}")
            else:
                print(f"   ❌ Contact not found")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        # Test 5: Search Contact by Phone (existing)
        print("\n5. Testing get_contact() with phone search (existing)...")
        try:
            found = await ghl.get_contact(phone="+15551234567")
            if found:
                print(f"   ✅ Success: Found contact by phone: {found.get('id', 'N/A')}")
            else:
                print(f"   ❌ Contact not found by phone")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        # Test 6: Update Contact
        print("\n6. Testing update_contact()...")
        try:
            update_data = {
                "firstName": "Updated",
                "lastName": "Test"
            }
            updated = await ghl.update_contact(contact_id, update_data)
            print(f"   ✅ Success: Updated contact {contact_id}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
    except Exception as e:
        print(f"   ❌ Error creating contact: {str(e)}")
    
    print("\n" + "=" * 60)
    print("Testing Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_ghl_endpoints())

