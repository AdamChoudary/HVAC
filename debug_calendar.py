#!/usr/bin/env python3
"""
GHL Calendar Debug Script

This script helps diagnose why the free-slots API might not be returning slots.
It will:
1. List all calendars in your GHL location
2. For each calendar, fetch free slots
3. Show detailed debugging information
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import json

# Add src to path
sys.path.append(os.getcwd())

from src.integrations.ghl import GHLClient
from src.utils.logging import logger, setup_logging

# Setup logging
setup_logging()

async def debug_calendars():
    print("\n" + "="*60)
    print("GHL CALENDAR FREE-SLOTS DEBUG TOOL")
    print("="*60 + "\n")
    
    ghl = GHLClient()
    
    # Step 1: Get all calendars
    print("📋 Step 1: Fetching all calendars...")
    try:
        calendars = await ghl.get_calendars()
        print(f"✅ Found {len(calendars)} calendar(s)\n")
        
        if not calendars:
            print("❌ No calendars found. Please check:")
            print("   - GHL API key is correct")
            print("   - Location ID is correct")
            print("   - Account has calendars set up")
            return
            
        # Display calendars
        for idx, cal in enumerate(calendars, 1):
            cal_id = cal.get("id", "N/A")
            cal_name = cal.get("name", "Unnamed")
            print(f"   {idx}. {cal_name}")
            print(f"      ID: {cal_id}")
            print()
            
    except Exception as e:
        print(f"❌ Error fetching calendars: {e}")
        return
    
    # Step 2: Test free-slots for each calendar
    print("\n" + "-"*60)
    print("📅 Step 2: Testing free-slots endpoint for each calendar")
    print("-"*60 + "\n")
    
    # Test with different date ranges
    today = datetime.now()
    test_ranges = [
        ("Tomorrow (1 day)", 
         (today + timedelta(days=1)).strftime("%Y-%m-%d"), 
         (today + timedelta(days=1)).strftime("%Y-%m-%d")),
        ("Next 7 days", 
         today.strftime("%Y-%m-%d"), 
         (today + timedelta(days=7)).strftime("%Y-%m-%d")),
        ("Next 30 days", 
         today.strftime("%Y-%m-%d"), 
         (today + timedelta(days=30)).strftime("%Y-%m-%d"))
    ]
    
    for cal in calendars:
        cal_id = cal.get("id")
        cal_name = cal.get("name", "Unnamed")
        
        print(f"\n🔍 Testing: {cal_name} (ID: {cal_id})")
        print("-" * 40)
        
        for range_name, start, end in test_ranges:
            print(f"\n   📆 {range_name}: {start} to {end}")
            
            try:
                # Fetch free slots
                slots = await ghl.get_calendar_free_slots(
                    calendar_id=cal_id,
                    start_date=start,
                    end_date=end
                )
                
                if slots:
                    print(f"   ✅ Found {len(slots)} FREE slot(s)!")
                    # Show first 3 slots
                    for i, slot in enumerate(slots[:3], 1):
                        if isinstance(slot, dict):
                            start_time = slot.get("startTime") or slot.get("start") or "N/A"
                            print(f"      {i}. {start_time}")
                        else:
                            print(f"      {i}. {slot}")
                    if len(slots) > 3:
                        print(f"      ... and {len(slots) - 3} more")
                else:
                    print(f"   ⚠️ No slots returned")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    # Step 3: Recommendations
    print("\n" + "="*60)
    print("💡 TROUBLESHOOTING TIPS")
    print("="*60 + "\n")
    
    print("If you're seeing 0 slots, here's what to check in GHL:")
    print()
    print("1. Calendar Settings → Availability")
    print("   - Ensure you have set available hours (e.g., 8am-4:30pm)")
    print("   - Check that weekdays are enabled")
    print("   - Verify slot duration is configured")
    print()
    print("2. Calendar Settings → Advanced")
    print("   - Check minimum scheduling notice")
    print("   - Verify date range availability settings")
    print()
    print("3. Calendar Settings → Team Members")
    print("   - If calendar requires team assignment, note the user ID")
    print("   - You may need to pass user_id parameter")
    print()
    print("4. Test in GHL directly:")
    print("   - Go to Calendars → [Your Calendar] → Preview")
    print("   - Try to book an appointment manually")
    print("   - If no slots show there, the API won't return any either")
    print()

if __name__ == "__main__":
    asyncio.run(debug_calendars())
