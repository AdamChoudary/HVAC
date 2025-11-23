"""
Script to create all required GHL custom fields via API.
This script creates all 14 custom fields needed for the Scott Valley HVAC Voice Agent system.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.integrations.ghl import GHLClient
from src.utils.logging import logger


# Define all custom fields to create
CUSTOM_FIELDS = [
    {
        "name": "AI Call Summary",
        "key": "ai_call_summary",
        "type": "textarea",  # Long text
        "description": "Stores AI-generated call summary"
    },
    {
        "name": "Call Transcript URL",
        "key": "call_transcript_url",
        "type": "url",  # URL field
        "description": "URL to full call transcript (if stored externally)"
    },
    {
        "name": "SMS Consent",
        "key": "sms_consent",
        "type": "checkbox",  # Yes/No checkbox
        "description": "Tracks whether contact has given SMS consent (TCPA compliance)"
    },
    {
        "name": "Lead Quality Score",
        "key": "lead_quality_score",
        "type": "number",  # Number field (0-100)
        "description": "Calculated lead quality score based on multiple factors"
    },
    {
        "name": "Equipment Type Tags",
        "key": "equipment_type_tags",
        "type": "text",  # Text field (comma-separated)
        "description": "Stores detected equipment types from conversation (furnace, AC, heat pump, etc.)"
    },
    {
        "name": "Call Duration Seconds",
        "key": "call_duration",
        "type": "number",  # Number field (seconds)
        "description": "Duration of the call in seconds"
    },
    {
        "name": "Call Type",
        "key": "call_type",
        "type": "dropdown",  # Dropdown with options
        "options": [
            "service_repair",
            "installation_estimate",
            "maintenance",
            "appointment_change",
            "other"
        ],
        "description": "Classified call type"
    },
    {
        "name": "Call Outcome",
        "key": "call_outcome",
        "type": "dropdown",  # Dropdown with options
        "options": [
            "booked",
            "transferred",
            "no_booking",
            "interested",
            "callback_scheduled",
            "declined",
            "no_answer",
            "voicemail"
        ],
        "description": "Outcome of the call"
    },
    {
        "name": "VAPI Called",
        "key": "vapi_called",
        "type": "checkbox",  # Yes/No checkbox
        "description": "Tracks if outbound call has been made to this contact"
    },
    {
        "name": "VAPI Call ID",
        "key": "vapi_call_id",
        "type": "text",  # Text field
        "description": "Stores Vapi call ID for tracking"
    },
    {
        "name": "Lead Source",
        "key": "lead_source",
        "type": "dropdown",  # Dropdown with options
        "options": [
            "form",
            "webchat",
            "google_ads",
            "meta_ads",
            "facebook_ads",
            "referral",
            "website",
            "other"
        ],
        "description": "Source of the lead"
    },
    {
        "name": "SMS Fallback Sent",
        "key": "sms_fallback_sent",
        "type": "checkbox",  # Yes/No checkbox
        "description": "Tracks if SMS fallback was sent after failed call"
    },
    {
        "name": "SMS Fallback Date",
        "key": "sms_fallback_date",
        "type": "date",  # Date/Time field
        "description": "Timestamp when SMS fallback was sent"
    },
    {
        "name": "SMS Fallback Reason",
        "key": "sms_fallback_reason",
        "type": "text",  # Text field
        "description": "Reason for SMS fallback (failed, no-answer, busy, etc.)"
    },
]


async def create_all_custom_fields():
    """Create all required custom fields in GHL"""
    ghl = GHLClient()
    
    print("=" * 70)
    print("CREATING GHL CUSTOM FIELDS")
    print("=" * 70)
    print(f"\nLocation ID: {ghl.location_id}")
    print(f"Total fields to create: {len(CUSTOM_FIELDS)}\n")
    
    # First, get existing custom fields to check for duplicates
    print("📋 Checking existing custom fields...")
    existing_fields = await ghl.get_custom_fields()
    # GHL returns fieldKey as "contact.{key}" format
    existing_keys = set()
    for field in existing_fields:
        field_key = field.get("fieldKey") or field.get("key", "")
        if field_key:
            existing_keys.add(field_key)
            # Also add without "contact." prefix for matching
            if field_key.startswith("contact."):
                existing_keys.add(field_key.replace("contact.", ""))
    print(f"   Found {len(existing_fields)} existing custom fields\n")
    
    created_count = 0
    skipped_count = 0
    failed_count = 0
    
    for field_def in CUSTOM_FIELDS:
        field_key = field_def["key"]
        field_name = field_def["name"]
        field_type = field_def["type"]
        
        # Check if field already exists
        # GHL generates fieldKey as "contact.{key}", so check both formats
        ghl_field_key = f"contact.{field_key}" if not field_key.startswith("contact.") else field_key
        if field_key in existing_keys or ghl_field_key in existing_keys:
            print(f"⏭️  SKIP - {field_name} ({field_key})")
            print(f"   Field already exists (key: {ghl_field_key})")
            skipped_count += 1
            continue
        
        print(f"🔧 Creating: {field_name} ({field_key})")
        print(f"   Type: {field_type}")
        
        try:
            result = await ghl.create_custom_field(
                name=field_name,
                key=field_key,
                field_type=field_type,
                object_type="contact",
                options=field_def.get("options"),
                required=False
            )
            
            field_id = result.get("id") or result.get("customFieldId") or "N/A"
            actual_field_key = result.get("fieldKey", field_key)
            print(f"   ✅ Created successfully!")
            print(f"      ID: {field_id}")
            print(f"      Field Key: {actual_field_key}")
            created_count += 1
            
        except Exception as e:
            error_msg = str(e)
            # Check if it's a duplicate error
            if "already exists" in error_msg.lower() or "duplicate" in error_msg.lower():
                print(f"   ⏭️  Field already exists (duplicate detected)")
                skipped_count += 1
            else:
                print(f"   ❌ Failed: {error_msg}")
                failed_count += 1
                logger.error(f"Failed to create custom field {field_key}: {e}")
        
        print()  # Empty line for readability
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"✅ Created: {created_count} fields")
    print(f"⏭️  Skipped: {skipped_count} fields (already exist)")
    print(f"❌ Failed: {failed_count} fields")
    print(f"📊 Total: {len(CUSTOM_FIELDS)} fields")
    
    if failed_count > 0:
        print("\n⚠️  Some fields failed to create. Check the errors above.")
        return False
    
    if created_count + skipped_count == len(CUSTOM_FIELDS):
        print("\n✅ All custom fields are now configured!")
        print("\nNext steps:")
        print("1. Verify fields in GHL dashboard: Settings → Custom Fields")
        print("2. Make fields visible in contact views if needed")
        print("3. Test field updates by creating a test contact")
        return True
    else:
        print("\n⚠️  Not all fields were processed. Please review the output above.")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(create_all_custom_fields())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        logger.exception("Fatal error in create_ghl_custom_fields")
        sys.exit(1)

