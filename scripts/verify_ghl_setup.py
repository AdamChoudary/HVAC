"""
Verify GoHighLevel setup and display current configuration.
"""
import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List
import httpx

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings


class GHLVerifier:
    def __init__(self, api_key: str, location_id: str):
        self.api_key = api_key
        self.location_id = location_id
        self.base_url = "https://services.leadconnectorhq.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Version": "2021-07-28"
        }
    
    async def _request(self, method: str, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
    
    async def verify_pipelines(self) -> List[Dict[str, Any]]:
        """Get all pipelines"""
        # Correct endpoint: /opportunities/pipelines?locationId={locationId}
        try:
            result = await self._request("GET", "opportunities/pipelines", params={"locationId": self.location_id})
            return result.get("pipelines", [])
        except Exception as e:
            print(f"      ⚠️  Error fetching pipelines: {str(e)}")
            return []
    
    async def verify_calendars(self) -> List[Dict[str, Any]]:
        """Get all calendars"""
        try:
            result = await self._request("GET", f"locations/{self.location_id}/calendars/")
            return result.get("calendars", [])
        except:
            # Try alternative endpoint
            try:
                result = await self._request("GET", "calendars/", params={"locationId": self.location_id})
                return result.get("calendars", [])
            except:
                return []
    
    async def verify_custom_fields(self) -> List[Dict[str, Any]]:
        """Get all custom fields"""
        result = await self._request("GET", f"locations/{self.location_id}/customFields/")
        return result.get("customFields", [])
    
    async def verify_webhooks(self) -> List[Dict[str, Any]]:
        """Get all webhooks"""
        try:
            result = await self._request("GET", f"locations/{self.location_id}/webhooks/")
            return result.get("webhooks", [])
        except:
            try:
                result = await self._request("GET", "webhooks/", params={"locationId": self.location_id})
                return result.get("webhooks", [])
            except:
                return []
    
    async def verify_setup(self):
        """Verify complete setup"""
        print("=" * 60)
        print("🔍 Verifying GoHighLevel Setup")
        print("=" * 60)
        print(f"Location ID: {self.location_id}\n")
        
        # Check pipelines
        print("📋 Pipelines:")
        pipelines = await self.verify_pipelines()
        if pipelines:
            for p in pipelines:
                print(f"  ✓ {p.get('name')} (ID: {p.get('id')})")
        else:
            print("  ✗ No pipelines found")
        
        # Check calendars
        print("\n📅 Calendars:")
        calendars = await self.verify_calendars()
        if calendars:
            for c in calendars:
                print(f"  ✓ {c.get('name')} (ID: {c.get('id')})")
        else:
            print("  ✗ No calendars found")
        
        # Check custom fields
        print("\n🏷️  Custom Fields:")
        custom_fields = await self.verify_custom_fields()
        required_fields = [
            "ai_call_summary",
            "call_transcript_url",
            "sms_consent",
            "lead_quality_score",
            "equipment_type",
            "call_duration",
            "call_type",
            "call_outcome",
            "vapi_called",
            "vapi_call_id"
        ]
        
        # GHL fieldKey format is "contact.fieldKey" or "contact.contactfieldKey"
        existing_keys = {}
        for f in custom_fields:
            field_key_full = f.get("fieldKey", "")
            name = f.get("name", "")
            # Extract key part from "contact.key" format
            if "." in field_key_full:
                key_part = field_key_full.split(".", 1)[1]
                # Remove "contact" prefix if it exists (GHL sometimes adds it)
                if key_part.startswith("contact"):
                    key_part = key_part[7:]  # Remove "contact" prefix
                existing_keys[key_part] = name
        
        for key in required_fields:
            if key in existing_keys:
                print(f"  ✓ {existing_keys[key]} ({key})")
            else:
                # Try partial match (GHL might have added "contact" prefix)
                found = False
                for existing_key, name in existing_keys.items():
                    if key in existing_key or existing_key.endswith(key):
                        print(f"  ✓ {name} (found as: {existing_key})")
                        found = True
                        break
                if not found:
                    print(f"  ✗ Missing: {key}")
        
        # Check webhooks
        print("\n🔗 Webhooks:")
        webhooks = await self.verify_webhooks()
        if webhooks:
            for wh in webhooks:
                events = ", ".join(wh.get("events", []))
                print(f"  ✓ {wh.get('url')} - Events: {events}")
        else:
            print("  ✗ No webhooks configured")
        
        print("\n" + "=" * 60)


async def main():
    api_key = settings.get_ghl_api_key()
    if not api_key:
        print("❌ Error: GHL_API not found in environment")
        return
    
    location_id = settings.ghl_location_id
    if not location_id:
        print("❌ Error: GHL_LOCATION_ID not found")
        return
    
    verifier = GHLVerifier(api_key, location_id)
    await verifier.verify_setup()


if __name__ == "__main__":
    asyncio.run(main())

