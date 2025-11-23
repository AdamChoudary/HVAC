"""
Comprehensive testing and validation script for Scott Valley HVAC Voice Agent System.
Tests all functions, integrations, and configurations.
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings
from src.integrations.ghl import GHLClient
from src.integrations.vapi import VapiClient
from src.integrations.twilio import TwilioService
from src.utils.webhook_security import verify_ghl_webhook_signature
from src.utils.lead_scoring import calculate_lead_quality_score
from src.functions import (
    create_contact,
    check_calendar_availability,
    book_appointment,
    classify_call_type,
    send_confirmation,
    log_call_summary
)
from src.models import (
    CreateContactRequest,
    CheckCalendarAvailabilityRequest,
    BookAppointmentRequest,
    ClassifyCallTypeRequest,
    SendConfirmationRequest,
    LogCallSummaryRequest,
    ServiceType,
    CallType
)
from src.utils.logging import logger
import httpx


class TestResults:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
    
    def add_pass(self, test_name: str, details: str = ""):
        self.passed.append({"test": test_name, "details": details})
        print(f"✅ PASS - {test_name}")
        if details:
            print(f"   {details}")
    
    def add_fail(self, test_name: str, error: str):
        self.failed.append({"test": test_name, "error": error})
        print(f"❌ FAIL - {test_name}")
        print(f"   Error: {error}")
    
    def add_warning(self, test_name: str, message: str):
        self.warnings.append({"test": test_name, "message": message})
        print(f"⚠️  WARN - {test_name}")
        print(f"   {message}")
    
    def print_summary(self):
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"✅ Passed: {len(self.passed)}")
        print(f"❌ Failed: {len(self.failed)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        
        if self.failed:
            print("\n❌ FAILED TESTS:")
            for fail in self.failed:
                print(f"   - {fail['test']}: {fail['error']}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warn in self.warnings:
                print(f"   - {warn['test']}: {warn['message']}")


async def test_environment_variables(results: TestResults):
    """Test 1: Environment Variables"""
    print("\n" + "=" * 70)
    print("TEST 1: ENVIRONMENT VARIABLES")
    print("=" * 70)
    
    required_vars = {
        "GHL API Key": settings.get_ghl_api_key(),
        "GHL Location ID": settings.ghl_location_id,
        "Vapi API Key": settings.vapi_api_key,
        "Twilio Account SID": settings.get_twilio_account_sid(),
        "Twilio Auth Token": settings.twilio_auth_token,
        "Twilio Phone Number": settings.twilio_phone_number,
    }
    
    optional_vars = {
        "Webhook Secret": settings.webhook_secret,
        "Vapi Inbound Assistant ID": settings.vapi_inbound_assistant_id,
        "Vapi Outbound Assistant ID": settings.vapi_outbound_assistant_id,
    }
    
    all_passed = True
    for name, value in required_vars.items():
        if value:
            results.add_pass(f"{name} configured", "Set")
        else:
            results.add_fail(f"{name} configured", "NOT SET")
            all_passed = False
    
    for name, value in optional_vars.items():
        if value:
            results.add_pass(f"{name} configured", "Set")
        else:
            results.add_warning(f"{name} configured", "NOT SET (optional)")
    
    return all_passed


async def test_ghl_integration(results: TestResults):
    """Test 2: GHL API Integration"""
    print("\n" + "=" * 70)
    print("TEST 2: GHL API INTEGRATION")
    print("=" * 70)
    
    try:
        ghl = GHLClient()
        
        # Test calendars
        calendars = await ghl.get_calendars()
        if calendars:
            results.add_pass("GHL Calendars", f"Found {len(calendars)} calendars")
        else:
            results.add_warning("GHL Calendars", "No calendars found")
        
        # Test contact search
        test_contact = await ghl.get_contact(phone="+15551234567")
        results.add_pass("GHL Contact Search", "API working")
        
        return True
    except Exception as e:
        results.add_fail("GHL Integration", str(e))
        return False


async def test_vapi_integration(results: TestResults):
    """Test 3: Vapi API Integration"""
    print("\n" + "=" * 70)
    print("TEST 3: VAPI API INTEGRATION")
    print("=" * 70)
    
    try:
        vapi = VapiClient()
        
        # Test assistant retrieval
        if settings.vapi_inbound_assistant_id:
            assistant = await vapi.get_assistant(settings.vapi_inbound_assistant_id)
            results.add_pass("Vapi Inbound Assistant", f"Found: {assistant.get('name', 'N/A')}")
        else:
            results.add_warning("Vapi Inbound Assistant", "ID not configured")
        
        if settings.vapi_outbound_assistant_id:
            assistant = await vapi.get_assistant(settings.vapi_outbound_assistant_id)
            results.add_pass("Vapi Outbound Assistant", f"Found: {assistant.get('name', 'N/A')}")
        else:
            results.add_warning("Vapi Outbound Assistant", "ID not configured")
        
        return True
    except Exception as e:
        results.add_fail("Vapi Integration", str(e))
        return False


async def test_twilio_integration(results: TestResults):
    """Test 4: Twilio Integration"""
    print("\n" + "=" * 70)
    print("TEST 4: TWILIO INTEGRATION")
    print("=" * 70)
    
    try:
        twilio = TwilioService()
        if twilio.client and twilio.phone_number:
            results.add_pass("Twilio Client", f"Configured: {twilio.phone_number}")
        else:
            results.add_fail("Twilio Client", "Not properly configured")
            return False
        return True
    except Exception as e:
        results.add_fail("Twilio Integration", str(e))
        return False


async def test_api_functions(results: TestResults):
    """Test 5: API Functions"""
    print("\n" + "=" * 70)
    print("TEST 5: API FUNCTIONS")
    print("=" * 70)
    
    server_url = settings.webhook_base_url or "https://scott-valley-hvac-api.fly.dev"
    
    endpoints = [
        "/functions/classify-call-type",
        "/functions/check-calendar-availability",
        "/functions/book-appointment",
        "/functions/create-contact",
        "/functions/send-confirmation",
        "/functions/initiate-warm-transfer",
        "/functions/log-call-summary",
    ]
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for endpoint in endpoints:
            try:
                response = await client.post(
                    f"{server_url}{endpoint}",
                    json={}
                )
                # 422 is expected for validation errors (missing required fields)
                if response.status_code in [200, 422]:
                    results.add_pass(f"Endpoint: {endpoint}", f"Status: {response.status_code}")
                else:
                    results.add_fail(f"Endpoint: {endpoint}", f"Status: {response.status_code}")
            except Exception as e:
                results.add_fail(f"Endpoint: {endpoint}", str(e))


async def test_webhook_security(results: TestResults):
    """Test 6: Webhook Signature Verification"""
    print("\n" + "=" * 70)
    print("TEST 6: WEBHOOK SECURITY")
    print("=" * 70)
    
    if not settings.webhook_secret:
        results.add_warning("Webhook Signature", "WEBHOOK_SECRET not configured")
        return
    
    test_payload = b'{"test": "data"}'
    test_secret = "test_secret_123"
    
    # Test valid signature
    import hmac
    import hashlib
    expected_sig = hmac.new(
        test_secret.encode('utf-8'),
        test_payload,
        hashlib.sha256
    ).hexdigest()
    
    is_valid = verify_ghl_webhook_signature(test_payload, expected_sig, test_secret)
    if is_valid:
        results.add_pass("Webhook Signature Verification", "Valid signature accepted")
    else:
        results.add_fail("Webhook Signature Verification", "Valid signature rejected")
    
    # Test invalid signature
    is_invalid = verify_ghl_webhook_signature(test_payload, "invalid_signature", test_secret)
    if not is_invalid:
        results.add_pass("Webhook Signature Rejection", "Invalid signature rejected")
    else:
        results.add_fail("Webhook Signature Rejection", "Invalid signature accepted")


async def test_lead_scoring(results: TestResults):
    """Test 7: Lead Quality Scoring"""
    print("\n" + "=" * 70)
    print("TEST 7: LEAD QUALITY SCORING")
    print("=" * 70)
    
    # Test with complete contact
    complete_contact = {
        "firstName": "John",
        "lastName": "Doe",
        "phone": "+15551234567",
        "email": "john@example.com",
        "address1": "123 Main St",
        "customFields": {
            "urgency": "emergency",
            "lead_source": "referral"
        }
    }
    
    call_data = {
        "outcome": "booked",
        "call_duration": 300
    }
    
    score = calculate_lead_quality_score(complete_contact, call_data)
    if 0 <= score <= 100:
        results.add_pass("Lead Scoring Algorithm", f"Score: {score}/100")
    else:
        results.add_fail("Lead Scoring Algorithm", f"Invalid score: {score}")


async def test_monitoring_endpoints(results: TestResults):
    """Test 8: Monitoring Endpoints"""
    print("\n" + "=" * 70)
    print("TEST 8: MONITORING ENDPOINTS")
    print("=" * 70)
    
    server_url = settings.webhook_base_url or "https://scott-valley-hvac-api.fly.dev"
    
    endpoints = [
        "/monitoring/health",
        "/monitoring/metrics/overview",
        "/monitoring/metrics/calls",
        "/monitoring/metrics/bookings",
        "/monitoring/metrics/leads",
    ]
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for endpoint in endpoints:
            try:
                response = await client.get(f"{server_url}{endpoint}")
                if response.status_code == 200:
                    results.add_pass(f"Monitoring: {endpoint}", "Accessible")
                else:
                    results.add_warning(f"Monitoring: {endpoint}", f"Status: {response.status_code}")
            except Exception as e:
                results.add_warning(f"Monitoring: {endpoint}", str(e))


async def main():
    """Run all tests"""
    print("=" * 70)
    print("COMPREHENSIVE SYSTEM TESTING & VALIDATION")
    print("=" * 70)
    print(f"\nTest started at: {datetime.now().isoformat()}\n")
    
    results = TestResults()
    
    # Run all tests
    await test_environment_variables(results)
    await test_ghl_integration(results)
    await test_vapi_integration(results)
    await test_twilio_integration(results)
    await test_api_functions(results)
    await test_webhook_security(results)
    await test_lead_scoring(results)
    await test_monitoring_endpoints(results)
    
    # Print summary
    results.print_summary()
    
    # Exit code
    if results.failed:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())

