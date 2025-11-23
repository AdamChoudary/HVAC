"""
Script to update existing Vapi assistants with comprehensive knowledge base and professional system prompts.
This script uses the updated assistant configurations from src/integrations/vapi/assistants.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.integrations.vapi import VapiClient
from src.integrations.vapi.assistants import create_inbound_assistant, create_outbound_assistant
from src.config import settings


async def update_assistants_with_knowledge():
    """Update both assistants with comprehensive knowledge base and professional system prompts"""
    vapi = VapiClient()
    
    # Get assistant IDs from environment
    inbound_assistant_id = settings.vapi_inbound_assistant_id
    outbound_assistant_id = settings.vapi_outbound_assistant_id
    
    # If not set, try to get from Vapi (list assistants and find by name)
    if not inbound_assistant_id or not outbound_assistant_id:
        print("⚠️  Assistant IDs not found in .env")
        print("   Attempting to find assistants by name...")
        try:
            # Try to list assistants (if API supports it)
            # For now, we'll use common fallback IDs or prompt user
            print("\n   Please provide assistant IDs:")
            if not inbound_assistant_id:
                print("   You can find Inbound Assistant ID in Vapi dashboard")
                print("   Or run: python scripts/setup_vapi.py to create new ones")
            if not outbound_assistant_id:
                print("   You can find Outbound Assistant ID in Vapi dashboard")
                print("   Or run: python scripts/setup_vapi.py to create new ones")
            print("\n   To set in .env, add:")
            if not inbound_assistant_id:
                print("   VAPI_INBOUND_ASSISTANT_ID=your_inbound_assistant_id")
            if not outbound_assistant_id:
                print("   VAPI_OUTBOUND_ASSISTANT_ID=your_outbound_assistant_id")
            return
        except Exception as e:
            print(f"   Error: {e}")
            return
    
    # Get server URL
    server_url = settings.webhook_base_url or "https://scott-valley-hvac-api.fly.dev"
    
    print("=" * 70)
    print("🔄 UPDATING VAPI ASSISTANTS WITH KNOWLEDGE BASE")
    print("=" * 70)
    print(f"\nServer URL: {server_url}")
    print(f"Inbound Assistant ID: {inbound_assistant_id}")
    print(f"Outbound Assistant ID: {outbound_assistant_id}\n")
    
    # Get current assistant configs to preserve other settings
    try:
        inbound_assistant = await vapi.get_assistant(inbound_assistant_id)
        outbound_assistant = await vapi.get_assistant(outbound_assistant_id)
    except Exception as e:
        print(f"❌ Error fetching assistants: {e}")
        print("   Make sure assistant IDs are correct in .env")
        return
    
    # Create new assistant configs with updated system prompts
    print("\n📝 Generating updated configurations...")
    inbound_config = await create_inbound_assistant(server_url)
    outbound_config = await create_outbound_assistant(server_url)
    
    # Extract just the model/messages for update (preserve other settings)
    inbound_model_update = {
        "model": inbound_config["model"]
    }
    outbound_model_update = {
        "model": outbound_config["model"]
    }
    
    # Update Inbound Assistant
    print("\n1️⃣  Updating Inbound Assistant...")
    try:
        await vapi.update_assistant(inbound_assistant_id, inbound_model_update)
        print("   ✅ Inbound assistant updated successfully!")
        print("   📋 Updated with:")
        print("      • Comprehensive knowledge base")
        print("      • Professional system prompt")
        print("      • Detailed tool usage instructions")
        print("      • Business hours, pricing, service areas")
        print("      • Staff directory and transfer protocols")
        print("      • Brand voice guidelines")
    except Exception as e:
        print(f"   ❌ Error updating inbound assistant: {str(e)}")
        return
    
    # Update Outbound Assistant
    print("\n2️⃣  Updating Outbound Assistant...")
    try:
        await vapi.update_assistant(outbound_assistant_id, outbound_model_update)
        print("   ✅ Outbound assistant updated successfully!")
        print("   📋 Updated with:")
        print("      • Comprehensive knowledge base")
        print("      • Professional system prompt")
        print("      • Detailed tool usage instructions")
        print("      • Outbound call flow guidelines")
        print("      • Lead qualification best practices")
        print("      • Brand voice guidelines")
    except Exception as e:
        print(f"   ❌ Error updating outbound assistant: {str(e)}")
        return
    
    print("\n" + "=" * 70)
    print("✅ KNOWLEDGE BASE INTEGRATION COMPLETE!")
    print("=" * 70)
    print("\n📊 What's Now Included:")
    print("  ✅ Complete business information (hours, service areas, coverage)")
    print("  ✅ Detailed pricing guidance and ranges")
    print("  ✅ Appointment types and durations")
    print("  ✅ Staff directory with transfer protocols")
    print("  ✅ Brand voice and communication guidelines")
    print("  ✅ Discount tiers and recognition programs")
    print("  ✅ Service area coverage details")
    print("  ✅ Emergency and weekend policies")
    print("  ✅ Professional tool usage instructions")
    print("  ✅ Best practices and critical rules")
    print("\n🎯 Next Steps:")
    print("  1. Test inbound calls to verify knowledge base is working")
    print("  2. Test outbound calls to verify lead qualification")
    print("  3. Monitor call quality and adjust prompts if needed")
    print("\n💡 The assistants now have all the information needed to:")
    print("   • Answer business-specific questions accurately")
    print("   • Provide pricing guidance appropriately")
    print("   • Handle emergencies and urgent situations")
    print("   • Transfer calls to appropriate staff members")
    print("   • Maintain brand voice and professionalism")


if __name__ == "__main__":
    asyncio.run(update_assistants_with_knowledge())

