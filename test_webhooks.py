#!/usr/bin/env python3
"""Test all deployed webhook endpoints"""
import requests
import json
from datetime import datetime

SERVER_URL = "https://scott-valley-hvac-api.fly.dev"
WEBHOOK_URL = f"{SERVER_URL}/webhooks/ghl"
LOCATION_ID = "NHEXwG3xQVwKMO77jAuB"

def test_webhook(name, payload):
    """Test a webhook endpoint"""
    print(f"\n{'='*70}")
    print(f"🧪 TESTING: {name}")
    print(f"{'='*70}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"HTTP Status: {response.status_code}")
        
        try:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            if response.status_code == 200:
                status = result.get("status", "unknown")
                if status == "ok":
                    print(f"✅ PASS - Webhook processed successfully")
                    return True
                elif status == "ignored":
                    print(f"⏭️  IGNORED - {result.get('reason', 'Unknown reason')}")
                    return "ignored"
                else:
                    print(f"⚠️  UNKNOWN STATUS - {status}")
                    return False
            else:
                print(f"❌ FAIL - HTTP {response.status_code}")
                return False
        except json.JSONDecodeError:
            print(f"Response (not JSON): {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR - {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "="*70)
    print("🧪 TESTING ALL DEPLOYED WEBHOOK ENDPOINTS")
    print("="*70)
    print(f"Server URL: {SERVER_URL}")
    print(f"Webhook URL: {WEBHOOK_URL}")
    print(f"Location ID: {LOCATION_ID}")
    
    results = []
    timestamp = int(datetime.now().timestamp())
    
    # Test 1: Contact Created
    payload1 = {
        "type": "contact.created",
        "locationId": LOCATION_ID,
        "contactId": f"TEST_CONTACT_CREATED_{timestamp}"
    }
    result1 = test_webhook("1️⃣  Contact Created", payload1)
    results.append(("Contact Created", result1))
    
    # Test 2: Contact Updated
    payload2 = {
        "type": "contact.updated",
        "locationId": LOCATION_ID,
        "contactId": f"TEST_CONTACT_UPDATED_{timestamp}"
    }
    result2 = test_webhook("2️⃣  Contact Updated", payload2)
    results.append(("Contact Updated", result2))
    
    # Test 3: Appointment Created
    payload3 = {
        "type": "appointment.created",
        "locationId": LOCATION_ID,
        "contactId": f"TEST_CONTACT_APPT_{timestamp}",
        "data": {
            "appointment": {
                "id": f"TEST_APPT_{timestamp}",
                "title": "Test Appointment",
                "startTime": "2024-11-21T14:00:00Z",
                "endTime": "2024-11-21T14:30:00Z"
            }
        }
    }
    result3 = test_webhook("3️⃣  Appointment Created", payload3)
    results.append(("Appointment Created", result3))
    
    # Test 4: Form Submitted
    payload4 = {
        "type": "form.submitted",
        "locationId": LOCATION_ID,
        "data": {
            "contact": {
                "id": f"TEST_CONTACT_FORM_{timestamp}",
                "phone": "+15551234567",
                "email": "test@example.com"
            },
            "form": {
                "id": f"TEST_FORM_{timestamp}",
                "name": "Test Form"
            }
        }
    }
    result4 = test_webhook("4️⃣  Form Submitted", payload4)
    results.append(("Form Submitted", result4))
    
    # Test 5: Location ID Mismatch (should be ignored)
    payload5 = {
        "type": "contact.created",
        "locationId": "WRONG_LOCATION_ID",
        "contactId": f"TEST_CONTACT_WRONG_{timestamp}"
    }
    result5 = test_webhook("5️⃣  Location ID Mismatch (Should be Ignored)", payload5)
    results.append(("Location ID Mismatch", result5))
    
    # Test 6: Invalid Event Type
    payload6 = {
        "type": "unknown.event",
        "locationId": LOCATION_ID,
        "contactId": f"TEST_CONTACT_UNKNOWN_{timestamp}"
    }
    result6 = test_webhook("6️⃣  Invalid Event Type (Should Handle Gracefully)", payload6)
    results.append(("Invalid Event Type", result6))
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, r in results if r is True)
    failed = sum(1 for _, r in results if r is False)
    ignored = sum(1 for _, r in results if r == "ignored")
    
    print(f"\n✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⏭️  Ignored (Expected): {ignored}")
    print(f"📊 Total: {len(results)}")
    
    print("\nDetailed Results:")
    for name, result in results:
        if result is True:
            print(f"  ✅ {name}: PASS")
        elif result == "ignored":
            print(f"  ⏭️  {name}: IGNORED (expected)")
        else:
            print(f"  ❌ {name}: FAIL")
    
    if failed == 0:
        print("\n✅ All webhook tests passed!")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Review errors above.")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
