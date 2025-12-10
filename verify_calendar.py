import asyncio
import sys
import os
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

# Add src to path
sys.path.append(os.getcwd())

from src.models import CheckCalendarAvailabilityRequest, ServiceType
from src.functions.check_calendar_availability import check_calendar_availability
from src.utils.logging import logger, setup_logging

# Setup logging
setup_logging()

async def verify_calendar():
    print("\n--- Verifying Calendar Availability ---")
    
    # Test parameters
    start_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d") # Tomorrow
    end_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
    
    print(f"Checking availability from {start_date} to {end_date}")
    
    request = CheckCalendarAvailabilityRequest(
        service_type=ServiceType.REPAIR, # Should map to Diagnostic/Repair calendar
        start_date=start_date,
        end_date=end_date,
        calendar_id="" # Let it auto-detect
    )
    
    try:
        response = await check_calendar_availability(request)
        
        print(f"\n✅ Calendar ID used: {response.calendar_id}")
        print(f"✅ Slots found: {len(response.slots)}")
        
        if not response.slots:
            print("⚠️ No slots found. This might be correct if calendar is full, but check logs.")
            return
            
        # Verify slots are within Field Hours (8:00 AM - 4:30 PM)
        print("\n--- Validating Slot Times ---")
        field_start = time(8, 0)
        field_end = time(16, 30)
        pacific_tz = ZoneInfo("America/Los_Angeles")
        
        all_valid = True
        for slot in response.slots[:5]: # Check first 5
            dt = datetime.fromisoformat(slot.start_time)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=pacific_tz)
            else:
                dt = dt.astimezone(pacific_tz)
                
            slot_time = dt.time()
            is_valid = field_start <= slot_time < field_end
            
            status = "✅" if is_valid else "❌"
            print(f"{status} {dt.strftime('%Y-%m-%d %H:%M')} (Pacific)")
            
            if not is_valid:
                all_valid = False
                
        if all_valid:
            print("\n✅ All checked slots are within Field Hours (8:00 AM - 4:30 PM)")
        else:
            print("\n❌ Some slots are OUTSIDE Field Hours!")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_calendar())
