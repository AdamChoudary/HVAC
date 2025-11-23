"""
Diagnose why outbound calls aren't being triggered
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings
from src.integrations.ghl import GHLClient
from src.integrations.vapi import VapiClient
from src.utils.logging import logger

import logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


async def diagnose():
    """Diagnose outbound call issues"""
    print("\n" + "=" * 70)
    print("🔍 DIAGNOSING OUTBOUND CALL ISSUES")
    print("=" * 70)
    
    # Check 1: Environment Variables
    print("\n📋 Check 1: Environment Variables")
    print(f"   VAPI_API_KEY: {'SET' if settings.vapi_api_key else '❌ NOT SET'}")
    print(f"   VAPI_OUTBOUND_ASSISTANT_ID: {settings.vapi_outbound_assistant_id or '❌ NOT SET'}")
    print(f"   VAPI_PHONE_NUMBER_ID: {settings.vapi_phone_number_id or '⚠️  NOT SET (optional)'}")
    print(f"   GHL_LOCATION_ID: {settings.ghl_location_id or '❌ NOT SET'}")
    print(f"   GHL_API_KEY: {'SET' if settings.get_ghl_api_key() else '❌ NOT SET'}")
    
    # Check 2: Vapi API Connection
    print("\n📋 Check 2: Vapi API Connection")
    try:
        vapi = VapiClient()
        # Try to get assistants to test connection
        result = await vapi._request("GET", "assistant")
        print(f"   ✅ Vapi API connection works")
        print(f"      Found {len(result) if isinstance(result, list) else 'N/A'} assistants")
    except Exception as e:
        print(f"   ❌ Vapi API connection failed: {str(e)}")
        return
    
    # Check 3: Outbound Assistant
    print("\n📋 Check 3: Outbound Assistant")
    assistant_id = settings.vapi_outbound_assistant_id or "d6c74f74-de2a-420d-ae59-aab8fa7cbabe"
    try:
        assistant = await vapi.get_assistant(assistant_id)
        print(f"   ✅ Outbound assistant found")
        print(f"      ID: {assistant_id}")
        print(f"      Name: {assistant.get('name', 'N/A')}")
        print(f"      Status: {assistant.get('status', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Outbound assistant not found: {str(e)}")
        print(f"      Assistant ID: {assistant_id}")
        return
    
    # Check 4: Test Contact Retrieval
    print("\n📋 Check 4: Test Contact Retrieval")
    ghl = GHLClient()
    test_contact_id = "aSuWVXHgDqVSExXv1JcU"  # From previous test
    
    try:
        contact = await ghl.get_contact(contact_id=test_contact_id)
        if contact:
            phone = contact.get("phone", "")
            email = contact.get("email", "")
            custom_fields = contact.get("customFields", {})
            vapi_called = custom_fields.get("vapi_called", "")
            
            print(f"   ✅ Contact retrieved")
            print(f"      ID: {test_contact_id}")
            print(f"      Phone: {phone or '❌ NO PHONE'}")
            print(f"      Email: {email or 'N/A'}")
            print(f"      Vapi Called: {vapi_called or 'false'}")
            
            if not phone:
                print(f"\n   ⚠️  ISSUE: Contact has no phone number!")
                print(f"      Outbound calls require a phone number")
                return
            
            # Check 5: Simulate handle_new_lead logic
            print("\n📋 Check 5: Simulating handle_new_lead() logic")
            
            # Check if already called
            if vapi_called == "true":
                print(f"   ⚠️  Contact already marked as called - skipping")
                return
            
            # Check assistant ID
            if not assistant_id:
                print(f"   ❌ No assistant ID configured")
                return
            
            print(f"   ✅ All checks passed - should trigger call")
            print(f"      Assistant ID: {assistant_id}")
            print(f"      Phone: {phone}")
            
            # Check 6: Test Vapi Call Creation (dry run)
            print("\n📋 Check 6: Testing Vapi Call Creation (dry run)")
            call_config = {
                "assistantId": assistant_id,
                "customer": {
                    "number": phone
                }
            }
            
            if settings.vapi_phone_number_id:
                call_config["phoneNumberId"] = settings.vapi_phone_number_id
            
            print(f"   Call Config: {call_config}")
            print(f"\n   ⚠️  Note: Not actually creating call (dry run)")
            print(f"   To test actual call, uncomment the create_call line below")
            
            # Uncomment to actually test call creation:
            # try:
            #     call_result = await vapi.create_call(call_config)
            #     call_id = call_result.get("id", "")
            #     print(f"   ✅ Call created! ID: {call_id}")
            # except Exception as e:
            #     print(f"   ❌ Call creation failed: {str(e)}")
            
        else:
            print(f"   ❌ Contact not found")
    except Exception as e:
        print(f"   ❌ Error retrieving contact: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 DIAGNOSIS SUMMARY")
    print("=" * 70)
    print("\nMost likely issues:")
    print("1. VAPI_OUTBOUND_ASSISTANT_ID not set in .env")
    print("2. Contact has no phone number")
    print("3. Contact already marked as called")
    print("4. Vapi API call creation failed (check server logs)")
    print("\nTo fix:")
    print("1. Set VAPI_OUTBOUND_ASSISTANT_ID in .env")
    print("2. Ensure contacts have phone numbers")
    print("3. Check server logs for detailed error messages")
    print("4. Verify Vapi API key is valid")


if __name__ == "__main__":
    asyncio.run(diagnose())

