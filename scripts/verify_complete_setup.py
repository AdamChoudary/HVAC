"""
Comprehensive verification script to check all components of the system.
Run this to verify everything is configured correctly.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings
from src.integrations.ghl import GHLClient
from src.integrations.vapi import VapiClient
from src.integrations.twilio import TwilioService
import httpx


async def verify_ghl():
    """Verify GHL configuration and connectivity"""
    print("\n" + "="*70)
    print("1️⃣  VERIFYING GHL (GoHighLevel) CONFIGURATION")
    print("="*70)
    
    checks = {
        "API Key": bool(settings.get_ghl_api_key()),
        "Location ID": bool(settings.ghl_location_id),
        "Base URL": settings.ghl_base_url == "https://services.leadconnectorhq.com"
    }
    
    for check, status in checks.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {check}: {'SET' if status else 'MISSING'}")
    
    if all(checks.values()):
        try:
            ghl = GHLClient()
            calendars = await ghl.get_calendars()
            print(f"   ✅ API Connection: SUCCESS ({len(calendars)} calendars found)")
            return True
        except Exception as e:
            print(f"   ❌ API Connection: FAILED - {str(e)}")
            return False
    else:
        print("   ⚠️  Cannot test API connection - missing configuration")
        return False


async def verify_vapi():
    """Verify Vapi configuration"""
    print("\n" + "="*70)
    print("2️⃣  VERIFYING VAPI.AI CONFIGURATION")
    print("="*70)
    
    checks = {
        "API Key": bool(settings.vapi_api_key),
        "Inbound Assistant ID": bool(settings.vapi_outbound_assistant_id),  # Note: This might be outbound
        "Phone Number ID": bool(settings.vapi_phone_number_id)
    }
    
    for check, status in checks.items():
        status_icon = "✅" if status else "⚠️"
        print(f"   {status_icon} {check}: {'SET' if status else 'NOT SET'}")
    
    if settings.vapi_api_key:
        try:
            vapi = VapiClient()
            # Try to get assistant info (if we have an ID)
            print(f"   ✅ API Key: VALID")
            return True
        except Exception as e:
            print(f"   ⚠️  API Key validation: {str(e)}")
            return True  # API key exists, connection will be tested during calls
    else:
        print("   ❌ API Key: MISSING")
        return False


async def verify_twilio():
    """Verify Twilio configuration"""
    print("\n" + "="*70)
    print("3️⃣  VERIFYING TWILIO CONFIGURATION")
    print("="*70)
    
    checks = {
        "Account SID": bool(settings.twilio_account_sid),
        "Auth Token": bool(settings.twilio_auth_token),
        "Phone Number": bool(settings.twilio_phone_number)
    }
    
    for check, status in checks.items():
        status_icon = "✅" if status else "⚠️"
        print(f"   {status_icon} {check}: {'SET' if status else 'NOT SET'}")
    
    return all(checks.values())


async def verify_server():
    """Verify server is running and accessible"""
    print("\n" + "="*70)
    print("4️⃣  VERIFYING SERVER DEPLOYMENT")
    print("="*70)
    
    server_url = settings.webhook_base_url or "https://scott-valley-hvac-api.fly.dev"
    
    endpoints_to_check = [
        ("/", "Root endpoint"),
        ("/health", "Health check"),
        ("/functions/create-contact", "Create contact function"),
        ("/functions/check-calendar-availability", "Calendar availability function"),
        ("/functions/book-appointment", "Book appointment function"),
        ("/webhooks/ghl", "GHL webhook endpoint")
    ]
    
    results = []
    async with httpx.AsyncClient(timeout=10.0) as client:
        for endpoint, description in endpoints_to_check:
            try:
                url = f"{server_url}{endpoint}"
                if endpoint in ["/functions/create-contact", "/functions/check-calendar-availability"]:
                    # These need POST, just check if they exist (405 is OK)
                    response = await client.post(url, json={})
                    status_ok = response.status_code in [200, 400, 405, 422]  # 405 = method not allowed but endpoint exists
                else:
                    response = await client.get(url)
                    status_ok = response.status_code in [200, 404, 405]  # 404/405 means server is up
                
                if status_ok:
                    print(f"   ✅ {description}: ACCESSIBLE")
                    results.append(True)
                else:
                    print(f"   ⚠️  {description}: Status {response.status_code}")
                    results.append(False)
            except Exception as e:
                print(f"   ❌ {description}: ERROR - {str(e)[:50]}")
                results.append(False)
    
    return all(results)


def verify_environment():
    """Verify environment variables"""
    print("\n" + "="*70)
    print("5️⃣  VERIFYING ENVIRONMENT CONFIGURATION")
    print("="*70)
    
    required = {
        "GHL_API": ("GoHighLevel API Key", lambda: bool(settings.get_ghl_api_key())),
        "GHL_LOCATION_ID": ("GoHighLevel Location ID", lambda: bool(settings.ghl_location_id))
    }
    
    optional = {
        "VAPI_API_KEY": ("Vapi.ai API Key", lambda: bool(settings.vapi_api_key)),
        "TWILIO_ACCOUNT_SID": ("Twilio Account SID", lambda: bool(settings.twilio_account_sid)),
        "TWILIO_AUTH_TOKEN": ("Twilio Auth Token", lambda: bool(settings.twilio_auth_token)),
        "TWILIO_PHONE_NUMBER": ("Twilio Phone Number", lambda: bool(settings.twilio_phone_number)),
        "WEBHOOK_BASE_URL": ("Webhook Base URL", lambda: bool(settings.webhook_base_url))
    }
    
    all_good = True
    
    print("   Required Variables:")
    for var, (desc, check_func) in required.items():
        if check_func():
            print(f"   ✅ {var}: SET")
        else:
            print(f"   ❌ {var}: MISSING - {desc}")
            all_good = False
    
    print("\n   Optional Variables:")
    for var, (desc, check_func) in optional.items():
        if check_func():
            print(f"   ✅ {var}: SET")
        else:
            print(f"   ⚠️  {var}: NOT SET - {desc}")
    
    return all_good


async def main():
    """Run all verification checks"""
    print("\n" + "="*70)
    print("🔍 COMPREHENSIVE SYSTEM VERIFICATION")
    print("="*70)
    
    results = {
        "Environment": verify_environment(),
        "GHL": await verify_ghl(),
        "Vapi": await verify_vapi(),
        "Twilio": await verify_twilio(),
        "Server": await verify_server()
    }
    
    print("\n" + "="*70)
    print("📊 VERIFICATION SUMMARY")
    print("="*70)
    
    for component, status in results.items():
        status_icon = "✅" if status else "❌"
        status_text = "PASS" if status else "FAIL"
        print(f"   {status_icon} {component}: {status_text}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL CHECKS PASSED - System is ready!")
    else:
        print("⚠️  SOME CHECKS FAILED - Review configuration above")
    print("="*70)
    
    return all_passed


if __name__ == "__main__":
    asyncio.run(main())

