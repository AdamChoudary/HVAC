"""
Test script for book_appointment function
"""
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.integrations.ghl import GHLClient
from src.config import settings


async def test_book_appointment():
    """Test booking an appointment"""
    print("\n" + "="*70)
    print("TEST: Book Appointment")
    print("="*70)
    
    ghl = GHLClient()
    
    # First, get calendars
    print("\n1. Getting calendars...")
    calendars = await ghl.get_calendars()
    print(f"   Found {len(calendars)} calendars")
    
    if not calendars:
        print("❌ No calendars found")
        return
    
    # Use Diagnostic calendar
    calendar_id = None
    for cal in calendars:
        if "diagnostic" in cal.get("name", "").lower():
            calendar_id = cal.get("id")
            print(f"   Using calendar: {cal.get('name')} (ID: {calendar_id})")
            break
    
    if not calendar_id:
        calendar_id = calendars[0].get("id")
        print(f"   Using first calendar: {calendars[0].get('name')} (ID: {calendar_id})")
    
    # Create a test contact first
    print("\n2. Creating test contact...")
    try:
        contact_data = {
            "firstName": "Test",
            "lastName": "Appointment",
            "phone": "+15035559999",
            "email": "test.appointment@example.com"
        }
        contact = await ghl.create_contact(contact_data)
        contact_id = contact.get("id") or contact.get("contactId")
        print(f"   ✅ Contact created: {contact_id}")
    except Exception as e:
        print(f"   ❌ Failed to create contact: {e}")
        return
    
    # Book appointment for tomorrow at 2 PM
    print("\n3. Booking appointment...")
    tomorrow = datetime.now() + timedelta(days=1)
    start_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)
    
    start_time_str = start_time.isoformat() + "Z"
    end_time_str = end_time.isoformat() + "Z"
    
    print(f"   Start: {start_time_str}")
    print(f"   End: {end_time_str}")
    print(f"   Title: Test Appointment")
    
    try:
        result = await ghl.book_appointment(
            calendar_id=calendar_id,
            contact_id=contact_id,
            start_time=start_time_str,
            end_time=end_time_str,
            title="Test Appointment - AI Voice Agent",
            notes="Test appointment created by AI voice agent"
        )
        
        print(f"\n✅ Success!")
        print(f"   Appointment ID: {result.get('id')}")
        print(f"   Result: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"\n❌ Failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_book_appointment())

