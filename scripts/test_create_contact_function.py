"""
Test script to verify create_contact function handles duplicates correctly.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.functions.create_contact import create_contact
from src.models import CreateContactRequest
from src.utils.logging import logger


async def test_create_contact_function():
    """Test create_contact function with duplicate handling"""
    print("=" * 60)
    print("Testing create_contact() Function")
    print("=" * 60)
    
    # Test 1: Create new contact
    print("\n1. Testing create_contact() with new contact...")
    try:
        request = CreateContactRequest(
            name="Test User",
            phone="+15559998888",
            email="newtest@example.com",
            address="123 Test St",
            zip_code="12345"
        )
        response = await create_contact(request)
        print(f"   ✅ Success: Contact ID: {response.contact_id}, Is New: {response.is_new}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        logger.exception("Error creating contact")
    
    # Test 2: Try to create duplicate using the same email (should update existing)
    print("\n2. Testing create_contact() with duplicate email (should update)...")
    try:
        request = CreateContactRequest(
            name="Updated Test User",
            phone="+15559998888",  # Same phone
            email="newtest@example.com",  # Same email - will trigger duplicate
            address="456 Updated St",
            zip_code="54321"
        )
        response = await create_contact(request)
        print(f"   ✅ Success: Contact ID: {response.contact_id}, Is New: {response.is_new}")
        if not response.is_new:
            print(f"   ✅ Correctly detected and updated duplicate contact")
        else:
            print(f"   ⚠️ Warning: Expected is_new=False but got True")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        logger.exception("Error handling duplicate contact")
    
    # Test 3: Create another new contact
    print("\n3. Testing create_contact() with another new contact...")
    try:
        request = CreateContactRequest(
            name="Another Test",
            phone="+15557776666",
            email="another@example.com"
        )
        response = await create_contact(request)
        print(f"   ✅ Success: Contact ID: {response.contact_id}, Is New: {response.is_new}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        logger.exception("Error creating second contact")
    
    print("\n" + "=" * 60)
    print("Testing Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_create_contact_function())

