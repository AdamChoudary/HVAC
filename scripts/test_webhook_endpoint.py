"""
Test script to verify GHL webhook endpoint is working.
Simulates webhook calls from GHL to test the endpoint.
"""
import asyncio
import sys
import json
from pathlib import Path
import httpx

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings


async def test_webhook_endpoint():
    """Test the webhook endpoint with sample GHL payloads"""
    webhook_url = "https://scott-valley-hvac-api.fly.dev/webhooks/ghl"
    
    print("=" * 70)
    print("🧪 Testing GHL Webhook Endpoint")
    print("=" * 70)
    print(f"Webhook URL: {webhook_url}\n")
    
    # Test 1: Contact Created
    print("1️⃣  Testing: Contact Created Webhook")
    contact_created_payload = {
        "event": "contact.created",
        "locationId": "NHEXwG3xQVwKMO77jAuB",
        "contact": {
            "id": "test_contact_123",
            "firstName": "Test",
            "lastName": "Contact",
            "email": "test@example.com",
            "phone": "+15551234567"
        },
        "data": {
            "contact": {
                "id": "test_contact_123",
                "firstName": "Test",
                "lastName": "Contact",
                "email": "test@example.com",
                "phone": "+15551234567"
            }
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                webhook_url,
                json=contact_created_payload,
                headers={"Content-Type": "application/json"}
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Contact Created webhook working!")
            else:
                print(f"   ⚠️  Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print()
    
    # Test 2: Contact Updated
    print("2️⃣  Testing: Contact Updated Webhook")
    contact_updated_payload = {
        "event": "contact.updated",
        "locationId": "NHEXwG3xQVwKMO77jAuB",
        "contact": {
            "id": "test_contact_123",
            "firstName": "Test",
            "lastName": "Contact Updated",
            "email": "test@example.com",
            "phone": "+15551234567"
        },
        "data": {
            "contact": {
                "id": "test_contact_123",
                "firstName": "Test",
                "lastName": "Contact Updated"
            }
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                webhook_url,
                json=contact_updated_payload,
                headers={"Content-Type": "application/json"}
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Contact Updated webhook working!")
            else:
                print(f"   ⚠️  Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print()
    
    # Test 3: Appointment Created
    print("3️⃣  Testing: Appointment Created Webhook")
    appointment_created_payload = {
        "event": "appointment.created",
        "locationId": "NHEXwG3xQVwKMO77jAuB",
        "appointment": {
            "id": "test_appt_123",
            "title": "Test Appointment",
            "startTime": "2025-01-20T10:00:00Z",
            "endTime": "2025-01-20T11:00:00Z",
            "contactId": "test_contact_123"
        },
        "data": {
            "appointment": {
                "id": "test_appt_123",
                "title": "Test Appointment"
            }
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                webhook_url,
                json=appointment_created_payload,
                headers={"Content-Type": "application/json"}
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Appointment Created webhook working!")
            else:
                print(f"   ⚠️  Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print()
    
    # Test 4: Form Submitted
    print("4️⃣  Testing: Form Submitted Webhook")
    form_submitted_payload = {
        "event": "form.submitted",
        "locationId": "NHEXwG3xQVwKMO77jAuB",
        "form": {
            "id": "test_form_123",
            "name": "Contact Form"
        },
        "contact": {
            "id": "test_contact_123",
            "firstName": "Test",
            "lastName": "Form Submitter",
            "email": "form@example.com",
            "phone": "+15551234567"
        },
        "data": {
            "form": {
                "id": "test_form_123",
                "name": "Contact Form"
            },
            "contact": {
                "id": "test_contact_123",
                "firstName": "Test"
            }
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                webhook_url,
                json=form_submitted_payload,
                headers={"Content-Type": "application/json"}
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Form Submitted webhook working!")
            else:
                print(f"   ⚠️  Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print()
    print("=" * 70)
    print("✅ Webhook Testing Complete!")
    print("=" * 70)
    print("\n📝 Next Steps:")
    print("   1. Create a test contact in GHL to trigger 'Contact Created' webhook")
    print("   2. Update a contact to trigger 'Contact Updated' webhook")
    print("   3. Create an appointment to trigger 'Appointment Created' webhook")
    print("   4. Submit a form to trigger 'Form Submitted' webhook")
    print("\n💡 Check server logs to see webhook events:")
    print("   fly logs -a scott-valley-hvac-api")


if __name__ == "__main__":
    asyncio.run(test_webhook_endpoint())

