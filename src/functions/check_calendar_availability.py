from src.models import (
    CheckCalendarAvailabilityRequest,
    CheckCalendarAvailabilityResponse,
    CalendarSlot,
    ServiceType
)
from src.integrations.ghl import GHLClient
from datetime import datetime, timedelta
from typing import List


async def check_calendar_availability(
    request: CheckCalendarAvailabilityRequest
) -> CheckCalendarAvailabilityResponse:
    """
    Check available appointment slots in GHL calendar.
    Maps service types to appropriate calendars.
    """
    ghl = GHLClient()
    
    # Get calendars
    calendars = await ghl.get_calendars()
    
    # Determine which calendar to use based on service type
    calendar_id = request.calendar_id
    if not calendar_id:
        # Map service types to calendar names/IDs
        # Updated to match new calendar names: Diagnostic, Proposal, Repair, Installation
        calendar_name_lower = ""
        if request.service_type in [ServiceType.REPAIR, ServiceType.MAINTENANCE]:
            # Find Diagnostic or Repair calendar
            for cal in calendars:
                calendar_name_lower = cal.get("name", "").lower()
                if any(keyword in calendar_name_lower for keyword in ["diagnostic", "service call", "repair", "service"]):
                    calendar_id = cal.get("id")
                    break
        elif request.service_type == ServiceType.ESTIMATE:
            # Find Proposal/Estimate calendar
            for cal in calendars:
                calendar_name_lower = cal.get("name", "").lower()
                if any(keyword in calendar_name_lower for keyword in ["proposal", "estimate", "sales"]):
                    calendar_id = cal.get("id")
                    break
        elif request.service_type == ServiceType.INSTALLATION:
            # Find Installation calendar
            for cal in calendars:
                calendar_name_lower = cal.get("name", "").lower()
                if "install" in calendar_name_lower:
                    calendar_id = cal.get("id")
                    break
        
        # Fallback to first calendar if not found
        if not calendar_id and calendars:
            calendar_id = calendars[0].get("id")
    
    if not calendar_id:
        return CheckCalendarAvailabilityResponse(
            slots=[],
            calendar_id=""
        )
    
    # Get availability
    availability = await ghl.get_calendar_availability(
        calendar_id=calendar_id,
        start_date=request.start_date,
        end_date=request.end_date
    )
    
    # Convert to our format
    slots = [
        CalendarSlot(
            start_time=slot.get("startTime", ""),
            end_time=slot.get("endTime", ""),
            available=slot.get("available", False)
        )
        for slot in availability
    ]
    
    return CheckCalendarAvailabilityResponse(
        slots=slots,
        calendar_id=calendar_id
    )


