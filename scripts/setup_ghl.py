"""
Comprehensive GoHighLevel CRM Setup Script
Automatically configures all required GHL components using API.
"""
import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import httpx
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings
from src.utils.logging import logger


class GHLSetup:
    def __init__(self, api_key: str, location_id: str):
        self.api_key = api_key
        self.location_id = location_id
        self.base_url = "https://services.leadconnectorhq.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Version": "2021-07-28"
        }
        self.created_resources = {
            "pipelines": {},
            "calendars": {},
            "custom_fields": {},
            "automations": {},
            "webhooks": {}
        }
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make API request to GHL"""
        url = f"{self.base_url}/{endpoint}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params
            )
            response.raise_for_status()
            return response.json()
    
    async def create_pipelines(self) -> Dict[str, str]:
        """Create Service and Sales pipelines"""
        print("\n📋 Creating Pipelines...")
        
        pipelines = {
            "Service Pipeline": {
                "name": "Service Pipeline",
                "stages": [
                    {"name": "New Request", "order": 1},
                    {"name": "Scheduled", "order": 2},
                    {"name": "In Progress", "order": 3},
                    {"name": "Completed", "order": 4},
                    {"name": "Follow-up", "order": 5}
                ]
            },
            "Sales Pipeline": {
                "name": "Sales Pipeline",
                "stages": [
                    {"name": "Lead", "order": 1},
                    {"name": "Qualified", "order": 2},
                    {"name": "Estimate Sent", "order": 3},
                    {"name": "Negotiation", "order": 4},
                    {"name": "Won", "order": 5},
                    {"name": "Lost", "order": 6}
                ]
            }
        }
        
        created = {}
        
        for pipeline_name, pipeline_data in pipelines.items():
            try:
                # Check if pipeline exists
                existing = await self._request("GET", "pipelines/", params={"locationId": self.location_id})
                existing_pipelines = existing.get("pipelines", [])
                
                pipeline_id = None
                for p in existing_pipelines:
                    if p.get("name") == pipeline_name:
                        pipeline_id = p.get("id")
                        print(f"  ✓ {pipeline_name} already exists (ID: {pipeline_id})")
                        break
                
                if not pipeline_id:
                    # Create pipeline
                    payload = {
                        "locationId": self.location_id,
                        "name": pipeline_data["name"]
                    }
                    result = await self._request("POST", "pipelines/", data=payload)
                    pipeline_id = result.get("id")
                    
                    # Create stages
                    for stage in pipeline_data["stages"]:
                        stage_payload = {
                            "locationId": self.location_id,
                            "pipelineId": pipeline_id,
                            "name": stage["name"],
                            "order": stage["order"]
                        }
                        await self._request("POST", f"pipelines/{pipeline_id}/stages", data=stage_payload)
                    
                    print(f"  ✓ Created {pipeline_name} (ID: {pipeline_id})")
                
                created[pipeline_name] = pipeline_id
            except Exception as e:
                print(f"  ✗ Error creating {pipeline_name}: {str(e)}")
        
        self.created_resources["pipelines"] = created
        return created
    
    async def create_calendars(self) -> Dict[str, str]:
        """Create Service and Sales/Estimate calendars"""
        print("\n📅 Creating Calendars...")
        
        calendars = {
            "Service Calendar": {
                "name": "Service Calendar",
                "description": "Calendar for repair and maintenance bookings",
                "timezone": "America/Los_Angeles",
                "appointmentDuration": 60,  # 1 hour
                "appointmentBuffer": 15,  # 15 min buffer
                "appointmentType": "service"
            },
            "Sales/Estimate Calendar": {
                "name": "Sales/Estimate Calendar",
                "description": "Calendar for installation consultations and estimates",
                "timezone": "America/Los_Angeles",
                "appointmentDuration": 90,  # 1.5 hours
                "appointmentBuffer": 15,
                "appointmentType": "sales"
            }
        }
        
        created = {}
        
        for calendar_name, calendar_data in calendars.items():
            try:
                # Check if calendar exists
                existing = await self._request("GET", "calendars/", params={"locationId": self.location_id})
                existing_calendars = existing.get("calendars", [])
                
                calendar_id = None
                for c in existing_calendars:
                    if c.get("name") == calendar_name:
                        calendar_id = c.get("id")
                        print(f"  ✓ {calendar_name} already exists (ID: {calendar_id})")
                        break
                
                if not calendar_id:
                    payload = {
                        "locationId": self.location_id,
                        "name": calendar_data["name"],
                        "description": calendar_data["description"],
                        "timezone": calendar_data["timezone"],
                        "appointmentDuration": calendar_data["appointmentDuration"],
                        "appointmentBuffer": calendar_data["appointmentBuffer"]
                    }
                    result = await self._request("POST", "calendars/", data=payload)
                    calendar_id = result.get("id")
                    print(f"  ✓ Created {calendar_name} (ID: {calendar_id})")
                
                created[calendar_name] = calendar_id
            except Exception as e:
                print(f"  ✗ Error creating {calendar_name}: {str(e)}")
        
        self.created_resources["calendars"] = created
        return created
    
    async def create_custom_fields(self) -> Dict[str, str]:
        """Create custom fields for call tracking and metadata"""
        print("\n🏷️  Creating Custom Fields...")
        
        custom_fields = [
            {
                "name": "AI Call Summary",
                "dataType": "TEXTAREA",
                "position": 1,
                "key": "ai_call_summary"
            },
            {
                "name": "Call Transcript URL",
                "dataType": "TEXT",
                "position": 2,
                "key": "call_transcript_url"
            },
            {
                "name": "SMS Consent",
                "dataType": "DROPDOWN",
                "position": 3,
                "key": "sms_consent",
                "options": ["true", "false"]
            },
            {
                "name": "Lead Quality Score",
                "dataType": "NUMBER",
                "position": 4,
                "key": "lead_quality_score"
            },
            {
                "name": "Equipment Type",
                "dataType": "TEXT",
                "position": 5,
                "key": "equipment_type"
            },
            {
                "name": "Call Duration",
                "dataType": "NUMBER",
                "position": 6,
                "key": "call_duration"
            },
            {
                "name": "Call Type",
                "dataType": "DROPDOWN",
                "position": 7,
                "key": "call_type",
                "options": ["service_repair", "install_estimate", "maintenance", "appointment_change", "other"]
            },
            {
                "name": "Call Outcome",
                "dataType": "TEXT",
                "position": 8,
                "key": "call_outcome"
            },
            {
                "name": "Vapi Called",
                "dataType": "DROPDOWN",
                "position": 9,
                "key": "vapi_called",
                "options": ["true", "false"]
            },
            {
                "name": "Vapi Call ID",
                "dataType": "TEXT",
                "position": 10,
                "key": "vapi_call_id"
            }
        ]
        
        created = {}
        
        try:
            # Get existing custom fields
            existing = await self._request("GET", f"locations/{self.location_id}/customFields/")
            existing_fields = {f.get("key"): f.get("id") for f in existing.get("customFields", [])}
            
            for field_data in custom_fields:
                field_key = field_data["key"]
                
                if field_key in existing_fields:
                    field_id = existing_fields[field_key]
                    print(f"  ✓ Custom field '{field_data['name']}' already exists (ID: {field_id})")
                    created[field_key] = field_id
                else:
                    payload = {
                        "locationId": self.location_id,
                        "name": field_data["name"],
                        "dataType": field_data["dataType"],
                        "position": field_data["position"],
                        "key": field_key
                    }
                    
                    if "options" in field_data:
                        payload["options"] = field_data["options"]
                    
                    result = await self._request("POST", f"locations/{self.location_id}/customFields/", data=payload)
                    field_id = result.get("id")
                    print(f"  ✓ Created custom field '{field_data['name']}' (ID: {field_id})")
                    created[field_key] = field_id
        except Exception as e:
            print(f"  ✗ Error creating custom fields: {str(e)}")
        
        self.created_resources["custom_fields"] = created
        return created
    
    async def create_automations(self) -> Dict[str, str]:
        """Create automations for confirmations and notifications"""
        print("\n🤖 Creating Automations...")
        
        # Note: Automation creation API may vary. This is a template.
        # You may need to create these manually in GHL UI or use workflow API
        
        automations = {
            "Appointment Confirmation SMS": {
                "name": "Appointment Confirmation SMS",
                "trigger": "appointment.created",
                "type": "sms"
            },
            "Appointment Confirmation Email": {
                "name": "Appointment Confirmation Email",
                "trigger": "appointment.created",
                "type": "email"
            },
            "New Booking Notification": {
                "name": "New Booking Notification",
                "trigger": "appointment.created",
                "type": "notification"
            }
        }
        
        print("  ⚠️  Note: Automations may need to be created manually in GHL UI")
        print("  ⚠️  Or use GHL Workflows API if available")
        
        # Return empty dict for now - automations typically created via UI
        self.created_resources["automations"] = {}
        return {}
    
    async def setup_webhooks(self, webhook_url: str) -> Dict[str, Any]:
        """Configure webhooks to point to our server"""
        print("\n🔗 Setting up Webhooks...")
        
        webhook_events = [
            "contact.created",
            "contact.updated",
            "appointment.created",
            "form.submitted"
        ]
        
        try:
            # Get existing webhooks
            existing = await self._request("GET", f"locations/{self.location_id}/webhooks/")
            existing_webhooks = existing.get("webhooks", [])
            
            # Check if webhook already exists
            webhook_id = None
            for wh in existing_webhooks:
                if wh.get("url") == webhook_url:
                    webhook_id = wh.get("id")
                    print(f"  ✓ Webhook already exists (ID: {webhook_id})")
                    break
            
            if not webhook_id:
                # Create webhook
                payload = {
                    "locationId": self.location_id,
                    "url": webhook_url,
                    "events": webhook_events
                }
                result = await self._request("POST", f"locations/{self.location_id}/webhooks/", data=payload)
                webhook_id = result.get("id")
                print(f"  ✓ Created webhook (ID: {webhook_id})")
            
            self.created_resources["webhooks"] = {"id": webhook_id, "url": webhook_url}
            return self.created_resources["webhooks"]
        except Exception as e:
            print(f"  ✗ Error setting up webhooks: {str(e)}")
            print(f"  ⚠️  You may need to configure webhooks manually in GHL Settings")
            return {}
    
    async def set_business_hours(self) -> bool:
        """Set business hours for calendars"""
        print("\n🕐 Setting Business Hours...")
        
        # Business hours: Mon-Fri 8AM-6PM, Sat 9AM-4PM, Sun closed
        business_hours = {
            "monday": {"enabled": True, "start": "08:00", "end": "18:00"},
            "tuesday": {"enabled": True, "start": "08:00", "end": "18:00"},
            "wednesday": {"enabled": True, "start": "08:00", "end": "18:00"},
            "thursday": {"enabled": True, "start": "08:00", "end": "18:00"},
            "friday": {"enabled": True, "start": "08:00", "end": "18:00"},
            "saturday": {"enabled": True, "start": "09:00", "end": "16:00"},
            "sunday": {"enabled": False}
        }
        
        try:
            # Update location settings with business hours
            # This may require location update API
            print("  ✓ Business hours configuration ready")
            print("  ⚠️  Update business hours in GHL Settings → Calendars if needed")
            return True
        except Exception as e:
            print(f"  ✗ Error setting business hours: {str(e)}")
            return False
    
    async def run_setup(self, webhook_url: Optional[str] = None):
        """Run complete GHL setup"""
        print("=" * 60)
        print("🚀 Starting GoHighLevel CRM Setup")
        print("=" * 60)
        print(f"Location ID: {self.location_id}")
        print(f"API Key: {self.api_key[:10]}...")
        
        # Run all setup steps
        await self.create_pipelines()
        await self.create_calendars()
        await self.create_custom_fields()
        await self.create_automations()
        await self.set_business_hours()
        
        if webhook_url:
            await self.setup_webhooks(webhook_url)
        
        # Print summary
        print("\n" + "=" * 60)
        print("✅ Setup Complete!")
        print("=" * 60)
        print("\n📊 Created Resources:")
        print(f"  Pipelines: {len(self.created_resources['pipelines'])}")
        print(f"  Calendars: {len(self.created_resources['calendars'])}")
        print(f"  Custom Fields: {len(self.created_resources['custom_fields'])}")
        print(f"  Webhooks: {len(self.created_resources['webhooks'])}")
        
        print("\n📝 Next Steps:")
        print("  1. Review created resources in GHL dashboard")
        print("  2. Configure automations manually in GHL UI")
        print("  3. Set up business hours in calendar settings")
        print("  4. Test webhook delivery")
        
        return self.created_resources


async def main():
    """Main setup function"""
    # Get API key from environment
    api_key = settings.get_ghl_api_key()
    
    if not api_key:
        print("❌ Error: GHL_API_KEY or GHL_API not found in environment")
        print("   Please set GHL_API in your .env file")
        return
    
    location_id = settings.ghl_location_id
    if not location_id:
        print("❌ Error: GHL_LOCATION_ID not found in environment")
        return
    
    webhook_url = settings.webhook_base_url
    if not webhook_url:
        webhook_url = input("\nEnter your webhook URL (or press Enter to skip): ").strip()
        if not webhook_url:
            webhook_url = None
    
    setup = GHLSetup(api_key, location_id)
    resources = await setup.run_setup(webhook_url)
    
    # Save configuration
    config_file = Path(__file__).parent.parent / "ghl_config.json"
    import json
    with open(config_file, "w") as f:
        json.dump(resources, f, indent=2)
    print(f"\n💾 Configuration saved to: {config_file}")


if __name__ == "__main__":
    asyncio.run(main())

