"""
Test the complete outbound call flow with a real contact
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from src.config import settings
from src.integrations.ghl import GHLClient
from src.utils.logging import logger

# Suppress debug logs
import logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


async def test_complete_outbound_flow():
    """Test complete outbound call flow"""
    print("\n" + "=" * 70)
    print("🧪 TESTING COMPLETE OUTBOUND CALL FLOW")
    print("=" * 70)
    
    server_url = settings.webhook_base_url or "https://scott-valley-hvac-api.fly.dev"
    webhook_url = f"{server_url}/webhooks/ghl"
    
    ghl = GHLClient()
    
    # Step 1: Create a test contact
    print("\n📋 Step 1: Creating test contact...")
    test_phone = f"+1555{datetime.now().strftime('%H%M%S')}"
    test_email = f"test{datetime.now().strftime('%H%M%S')}@test.com"
    
    contact_data = {
        "firstName": "Test",
        "lastName": f"Outbound{datetime.now().strftime('%H%M%S')}",
        "phone": test_phone,
        "email": test_email,
        "address1": "123 Test St",
        "postalCode": "12345"
    }
    
    try:
        contact_result = await ghl.create_contact(contact_data)
        
        # Extract contact ID
        if isinstance(contact_result, dict):
            contact_id = contact_result.get("id") or contact_result.get("contact", {}).get("id", "")
        else:
            contact_id = ""
        
        if not contact_id:
            print("   ❌ FAIL - Could not create test contact")
            return
        
        print(f"   ✅ Created contact: {contact_id}")
        print(f"      Phone: {test_phone}")
        print(f"      Email: {test_email}")
        
        # Step 2: Simulate webhook for contact.created
        print("\n📋 Step 2: Simulating GHL webhook (contact.created)...")
        
        webhook_payload = {
            "type": "contact.created",
            "locationId": settings.ghl_location_id,
            "contactId": contact_id
        }
        
        print(f"   Webhook URL: {webhook_url}")
        print(f"   Payload: {json.dumps(webhook_payload, indent=2)}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                webhook_url,
                json=webhook_payload,
                headers={"Content-Type": "application/json"}
            )
            
            result = response.json() if response.status_code == 200 else response.text
            
            if response.status_code == 200:
                status = result.get("status", "unknown")
                if status == "ok":
                    print(f"   ✅ Webhook received and processed")
                    print(f"      Status: {status}")
                    print(f"      Event: {result.get('event')}")
                else:
                    print(f"   ⚠️  Webhook status: {status}")
                    print(f"      Response: {result}")
            else:
                print(f"   ❌ Webhook failed - Status: {response.status_code}")
                print(f"      Response: {result}")
                return
        
        # Step 3: Check if contact was marked as called
        print("\n📋 Step 3: Verifying contact was processed...")
        await asyncio.sleep(2)  # Wait a moment for processing
        
        contact = await ghl.get_contact(contact_id=contact_id)
        if contact:
            custom_fields = contact.get("customFields", {})
            vapi_called = custom_fields.get("vapi_called", "")
            vapi_call_id = custom_fields.get("vapi_call_id", "")
            
            if vapi_called == "true":
                print(f"   ✅ Contact marked as called")
                print(f"      Vapi Call ID: {vapi_call_id}")
                print(f"      Note: Outbound call should have been initiated via Vapi")
            else:
                print(f"   ⚠️  Contact not marked as called")
                print(f"      This could mean:")
                print(f"      - Contact has no phone number")
                print(f"      - Contact was already called")
                print(f"      - Vapi call creation failed")
                print(f"      - VAPI_OUTBOUND_ASSISTANT_ID not set")
        else:
            print(f"   ⚠️  Could not retrieve contact to verify")
        
        # Step 4: Summary
        print("\n📋 Step 4: Summary")
        print(f"   Contact ID: {contact_id}")
        print(f"   Phone: {test_phone}")
        print(f"   Webhook Status: {status if response.status_code == 200 else 'FAILED'}")
        print(f"\n   ✅ Test completed!")
        print(f"   Check Vapi dashboard to see if outbound call was created")
        print(f"   Check server logs for detailed processing information")
        
    except Exception as e:
        print(f"   ❌ ERROR - {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import json
    asyncio.run(test_complete_outbound_flow())

