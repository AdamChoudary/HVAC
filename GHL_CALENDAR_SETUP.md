# GHL Calendar Configuration Guide

## Overview
The system now uses the official GHL `GET /calendars/{calendarId}/free-slots` endpoint to fetch **available (non-booked) slots** directly from GoHighLevel.

## Current Status
✅ **API Integration**: Working correctly  
⚠️ **Calendar Configuration**: Needs setup in GHL

The API is returning 0 slots because your GHL calendar doesn't have availability configured yet.

## How to Configure Your GHL Calendar

### 1. Set Up Calendar Availability

1. Log in to GoHighLevel
2. Navigate to **Settings → Calendars**
3. Select your calendar (e.g., "Diagnostic" or "Service Call")
4. Go to **Availability** tab

**Configure:**
- **Available Hours**: Set to your field hours (8:00 AM - 4:30 PM)
- **Days**: Enable Monday through Friday
- **Slot Duration**: Set to 1 hour (or your preferred appointment length)
- **Slot Interval**: Set to match your booking preferences

### 2. Advanced Settings

Go to **Advanced** tab and verify:
- **Minimum Scheduling Notice**: Set appropriately (e.g., 2 hours)
- **Date Range**: Ensure future dates are not restricted
- **Buffer Time**: Add buffer between appointments if needed

### 3. Verify Configuration

**Test in GHL First:**
1. Go to **Calendars** → Select your calendar
2. Click **Preview** or **Book Appointment**
3. Try to book a test appointment
4. You should see available slots appear

If you don't see slots in the GHL preview, the API won't return any either.

### 4. Test the API

Once you've configured availability in GHL, run the debug script:

\`\`\`bash
python3 debug_calendar.py
\`\`\`

This will show you:
- All calendars in your GHL location
- Available slots for each calendar
- Detailed debug information

## What the Free-Slots Endpoint Does

The `free-slots` endpoint returns **ONLY available slots** that:
- ✅ Fall within your configured availability hours
- ✅ Are NOT already booked
- ✅ Respect minimum scheduling notice
- ✅ Respect buffer time and other calendar rules

Our system adds an additional filter to ensure slots are within **Field Hours (8:00 AM - 4:30 PM)**, even if GHL returns later slots.

## Optional: User-Specific Calendars

If your calendar is assigned to specific team members:
1. Note the User ID from GHL (Settings → Team)
2. Pass it when calling the API:

\`\`\`python
slots = await ghl.get_calendar_free_slots(
    calendar_id="your_calendar_id",
    start_date="2025-11-28",
    end_date="2025-12-05",
    user_id="your_user_id"  # Optional
)
\`\`\`

## Need Help?

Run the debug script to troubleshoot:
\`\`\`bash
python3 debug_calendar.py
\`\`\`

Check the logs for detailed information about what the API is returning.
