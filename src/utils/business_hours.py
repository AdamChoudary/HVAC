"""
Business hours utility for Scott Valley HVAC.
Checks if current time is within business hours.
Supports two schedules:
1. FIELD_HOURS: 8:00 AM - 4:30 PM, Monday-Friday (For scheduling service)
2. OFFICE_HOURS: 7:00 AM - 8:30 PM, Monday-Friday (For answering phones/transfers)
"""
from dataclasses import dataclass
from datetime import datetime, time
from typing import Dict, Set, Optional, Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def _load_zone(key: str) -> ZoneInfo:
    try:
        return ZoneInfo(key)
    except ZoneInfoNotFoundError as exc:
        raise RuntimeError(
            f"Time zone data for '{key}' not found. Install the 'tzdata' package."
        ) from exc


PACIFIC_TZ = _load_zone("America/Los_Angeles")
UTC_TZ = _load_zone("UTC")


@dataclass(frozen=True)
class OfficeHours:
    start: time
    end: time
    
    def contains(self, dt: datetime) -> bool:
        """Check if datetime falls within these hours"""
        local_time = dt.time()
        return self.start <= local_time <= self.end


# Schedule Types
ScheduleType = Literal["field", "office"]

# 1. Field/Service Hours: 8:00 AM - 4:30 PM, Monday-Friday
FIELD_HOURS: Dict[int, OfficeHours] = {
    0: OfficeHours(start=time(hour=8, minute=0), end=time(hour=16, minute=30)),  # Monday
    1: OfficeHours(start=time(hour=8, minute=0), end=time(hour=16, minute=30)),  # Tuesday
    2: OfficeHours(start=time(hour=8, minute=0), end=time(hour=16, minute=30)),  # Wednesday
    3: OfficeHours(start=time(hour=8, minute=0), end=time(hour=16, minute=30)),  # Thursday
    4: OfficeHours(start=time(hour=8, minute=0), end=time(hour=16, minute=30)),  # Friday
}

# 2. Office/Phone Hours: 7:00 AM - 8:30 PM, Monday-Friday
OFFICE_HOURS: Dict[int, OfficeHours] = {
    0: OfficeHours(start=time(hour=7, minute=0), end=time(hour=20, minute=30)),  # Monday
    1: OfficeHours(start=time(hour=7, minute=0), end=time(hour=20, minute=30)),  # Tuesday
    2: OfficeHours(start=time(hour=7, minute=0), end=time(hour=20, minute=30)),  # Wednesday
    3: OfficeHours(start=time(hour=7, minute=0), end=time(hour=20, minute=30)),  # Thursday
    4: OfficeHours(start=time(hour=7, minute=0), end=time(hour=20, minute=30)),  # Friday
}

# Holidays when business is closed
HOLIDAYS: Set[str] = {
    # Format: YYYY-MM-DD
    "2025-01-01",  # New Year's Day
    "2025-07-04",  # Independence Day
    "2025-12-25",  # Christmas Day
    "2026-01-01",  # New Year's Day
    "2026-07-04",  # Independence Day
    "2026-12-25",  # Christmas Day
}


def get_current_time_pacific() -> datetime:
    """Return aware datetime in Pacific Time (Salem, OR timezone)."""
    return datetime.now(tz=UTC_TZ).astimezone(PACIFIC_TZ)


def _ensure_pacific(reference_time: datetime) -> datetime:
    """Normalize a datetime to Pacific Time."""
    if reference_time.tzinfo is None:
        # Assume reference time is already Pacific if naive
        return reference_time.replace(tzinfo=PACIFIC_TZ)
    return reference_time.astimezone(PACIFIC_TZ)


def check_business_hours(reference_time: Optional[datetime] = None, schedule_type: ScheduleType = "field") -> Dict[str, any]:
    """
    Determine if a given time falls within business hours.
    
    Args:
        reference_time: Optional datetime to check. Defaults to current Pacific time.
        schedule_type: "field" (8a-4:30p) or "office" (7a-8:30p). Defaults to "field".
    
    Returns:
        dict containing status and messages.
    """
    current_time = _ensure_pacific(reference_time) if reference_time else get_current_time_pacific()
    day_of_week = current_time.weekday()  # Monday=0, Sunday=6
    current_date_str = current_time.strftime("%Y-%m-%d")
    current_time_str = current_time.strftime("%I:%M %p").lstrip("0")
    
    # Select schedule
    schedule = FIELD_HOURS if schedule_type == "field" else OFFICE_HOURS
    schedule_name = "Field Service" if schedule_type == "field" else "Office"
    
    # Check if it's a holiday
    if current_date_str in HOLIDAYS:
        return {
            "isBusinessHours": False,
            "message": f"We're closed today for a holiday.",
            "day": current_time.strftime("%A"),
            "timezone": "America/Los_Angeles",
            "currentTime": current_time_str,
            "currentDate": current_date_str,
            "currentYear": str(current_time.year),
            "businessHoursToday": "Closed (Holiday)",
        }
    
    # Check if it's a weekday
    if day_of_week not in schedule:
        return {
            "isBusinessHours": False,
            "message": f"We're closed on weekends.",
            "day": current_time.strftime("%A"),
            "timezone": "America/Los_Angeles",
            "currentTime": current_time_str,
            "currentDate": current_date_str,
            "currentYear": str(current_time.year),
            "businessHoursToday": "Closed (Weekend)",
        }
    
    office_hours = schedule[day_of_week]
    
    if office_hours.contains(current_time):
        end_display = office_hours.end.strftime("%I:%M %p").lstrip("0")
        return {
            "isBusinessHours": True,
            "message": f"We're open now until {end_display} Pacific Time today.",
            "day": current_time.strftime("%A"),
            "timezone": "America/Los_Angeles",
            "currentTime": current_time_str,
            "currentDate": current_date_str,
            "currentYear": str(current_time.year),
            "businessHoursToday": f"{office_hours.start.strftime('%I:%M %p').lstrip('0')} - {end_display}",
        }
    
    # Outside business hours
    start_display = office_hours.start.strftime("%I:%M %p").lstrip("0")
    end_display = office_hours.end.strftime("%I:%M %p").lstrip("0")
    
    # Determine if we're before or after hours
    if current_time.time() < office_hours.start:
        next_open = f"today at {start_display}"
    else:
        # After hours - next open is tomorrow (or Monday if it's Friday)
        if day_of_week == 4:  # Friday
            next_open = "Monday at " + (schedule[0].start.strftime("%I:%M %p").lstrip("0"))
        else:
            next_open = f"tomorrow at {start_display}"
    
    return {
        "isBusinessHours": False,
        "message": f"We're currently closed. Our {schedule_name} hours today are {start_display} to {end_display} Pacific Time. We'll be open {next_open}.",
        "day": current_time.strftime("%A"),
        "timezone": "America/Los_Angeles",
        "currentTime": current_time_str,
        "currentDate": current_date_str,
        "currentYear": str(current_time.year),
        "businessHoursToday": f"{start_display} - {end_display}",
    }


def get_current_date_pacific() -> str:
    """Get current date in Pacific Time (YYYY-MM-DD format)."""
    return get_current_time_pacific().strftime("%Y-%m-%d")


def get_current_datetime_pacific() -> datetime:
    """Get current datetime in Pacific Time."""
    return get_current_time_pacific()

