from src.models import (
    CheckCalendarAvailabilityRequest,
    CheckCalendarAvailabilityResponse,
    CalendarSlot,
    ServiceType
)
from src.integrations.ghl import GHLClient
from src.utils.business_hours import get_current_datetime_pacific
from src.utils.logging import logger
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo
from typing import List


async def check_calendar_availability(
    request: CheckCalendarAvailabilityRequest
) -> CheckCalendarAvailabilityResponse:
    """
    Check available appointment slots by:
    1. Generating slots during Field Hours (8:00 AM - 4:30 PM)
    2. Fetching booked appointments from GHL
    3. Excluding booked slots from the response
    
    This ensures we only return truly available slots.
    """
    ghl = GHLClient()
    
    # Get current date and time
    current_datetime = get_current_datetime_pacific()
    current_date = current_datetime.date()
    current_time = current_datetime.time()
    
    start_date = request.start_date
    end_date = request.end_date
    
    # Validate dates
    try:
        if start_date:
            start_dt = datetime.fromisoformat(start_date.split("T")[0] if "T" in start_date else start_date)
            start_date_obj = start_dt.date()
        else:
            start_date_obj = current_date
        
        # If start date is in the past, use tomorrow
        if start_date_obj < current_date:
            start_date_obj = current_date + timedelta(days=1)
            start_date = start_date_obj.strftime("%Y-%m-%d")
        # If start date is today, check if we're past business hours
        elif start_date_obj == current_date:
            # Business hours end at 4:30 PM (16:30)
            if current_time >= time(16, 30):
                # Past business hours, start from tomorrow
                start_date_obj = current_date + timedelta(days=1)
                start_date = start_date_obj.strftime("%Y-%m-%d")
                logger.info(f"⏰ Past business hours ({current_time}), starting availability from tomorrow: {start_date}")
        
        # Ensure end_date is at least 7 days from start_date
        if end_date:
            end_dt = datetime.fromisoformat(end_date.split("T")[0] if "T" in end_date else end_date)
            if end_dt.date() < start_date_obj:
                end_date = (start_date_obj + timedelta(days=7)).strftime("%Y-%m-%d")
        else:
            end_date = (start_date_obj + timedelta(days=7)).strftime("%Y-%m-%d")
            
    except Exception as e:
        logger.warning(f"Date parsing error: {e}, using tomorrow as start date")
        start_date = (current_date + timedelta(days=1)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = (current_date + timedelta(days=8)).strftime("%Y-%m-%d")
    
    # Get calendar ID
    calendar_id = request.calendar_id
    if not calendar_id:
        calendars = await ghl.get_calendars()
        calendar_name_lower = ""
        if request.service_type in [ServiceType.REPAIR, ServiceType.MAINTENANCE]:
            for cal in calendars:
                calendar_name_lower = cal.get("name", "").lower()
                if any(keyword in calendar_name_lower for keyword in ["diagnostic", "service call", "repair", "service"]):
                    calendar_id = cal.get("id")
                    break
        elif request.service_type == ServiceType.ESTIMATE:
            for cal in calendars:
                calendar_name_lower = cal.get("name", "").lower()
                if any(keyword in calendar_name_lower for keyword in ["proposal", "estimate", "sales"]):
                    calendar_id = cal.get("id")
                    break
        elif request.service_type == ServiceType.INSTALLATION:
            for cal in calendars:
                calendar_name_lower = cal.get("name", "").lower()
                if "install" in calendar_name_lower:
                    calendar_id = cal.get("id")
                    break
        
        # Fallback
        if not calendar_id and calendars:
            calendar_id = calendars[0].get("id")
    
    if not calendar_id:
        return CheckCalendarAvailabilityResponse(slots=[], calendar_id="")
    
    # Use the working method: generate slots + exclude booked appointments
    logger.info(f"📅 Generating slots for Field Hours (8:00 AM - 4:30 PM)")
    logger.info(f"   Date range: {start_date} to {end_date}")
    
    # Get availability using the original working method
    availability = await ghl.get_calendar_availability(
        calendar_id=calendar_id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Process slots
    pacific_tz = ZoneInfo("America/Los_Angeles")
    processed_slots = []
    
    for slot in availability:
        if not slot.get("available", False):
            continue
            
        try:
            start_str = slot.get("startTime", "")
            end_str = slot.get("endTime", "")
            
            if not start_str:
                continue
                
            # Parse datetime
            dt = datetime.fromisoformat(start_str)
            
            # Normalize to Pacific
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=pacific_tz)
            else:
                dt = dt.astimezone(pacific_tz)
            
            # Filter: Must be in future (relative to now)
            if dt <= current_datetime:
                continue
                
            # Add to list (already filtered by business hours in get_calendar_availability)
            processed_slots.append(CalendarSlot(
                start_time=start_str,
                end_time=end_str,
                available=True
            ))
            
        except Exception as e:
            logger.warning(f"Error processing slot {slot}: {e}")
            continue
            
    logger.info(f"✅ Returning {len(processed_slots)} available slots (booked appointments excluded)")
    
    return CheckCalendarAvailabilityResponse(
        slots=processed_slots,
        calendar_id=calendar_id
    )


