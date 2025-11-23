"""
Test script for checkCalendarAvailability function
"""
import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.functions.check_calendar_availability import check_calendar_availability
from src.models import CheckCalendarAvailabilityRequest, ServiceType
from src.integrations.ghl import GHLClient
from src.config import settings


async def test_get_calendars():
    """Test 1: Get all calendars"""
    print("\n" + "="*70)
    print("TEST 1: Get All Calendars")
    print("="*70)
    
    try:
        ghl = GHLClient()
        calendars = await ghl.get_calendars()
        
        print(f"✅ Successfully retrieved {len(calendars)} calendars:")
        for i, cal in enumerate(calendars, 1):
            print(f"  {i}. {cal.get('name')} (ID: {cal.get('id')})")
        
        return calendars
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return []


async def test_get_calendar_availability_direct():
    """Test 2: Test GHL get_calendar_availability directly"""
    print("\n" + "="*70)
    print("TEST 2: Direct GHL Calendar Availability API Call")
    print("="*70)
    
    try:
        ghl = GHLClient()
        calendars = await ghl.get_calendars()
        
        if not calendars:
            print("❌ No calendars found")
            return
        
        # Use first calendar
        calendar_id = calendars[0].get("id")
        calendar_name = calendars[0].get("name")
        
        print(f"Testing calendar: {calendar_name} (ID: {calendar_id})")
        
        # Test with next 7 days
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=7)
        
        print(f"Checking availability from {start_date} to {end_date}")
        
        availability = await ghl.get_calendar_availability(
            calendar_id=calendar_id,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        print(f"✅ Successfully retrieved availability")
        print(f"   Found {len(availability)} time slots")
        
        if availability:
            print("\nFirst 5 slots:")
            for i, slot in enumerate(availability[:5], 1):
                print(f"  {i}. {slot.get('startTime')} - {slot.get('endTime')} (Available: {slot.get('available')})")
        else:
            print("⚠️  No slots returned")
        
        return availability
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_check_calendar_availability_function():
    """Test 3: Test the check_calendar_availability function"""
    print("\n" + "="*70)
    print("TEST 3: check_calendar_availability Function")
    print("="*70)
    
    try:
        # Test with repair service type
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=7)
        
        request = CheckCalendarAvailabilityRequest(
            service_type=ServiceType.REPAIR,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        print(f"Request: service_type=repair, start_date={start_date}, end_date={end_date}")
        
        response = await check_calendar_availability(request)
        
        print(f"✅ Function executed successfully")
        print(f"   Calendar ID: {response.calendar_id}")
        print(f"   Slots found: {len(response.slots)}")
        
        if response.slots:
            print("\nFirst 5 slots:")
            for i, slot in enumerate(response.slots[:5], 1):
                print(f"  {i}. {slot.start_time} - {slot.end_time} (Available: {slot.available})")
        else:
            print("⚠️  No slots returned")
        
        return response
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_all_service_types():
    """Test 4: Test all service types"""
    print("\n" + "="*70)
    print("TEST 4: Test All Service Types")
    print("="*70)
    
    service_types = [
        (ServiceType.REPAIR, "repair"),
        (ServiceType.MAINTENANCE, "maintenance"),
        (ServiceType.ESTIMATE, "estimate"),
        (ServiceType.INSTALLATION, "installation")
    ]
    
    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=7)
    
    results = {}
    
    for service_type, name in service_types:
        print(f"\nTesting {name}...")
        try:
            request = CheckCalendarAvailabilityRequest(
                service_type=service_type,
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat()
            )
            
            response = await check_calendar_availability(request)
            
            results[name] = {
                "status": "✅ Success",
                "calendar_id": response.calendar_id,
                "slots_count": len(response.slots),
                "available_slots": sum(1 for s in response.slots if s.available)
            }
            
            print(f"  ✅ Calendar ID: {response.calendar_id}")
            print(f"  ✅ Slots: {len(response.slots)} (Available: {sum(1 for s in response.slots if s.available)})")
            
        except Exception as e:
            results[name] = {
                "status": f"❌ Failed: {str(e)}",
                "error": str(e)
            }
            print(f"  ❌ Error: {e}")
    
    return results


async def test_with_specific_calendar():
    """Test 5: Test with specific calendar ID"""
    print("\n" + "="*70)
    print("TEST 5: Test with Specific Calendar ID")
    print("="*70)
    
    try:
        ghl = GHLClient()
        calendars = await ghl.get_calendars()
        
        # Find Diagnostic calendar
        diagnostic_cal = None
        for cal in calendars:
            if "diagnostic" in cal.get("name", "").lower():
                diagnostic_cal = cal
                break
        
        if not diagnostic_cal:
            print("⚠️  Diagnostic calendar not found, using first calendar")
            diagnostic_cal = calendars[0] if calendars else None
        
        if not diagnostic_cal:
            print("❌ No calendars available")
            return
        
        calendar_id = diagnostic_cal.get("id")
        print(f"Using calendar: {diagnostic_cal.get('name')} (ID: {calendar_id})")
        
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=7)
        
        request = CheckCalendarAvailabilityRequest(
            service_type=ServiceType.REPAIR,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            calendar_id=calendar_id
        )
        
        response = await check_calendar_availability(request)
        
        print(f"✅ Success")
        print(f"   Calendar ID: {response.calendar_id}")
        print(f"   Slots: {len(response.slots)}")
        
        return response
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_api_endpoint():
    """Test 6: Test the API endpoint directly"""
    print("\n" + "="*70)
    print("TEST 6: Test API Endpoint")
    print("="*70)
    
    try:
        import httpx
        
        base_url = os.getenv("WEBHOOK_BASE_URL", "http://localhost:8000")
        endpoint = f"{base_url}/functions/check-calendar-availability"
        
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=7)
        
        payload = {
            "service_type": "repair",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        
        print(f"Testing endpoint: {endpoint}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(endpoint, json=payload)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success")
                print(f"   Calendar ID: {result.get('calendar_id')}")
                print(f"   Slots: {len(result.get('slots', []))}")
                return result
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🧪 CALENDAR AVAILABILITY TEST SUITE")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check environment
    print("\n📋 Environment Check:")
    print(f"   GHL API Key: {'✅ Set' if settings.get_ghl_api_key() else '❌ Missing'}")
    print(f"   GHL Location ID: {'✅ Set' if settings.ghl_location_id else '❌ Missing'}")
    
    if not settings.get_ghl_api_key() or not settings.ghl_location_id:
        print("\n❌ Missing required environment variables!")
        return
    
    tests = [
        ("Get Calendars", test_get_calendars),
        ("Direct GHL API Call", test_get_calendar_availability_direct),
        ("Function Test", test_check_calendar_availability_function),
        ("All Service Types", test_all_service_types),
        ("Specific Calendar", test_with_specific_calendar),
    ]
    
    # Only test API endpoint if server is running
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.get("http://localhost:8000/health")
        tests.append(("API Endpoint", test_api_endpoint))
    except:
        print("\n⚠️  FastAPI server not running, skipping API endpoint test")
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = {"status": "✅ Passed", "result": result}
            await asyncio.sleep(1)  # Small delay between tests
        except Exception as e:
            results[test_name] = {"status": "❌ Failed", "error": str(e)}
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for r in results.values() if "✅" in r.get("status", ""))
    failed = sum(1 for r in results.values() if "❌" in r.get("status", ""))
    
    print(f"\nTotal Tests: {len(results)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    print("\nDetailed Results:")
    for test_name, result in results.items():
        status = result.get("status", "Unknown")
        print(f"  {status} - {test_name}")
        if "error" in result:
            print(f"    Error: {result['error']}")
    
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())

