"""
Verify and configure Vapi tools in API Request format.
Checks current assistant configuration and verifies tools are properly set up.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.integrations.vapi import VapiClient
from src.config import settings
from src.utils.logging import logger


async def verify_assistant_tools(assistant_id: str, assistant_name: str):
    """Verify tools are configured for an assistant"""
    vapi = VapiClient()
    
    print(f"\n{'='*70}")
    print(f"Checking: {assistant_name}")
    print(f"Assistant ID: {assistant_id}")
    print(f"{'='*70}\n")
    
    try:
        # Get assistant details
        assistant = await vapi.get_assistant(assistant_id)
        
        print("✅ Assistant found!")
        print(f"   Name: {assistant.get('name', 'N/A')}")
        print(f"   Status: {assistant.get('status', 'N/A')}")
        print()
        
        # Check functions/tools
        functions = assistant.get("functions", [])
        server_functions = assistant.get("serverFunctions", [])
        
        # Vapi can have functions in different formats
        all_tools = functions + server_functions
        
        if not all_tools:
            print("❌ NO TOOLS/FUNCTIONS FOUND!")
            print("   Tools need to be configured.")
            return False
        
        print(f"📋 Found {len(all_tools)} tool(s):\n")
        
        for i, tool in enumerate(all_tools, 1):
            tool_type = tool.get("type", "unknown")
            tool_name = tool.get("name", "unnamed")
            server_url = tool.get("serverUrl", tool.get("url", "N/A"))
            
            print(f"   {i}. {tool_name}")
            print(f"      Type: {tool_type}")
            print(f"      Server URL: {server_url}")
            
            # Check if it's properly configured
            if server_url and "scott-valley-hvac-api.fly.dev" in server_url:
                print(f"      ✅ URL configured correctly")
            elif server_url == "N/A":
                print(f"      ⚠️  No server URL configured")
            else:
                print(f"      ⚠️  URL might be incorrect: {server_url}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking assistant: {str(e)}")
        logger.exception(f"Error verifying assistant {assistant_id}")
        return False


async def main():
    """Main verification function"""
    print("\n" + "="*70)
    print("🔍 VAPI TOOLS VERIFICATION")
    print("="*70)
    
    # Get assistant IDs
    inbound_id = settings.vapi_outbound_assistant_id or "d61d0517-4a65-496e-b97f-d3ad220f684e"
    outbound_id = "d6c74f74-de2a-420d-ae59-aab8fa7cbabe"
    
    print("\nNote: Using assistant IDs from environment or defaults")
    print(f"Inbound ID: {inbound_id}")
    print(f"Outbound ID: {outbound_id}")
    
    # Verify Inbound Assistant
    inbound_ok = await verify_assistant_tools(
        inbound_id,
        "Inbound Assistant"
    )
    
    # Verify Outbound Assistant
    outbound_ok = await verify_assistant_tools(
        outbound_id,
        "Outbound Assistant"
    )
    
    # Summary
    print("\n" + "="*70)
    print("📊 VERIFICATION SUMMARY")
    print("="*70)
    
    if inbound_ok and outbound_ok:
        print("\n✅ Both assistants have tools configured!")
        print("\nNext steps:")
        print("1. Go to Vapi dashboard: https://dashboard.vapi.ai")
        print("2. Navigate to Assistants section")
        print("3. Click on each assistant")
        print("4. Check 'Tools' or 'Functions' tab")
        print("5. Verify all tools are listed with correct URLs")
        print("\nIf tools are NOT showing in dashboard:")
        print("  - They might need to be configured manually")
        print("  - Or the API format might need adjustment")
    else:
        print("\n⚠️  Some assistants are missing tools!")
        print("   You may need to reconfigure them.")
    
    print()


if __name__ == "__main__":
    asyncio.run(main())

