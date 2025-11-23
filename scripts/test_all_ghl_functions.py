"""
Comprehensive test script for all GHL-related functions.
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.functions.create_contact import create_contact
from src.functions.check_calendar_availability import check_calendar_availability
from src.functions.book_appointment import book_appointment
from src.models import (
    CreateContactRequest,
    CheckCalendarAvailabilityRequest,
    BookAppointmentRequest,
    ServiceType
)
from src.integrations.ghl import GHLClient
from src.utils.logging import logger


async def test_all_functions():
    """Test all GHL-related functions"""
    print("=" * 70)
    print("Testing All GHL Functions")
    print("=" * 70)
    
    ghl = GHLClient()
    contact_id = None
    
    # Test 1: Create Contact
    print("\n1️⃣  Testing create_contact()...")
    try:
        request = CreateContactRequest(
            name="John Test Customer",
            phone="+15551112222",
            email="johntest@example.com",
            address="123 Main St",
            zip_code="95066"
        )
        response = await create_contact(request)
        contact_id = response.contact_id
        print(f"   ✅ Success: Contact ID: {contact_id}, Is New: {response.is_new}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        logger.exception("Error in create_contact")
        return
    
    if not contact_id:
        print("   ❌ No contact ID, cannot continue tests")
        return
    
    # Test 2: Get Calendars
    print("\n2️⃣  Testing get_calendars()...")
    try:
        calendars = await ghl.get_calendars()
        print(f"   ✅ Success: Found {len(calendars)} calendars")
        if calendars:
            print(f"   Sample calendars:")
            for cal in calendars[:3]:
                print(f"      - {cal.get('name', 'N/A')} (ID: {cal.get('id', 'N/A')[:20]}...)")
            calendar_id = calendars[0].get("id")
        else:
            print("   ⚠️  No calendars found")
            calendar_id = None
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        calendar_id = None
    
    # Test 3: Check Calendar Availability
    if calendar_id:
        print("\n3️⃣  Testing check_calendar_availability()...")
        try:
            # Get dates for next week
            start_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            end_date = (datetime.now() + timedelta(days=8)).strftime("%Y-%m-%d")
            
            request = CheckCalendarAvailabilityRequest(
                calendar_id=calendar_id,
                service_type=ServiceType.REPAIR,
                start_date=start_date,
                end_date=end_date
            )
            response = await check_calendar_availability(request)
            print(f"   ✅ Success: Found {len(response.slots)} available slots")
            if response.slots:
                print(f"   Sample slots:")
                for slot in response.slots[:3]:
                    if slot.available:
                        print(f"      - {slot.start_time} to {slot.end_time} (Available)")
            else:
                print("   ⚠️  No available slots found")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            logger.exception("Error in check_calendar_availability")
    else:
        print("\n3️⃣  Skipping check_calendar_availability() - no calendar ID")
    
    # Test 4: Book Appointment (if we have calendar and contact)
    if calendar_id and contact_id:
        print("\n4️⃣  Testing book_appointment()...")
        try:
            # Book appointment for tomorrow at 10 AM
            tomorrow = datetime.now() + timedelta(days=1)
            start_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0).isoformat()
            end_time = tomorrow.replace(hour=11, minute=0, second=0, microsecond=0).isoformat()
            
            request = BookAppointmentRequest(
                calendar_id=calendar_id,
                contact_id=contact_id,
                start_time=start_time,
                end_time=end_time,
                title="Test Appointment - HVAC Service",
                service_type=ServiceType.REPAIR,
                notes="Test appointment created by automated test"
            )
            response = await book_appointment(request)
            if response.success:
                print(f"   ✅ Success: Appointment ID: {response.appointment_id}")
                print(f"   Message: {response.message}")
            else:
                print(f"   ❌ Failed: {response.message}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            logger.exception("Error in book_appointment")
    else:
        print("\n4️⃣  Skipping book_appointment() - missing calendar or contact ID")
    
    # Test 5: Add Timeline Note
    print("\n5️⃣  Testing add_timeline_note()...")
    try:
        note_result = await ghl.add_timeline_note(
            contact_id=contact_id,
            note="Test note added by automated test script"
        )
        note_id = note_result.get("id", "")
        if note_id:
            print(f"   ✅ Success: Note ID: {note_id}")
        else:
            print(f"   ⚠️  Note created but no ID returned: {note_result}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        logger.exception("Error in add_timeline_note")
    
    # Test 6: Update Custom Fields
    print("\n6️⃣  Testing update_contact() with custom fields...")
    try:
        custom_fields_array = [
            {"key": "test_field", "field_value": "test_value"},
            {"key": "test_date", "field_value": datetime.now().isoformat()}
        ]
        result = await ghl.update_contact(
            contact_id=contact_id,
            contact_data={"customFields": custom_fields_array}
        )
        print(f"   ✅ Success: Custom fields updated")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        logger.exception("Error updating custom fields")
    
    print("\n" + "=" * 70)
    print("✅ All Function Tests Complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_all_functions())

