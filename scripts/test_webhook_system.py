"""
Comprehensive test script for webhook system and API endpoints
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from src.config import settings
from src.integrations.ghl import GHLClient
from src.utils.logging import logger

# Suppress debug logs for cleaner output
import logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


async def test_webhook_endpoint():
    """Test webhook endpoint with various payloads"""
    print("\n" + "=" * 70)
    print("1️⃣  TESTING WEBHOOK ENDPOINT")
    print("=" * 70)
    
    server_url = settings.webhook_base_url or "https://scott-valley-hvac-api.fly.dev"
    webhook_url = f"{server_url}/webhooks/ghl"
    
    test_cases = [
        {
            "name": "Contact Created (with type field)",
            "payload": {
                "type": "contact.created",
                "locationId": settings.ghl_location_id,
                "contactId": "TEST_CONTACT_ID_123"
            }
        },
        {
            "name": "Contact Created (with event field)",
            "payload": {
                "event": "contact.created",
                "locationId": settings.ghl_location_id,
                "contactId": "TEST_CONTACT_ID_456"
            }
        },
        {
            "name": "Contact Updated",
            "payload": {
                "type": "contact.updated",
                "locationId": settings.ghl_location_id,
                "contactId": "TEST_CONTACT_ID_789"
            }
        },
        {
            "name": "Appointment Created",
            "payload": {
                "type": "appointment.created",
                "locationId": settings.ghl_location_id,
                "contactId": "TEST_CONTACT_ID_101",
                "data": {
                    "appointment": {
                        "id": "TEST_APPT_123",
                        "title": "Test Appointment"
                    }
                }
            }
        },
        {
            "name": "Form Submitted",
            "payload": {
                "type": "form.submitted",
                "locationId": settings.ghl_location_id,
                "data": {
                    "contact": {
                        "id": "TEST_CONTACT_ID_202"
                    },
                    "form": {
                        "id": "TEST_FORM_123",
                        "name": "Test Form"
                    }
                }
            }
        },
        {
            "name": "Location ID Mismatch (should be ignored)",
            "payload": {
                "type": "contact.created",
                "locationId": "WRONG_LOCATION_ID",
                "contactId": "TEST_CONTACT_ID_303"
            }
        }
    ]
    
    results = []
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for test_case in test_cases:
            print(f"\n📋 Testing: {test_case['name']}")
            try:
                response = await client.post(
                    webhook_url,
                    json=test_case['payload'],
                    headers={"Content-Type": "application/json"}
                )
                
                result_data = response.json() if response.status_code == 200 else response.text
                
                if response.status_code == 200:
                    status = result_data.get("status", "unknown")
                    if status == "ok":
                        print(f"   ✅ PASS - Status: {status}, Event: {result_data.get('event')}")
                        results.append(("PASS", test_case['name']))
                    elif status == "ignored":
                        print(f"   ⚠️  IGNORED - Reason: {result_data.get('reason')}")
                        results.append(("IGNORED", test_case['name']))
                    else:
                        print(f"   ⚠️  UNKNOWN - Response: {result_data}")
                        results.append(("UNKNOWN", test_case['name']))
                else:
                    print(f"   ❌ FAIL - Status: {response.status_code}, Response: {result_data}")
                    results.append(("FAIL", test_case['name']))
                    
            except Exception as e:
                print(f"   ❌ ERROR - {str(e)}")
                results.append(("ERROR", test_case['name']))
    
    return results


async def test_book_appointment_api():
    """Test book-appointment API with correct format"""
    print("\n" + "=" * 70)
    print("2️⃣  TESTING BOOK-APPOINTMENT API")
    print("=" * 70)
    
    server_url = settings.webhook_base_url or "https://scott-valley-hvac-api.fly.dev"
    api_url = f"{server_url}/functions/book-appointment"
    
    # First, get a real contact and calendar
    ghl = GHLClient()
    
    try:
        # Get calendars
        calendars = await ghl.get_calendars()
        if not calendars:
            print("   ⚠️  No calendars found, skipping appointment booking test")
            return []
        
        # Get first active calendar
        active_calendar = next((c for c in calendars if c.get("status") == "active"), None)
        if not active_calendar:
            print("   ⚠️  No active calendars found, skipping appointment booking test")
            return []
        
        calendar_id = active_calendar.get("id")
        calendar_name = active_calendar.get("name", "Unknown")
        print(f"   📅 Using calendar: {calendar_name} (ID: {calendar_id})")
        
        # Create a test contact
        test_phone = f"+1555{datetime.now().strftime('%H%M%S')}"
        test_email = f"test{datetime.now().strftime('%H%M%S')}@test.com"
        
        contact_data = {
            "firstName": "Test",
            "lastName": f"User{datetime.now().strftime('%H%M%S')}",
            "phone": test_phone,
            "email": test_email
        }
        
        print(f"   👤 Creating test contact: {test_phone}")
        contact_result = await ghl.create_contact(contact_data)
        
        # Extract contact ID
        if isinstance(contact_result, dict):
            contact_id = contact_result.get("id") or contact_result.get("contact", {}).get("id", "")
        else:
            contact_id = ""
        
        if not contact_id:
            print("   ❌ FAIL - Could not create test contact")
            return [("FAIL", "Create test contact")]
        
        print(f"   ✅ Created contact: {contact_id}")
        
        # Test with ISO datetime format
        tomorrow = datetime.now() + timedelta(days=1)
        start_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0).isoformat() + "Z"
        end_time = tomorrow.replace(hour=14, minute=30, second=0, microsecond=0).isoformat() + "Z"
        
        test_payload = {
            "contact_id": contact_id,
            "calendar_id": calendar_id,
            "start_time": start_time,
            "end_time": end_time,
            "title": "Test Appointment",
            "service_type": "repair",
            "notes": "Automated test appointment",
            "urgency": "standard"
        }
        
        print(f"\n   📋 Testing book-appointment with ISO datetime format")
        print(f"      Start: {start_time}")
        print(f"      End: {end_time}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                api_url,
                json=test_payload,
                headers={"Content-Type": "application/json"}
            )
            
            result_data = response.json() if response.status_code == 200 else response.text
            
            if response.status_code == 200:
                if result_data.get("success"):
                    appointment_id = result_data.get("appointment_id", "")
                    print(f"   ✅ PASS - Appointment booked! ID: {appointment_id}")
                    return [("PASS", "Book appointment with ISO format")]
                else:
                    print(f"   ❌ FAIL - {result_data.get('message', 'Unknown error')}")
                    return [("FAIL", "Book appointment with ISO format")]
            else:
                print(f"   ❌ FAIL - Status: {response.status_code}")
                print(f"      Response: {result_data}")
                return [("FAIL", "Book appointment with ISO format")]
                
    except Exception as e:
        print(f"   ❌ ERROR - {str(e)}")
        import traceback
        traceback.print_exc()
        return [("ERROR", "Book appointment test")]


async def test_server_health():
    """Test server health and accessibility"""
    print("\n" + "=" * 70)
    print("3️⃣  TESTING SERVER HEALTH")
    print("=" * 70)
    
    server_url = settings.webhook_base_url or "https://scott-valley-hvac-api.fly.dev"
    
    endpoints = [
        ("/", "Root endpoint"),
        ("/health", "Health check"),
    ]
    
    results = []
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for endpoint, name in endpoints:
            url = f"{server_url}{endpoint}"
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    print(f"   ✅ PASS - {name} (Status: {response.status_code})")
                    results.append(("PASS", name))
                else:
                    print(f"   ⚠️  WARN - {name} (Status: {response.status_code})")
                    results.append(("WARN", name))
            except Exception as e:
                print(f"   ❌ FAIL - {name} - {str(e)}")
                results.append(("FAIL", name))
    
    return results


async def test_ghl_connection():
    """Test GHL API connection"""
    print("\n" + "=" * 70)
    print("4️⃣  TESTING GHL API CONNECTION")
    print("=" * 70)
    
    ghl = GHLClient()
    
    try:
        # Test getting calendars
        calendars = await ghl.get_calendars()
        print(f"   ✅ PASS - GHL API Connection")
        print(f"      Found {len(calendars)} calendars")
        print(f"      Location ID: {settings.ghl_location_id}")
        
        # Show calendar details
        for cal in calendars[:3]:  # Show first 3
            name = cal.get("name", "Unknown")
            status = cal.get("status", "unknown")
            cal_id = cal.get("id", "N/A")
            print(f"      - {name}: {status} (ID: {cal_id[:20]}...)")
        
        return [("PASS", "GHL API Connection")]
    except Exception as e:
        print(f"   ❌ FAIL - GHL API Connection - {str(e)}")
        return [("FAIL", "GHL API Connection")]


async def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("🧪 COMPREHENSIVE WEBHOOK SYSTEM TEST")
    print("=" * 70)
    print(f"\nServer URL: {settings.webhook_base_url or 'https://scott-valley-hvac-api.fly.dev'}")
    print(f"GHL Location ID: {settings.ghl_location_id}")
    print(f"GHL API Key: {'SET' if settings.get_ghl_api_key() else 'NOT SET'}")
    
    all_results = []
    
    # Test 1: Server Health
    health_results = await test_server_health()
    all_results.extend(health_results)
    
    # Test 2: GHL Connection
    ghl_results = await test_ghl_connection()
    all_results.extend(ghl_results)
    
    # Test 3: Webhook Endpoint
    webhook_results = await test_webhook_endpoint()
    all_results.extend(webhook_results)
    
    # Test 4: Book Appointment API
    appointment_results = await test_book_appointment_api()
    all_results.extend(appointment_results)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for status, _ in all_results if status == "PASS")
    failed = sum(1 for status, _ in all_results if status == "FAIL")
    errors = sum(1 for status, _ in all_results if status == "ERROR")
    ignored = sum(1 for status, _ in all_results if status == "IGNORED")
    warnings = sum(1 for status, _ in all_results if status == "WARN")
    
    print(f"\n✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  Errors: {errors}")
    print(f"⏭️  Ignored: {ignored}")
    print(f"⚠️  Warnings: {warnings}")
    print(f"📊 Total: {len(all_results)}")
    
    if failed > 0 or errors > 0:
        print("\n❌ FAILED TESTS:")
        for status, name in all_results:
            if status in ["FAIL", "ERROR"]:
                print(f"   - {name}: {status}")
    
    if ignored > 0:
        print("\n⏭️  IGNORED TESTS (Expected):")
        for status, name in all_results:
            if status == "IGNORED":
                print(f"   - {name}: {status}")
    
    print("\n" + "=" * 70)
    
    if failed == 0 and errors == 0:
        print("✅ All critical tests passed!")
    else:
        print("⚠️  Some tests failed. Review errors above.")


if __name__ == "__main__":
    asyncio.run(main())

