"""
Complete GoHighLevel CRM Setup Script
Automatically configures all GHL components using API.
Run this once to set up your entire GHL instance.
"""
import asyncio
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import httpx
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings
from src.utils.logging import logger


class CompleteGHLSetup:
    def __init__(self, api_key: str, location_id: str):
        self.api_key = api_key
        self.location_id = location_id
        self.base_url = "https://services.leadconnectorhq.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Version": "2021-07-28"
        }
        self.results = {
            "pipelines": {},
            "calendars": {},
            "custom_fields": {},
            "webhooks": {},
            "workflows": {},
            "errors": []
        }
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make API request with error handling"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
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
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            self.results["errors"].append(f"{endpoint}: {error_msg}")
            # Print error details for debugging
            if e.response.status_code == 422:
                try:
                    error_body = e.response.json()
                    print(f"      ⚠️  Validation error: {error_body}")
                except:
                    pass
            # Re-raise with response attached for custom handling
            e._response_text = e.response.text
            e._status_code = e.response.status_code
            raise
        except Exception as e:
            error_msg = f"Request failed: {str(e)}"
            self.results["errors"].append(f"{endpoint}: {error_msg}")
            raise
    
    async def setup_pipelines(self):
        """Verify existing pipelines (creation via API not supported)"""
        print("\n" + "="*60)
        print("📋 VERIFYING PIPELINES")
        print("="*60)
        print("  ⚠️  NOTE: Pipeline creation via API is not supported")
        print("  ⚠️  Error: 'This route is not yet supported by the IAM Service'")
        print("  ⚠️  Pipelines must be created manually in GHL UI")
        print()
        
        pipelines_config = [
            {
                "name": "Service Pipeline",
                "stages": [
                    {"name": "New Request", "order": 1},
                    {"name": "Scheduled", "order": 2},
                    {"name": "In Progress", "order": 3},
                    {"name": "Completed", "order": 4},
                    {"name": "Follow-up", "order": 5}
                ]
            },
            {
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
        ]
        
        # Get existing pipelines
        existing_pipelines = {}
        try:
            existing_data = await self._request("GET", "opportunities/pipelines", params={"locationId": self.location_id})
            existing_pipelines = {p.get("name"): p for p in existing_data.get("pipelines", [])}
            print(f"  ✓ Found {len(existing_pipelines)} existing pipeline(s)")
        except Exception as e:
            print(f"  ✗ Could not fetch pipelines: {str(e)}")
            return
        
        for pipeline_config in pipelines_config:
            pipeline_name = pipeline_config["name"]
            print(f"\n  Checking: {pipeline_name}")
            
            if pipeline_name in existing_pipelines:
                pipeline_id = existing_pipelines[pipeline_name].get("id")
                stages = existing_pipelines[pipeline_name].get("stages", [])
                print(f"    ✓ Exists (ID: {pipeline_id})")
                print(f"    ✓ Has {len(stages)} stage(s)")
                self.results["pipelines"][pipeline_name] = pipeline_id
            else:
                print(f"    ✗ Not found - Please create manually in GHL UI")
                print(f"    Required stages: {', '.join([s['name'] for s in pipeline_config['stages']])}")
    
    async def setup_calendars(self):
        """Verify existing calendars (creation via API format unclear)"""
        print("\n" + "="*60)
        print("📅 VERIFYING CALENDARS")
        print("="*60)
        
        calendars_config = [
            {
                "name": "Service Calendar",
                "description": "Calendar for repair and maintenance bookings",
                "timezone": "America/Los_Angeles",
                "appointmentDuration": 60,
                "appointmentBuffer": 15
            },
            {
                "name": "Sales/Estimate Calendar",
                "description": "Calendar for installation consultations and estimates",
                "timezone": "America/Los_Angeles",
                "appointmentDuration": 90,
                "appointmentBuffer": 15
            }
        ]
        
        # Get existing calendars
        existing_calendars = {}
        try:
            existing_data = await self._request("GET", "calendars/", params={"locationId": self.location_id})
            existing_calendars = {c.get("name"): c for c in existing_data.get("calendars", [])}
            print(f"  ✓ Found {len(existing_calendars)} existing calendar(s)")
        except Exception as e:
            print(f"  ✗ Could not fetch calendars: {str(e)}")
            return
        
        for calendar_config in calendars_config:
            calendar_name = calendar_config["name"]
            print(f"\n  Checking: {calendar_name}")
            
            # Check for partial matches (e.g., "Service" in name)
            found = False
            for existing_name, calendar_data in existing_calendars.items():
                if calendar_name.lower() in existing_name.lower() or existing_name.lower() in calendar_name.lower():
                    calendar_id = calendar_data.get("id")
                    print(f"    ✓ Found similar: '{existing_name}' (ID: {calendar_id})")
                    self.results["calendars"][calendar_name] = calendar_id
                    found = True
                    break
            
            if not found:
                print(f"    ⚠️  Not found - May need to create/rename manually in GHL UI")
                print(f"    Required settings:")
                print(f"      - Duration: {calendar_config['appointmentDuration']} minutes")
                print(f"      - Buffer: {calendar_config['appointmentBuffer']} minutes")
                print(f"      - Timezone: {calendar_config['timezone']}")
    
    async def setup_custom_fields(self):
        """Create all required custom fields"""
        print("\n" + "="*60)
        print("🏷️  SETTING UP CUSTOM FIELDS")
        print("="*60)
        
        custom_fields_config = [
            {"name": "AI Call Summary", "dataType": "LARGE_TEXT", "key": "ai_call_summary"},
            {"name": "Call Transcript URL", "dataType": "TEXT", "key": "call_transcript_url"},
            {"name": "SMS Consent", "dataType": "SINGLE_OPTIONS", "key": "sms_consent", 
             "options": [{"name": "Yes", "value": "true"}, {"name": "No", "value": "false"}]},
            {"name": "Lead Quality Score", "dataType": "NUMERICAL", "key": "lead_quality_score"},
            {"name": "Equipment Type", "dataType": "TEXT", "key": "equipment_type"},
            {"name": "Call Duration", "dataType": "NUMERICAL", "key": "call_duration"},
            {"name": "Call Type", "dataType": "SINGLE_OPTIONS", "key": "call_type",
             "options": [
                 {"name": "Service/Repair", "value": "service_repair"},
                 {"name": "Install/Estimate", "value": "install_estimate"},
                 {"name": "Maintenance", "value": "maintenance"},
                 {"name": "Appointment Change", "value": "appointment_change"},
                 {"name": "Other", "value": "other"}
             ]},
            {"name": "Call Outcome", "dataType": "TEXT", "key": "call_outcome"},
            {"name": "Vapi Called", "dataType": "SINGLE_OPTIONS", "key": "vapi_called",
             "options": [{"name": "Yes", "value": "true"}, {"name": "No", "value": "false"}]},
            {"name": "Vapi Call ID", "dataType": "TEXT", "key": "vapi_call_id"}
        ]
        
        # Get existing custom fields
        existing_fields = {}
        try:
            existing_data = await self._request("GET", f"locations/{self.location_id}/customFields/")
            # GHL uses fieldKey format like "contact.fieldKey", so we need to extract the key part
            for f in existing_data.get("customFields", []):
                field_key_full = f.get("fieldKey", "")
                # Extract key from "contact.key" format
                if "." in field_key_full:
                    key_part = field_key_full.split(".", 1)[1]
                    existing_fields[key_part] = f
                else:
                    existing_fields[field_key_full] = f
        except Exception as e:
            print(f"      ⚠️  Could not fetch existing fields: {str(e)}")
            existing_fields = {}
        
        for field_config in custom_fields_config:
            field_key = field_config["key"]
            field_name = field_config["name"]
            print(f"\n  Processing: {field_name} ({field_key})")
            
            try:
                if field_key in existing_fields:
                    field_id = existing_fields[field_key].get("id")
                    print(f"    ✓ Already exists (ID: {field_id})")
                    self.results["custom_fields"][field_key] = field_id
                else:
                    # Build payload according to GHL API format
                    # Note: locationId is in URL, not in payload
                    payload = {
                        "name": field_name,
                        "dataType": field_config["dataType"],
                        "fieldKey": f"contact.{field_key}",  # GHL uses contact.fieldKey format
                        "model": "contact",
                        "documentType": "field"
                    }
                    
                    # Add options for SINGLE_OPTIONS fields (GHL expects simple array of strings)
                    if "options" in field_config and field_config["dataType"] == "SINGLE_OPTIONS":
                        # Convert options to simple string array
                        options_list = []
                        for opt in field_config["options"]:
                            if isinstance(opt, dict):
                                # Use value if available, otherwise name
                                options_list.append(str(opt.get("value", opt.get("name", ""))))
                            else:
                                options_list.append(str(opt))
                        payload["options"] = options_list
                    
                    result = await self._request("POST", f"locations/{self.location_id}/customFields/", data=payload)
                    # Response structure: {"customField": {"id": ...}}
                    custom_field = result.get("customField", {})
                    field_id = custom_field.get("id") or result.get("id")
                    print(f"    ✓ Created (ID: {field_id})")
                    self.results["custom_fields"][field_key] = field_id
            except httpx.HTTPStatusError as e:
                # Check if field already exists (400 error with "already exists" message)
                response_text = e.response.text if hasattr(e, 'response') else str(e)
                if "already exists" in response_text.lower() or (e.response.status_code == 400 and "already exists" in response_text.lower()):
                    print(f"    ✓ Already exists")
                    # Get the existing field ID
                    try:
                        existing_data = await self._request("GET", f"locations/{self.location_id}/customFields/")
                        for f in existing_data.get("customFields", []):
                            field_key_full = f.get("fieldKey", "")
                            # Check if this field matches (handle contact.contact prefix)
                            if field_key in field_key_full or field_key_full.endswith(field_key) or f"contact{field_key}" in field_key_full:
                                field_id = f.get("id")
                                self.results["custom_fields"][field_key] = field_id
                                break
                    except:
                        pass
                else:
                    print(f"    ✗ Error: HTTP {e.response.status_code} - {response_text[:100]}")
            except Exception as e:
                error_str = str(e)
                print(f"    ✗ Error: {error_str}")
    
    async def setup_webhooks(self, webhook_url: str):
        """Webhook configuration instructions (API not available)"""
        print("\n" + "="*60)
        print("🔗 WEBHOOK CONFIGURATION")
        print("="*60)
        print("  ⚠️  NOTE: Webhook creation via API is NOT available")
        print("  ⚠️  All webhook endpoints return 404 Not Found")
        print("  ⚠️  Webhooks must be configured manually in GHL Settings")
        print()
        
        if not webhook_url:
            print("  ⚠️  No webhook URL provided")
            print("  📝 To configure webhooks manually:")
        else:
            print(f"  📝 Configure webhook manually in GHL:")
            print(f"     URL: {webhook_url}")
        
        webhook_events = [
            "contact.created",
            "contact.updated",
            "appointment.created",
            "form.submitted"
        ]
        
        print(f"     Events: {', '.join(webhook_events)}")
        print()
        print("  📋 Steps to configure in GHL UI:")
        print("     1. Go to Settings → Integrations → Webhooks")
        print("     2. Click 'Add Webhook'")
        print(f"     3. Enter URL: {webhook_url if webhook_url else 'YOUR_WEBHOOK_URL'}")
        print(f"     4. Select events: {', '.join(webhook_events)}")
        print("     5. Save webhook")
        print()
        
        # Note: We can't verify webhooks via API either
        self.results["webhooks"] = {
            "status": "manual_configuration_required",
            "url": webhook_url,
            "events": webhook_events
        }
    
    async def setup_workflows(self):
        """List existing workflows (automations)"""
        print("\n" + "="*60)
        print("⚙️  VERIFYING WORKFLOWS (AUTOMATIONS)")
        print("="*60)
        print("  ℹ️  Workflows are GHL's automation system")
        print("  ℹ️  Workflow creation via API requires complex payload structure")
        print("  ℹ️  Recommended: Create automations manually in GHL UI")
        print()
        
        try:
            existing_data = await self._request("GET", "workflows/", params={"locationId": self.location_id})
            workflows = existing_data.get("workflows", [])
            print(f"  ✓ Found {len(workflows)} existing workflow(s)")
            
            if workflows:
                print("\n  Existing workflows:")
                for wf in workflows[:5]:  # Show first 5
                    status_icon = "✅" if wf.get("status") == "active" else "📝"
                    print(f"    {status_icon} {wf.get('name')} ({wf.get('status', 'unknown')})")
                if len(workflows) > 5:
                    print(f"    ... and {len(workflows) - 5} more")
            
            self.results["workflows"] = {
                "count": len(workflows),
                "note": "Create automations manually in GHL UI for SMS/email confirmations"
            }
        except Exception as e:
            print(f"  ✗ Could not fetch workflows: {str(e)}")
            self.results["workflows"] = {"error": str(e)}
    
    async def run_complete_setup(self, webhook_url: Optional[str] = None):
        """Run all setup steps"""
        print("\n" + "="*60)
        print("🚀 GO HIGH LEVEL CRM COMPLETE SETUP")
        print("="*60)
        print(f"Location ID: {self.location_id}")
        print(f"API Key: {self.api_key[:10]}...{self.api_key[-4:]}")
        print("="*60)
        
        await self.setup_pipelines()
        await self.setup_calendars()
        await self.setup_custom_fields()
        await self.setup_webhooks(webhook_url)
        await self.setup_workflows()
        
        # Print summary
        print("\n" + "="*60)
        print("✅ SETUP COMPLETE!")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"  Pipelines: {len(self.results['pipelines'])} verified")
        print(f"  Calendars: {len(self.results['calendars'])} verified")
        print(f"  Custom Fields: {len(self.results['custom_fields'])} created/verified")
        print(f"  Webhooks: {'Manual config required' if self.results.get('webhooks', {}).get('status') == 'manual_configuration_required' else '0'}")
        print(f"  Workflows: {self.results.get('workflows', {}).get('count', 0)} found")
        
        if self.results["errors"]:
            print(f"\n⚠️  Errors encountered: {len(self.results['errors'])}")
            for error in self.results["errors"]:
                print(f"  - {error}")
        
        # Save configuration
        config_file = Path(__file__).parent.parent / "ghl_setup_config.json"
        with open(config_file, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Configuration saved to: {config_file}")
        
        return self.results


async def main():
    """Main entry point"""
    api_key = settings.get_ghl_api_key()
    if not api_key:
        print("❌ Error: GHL_API or GHL_API_KEY not found in .env file")
        print("   Please set GHL_API=your_api_key in .env")
        sys.exit(1)
    
    location_id = settings.ghl_location_id
    if not location_id:
        print("❌ Error: GHL_LOCATION_ID not found in .env file")
        sys.exit(1)
    
    webhook_url = settings.webhook_base_url
    if not webhook_url:
        webhook_url = input("\nEnter your webhook URL (or press Enter to skip): ").strip()
        if not webhook_url:
            webhook_url = None
    
    setup = CompleteGHLSetup(api_key, location_id)
    await setup.run_complete_setup(webhook_url)


if __name__ == "__main__":
    asyncio.run(main())

