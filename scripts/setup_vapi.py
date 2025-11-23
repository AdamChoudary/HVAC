"""
Script to set up Vapi assistants.
Run this after deploying your server to create the assistants.
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.integrations.vapi.assistants import create_inbound_assistant, create_outbound_assistant
from src.config import settings


async def main():
    # Get server URL from settings or use default
    server_url = settings.webhook_base_url
    if not server_url:
        # Default to Fly.io deployment URL
        server_url = "https://scott-valley-hvac-api.fly.dev"
        print(f"⚠️  WEBHOOK_BASE_URL not set in .env, using default: {server_url}")
        print("   To set custom URL, add WEBHOOK_BASE_URL to .env file")
    else:
        print(f"✅ Using server URL from settings: {server_url}")
    
    if not server_url:
        print("❌ Error: Server URL is required")
        print("   Set WEBHOOK_BASE_URL in .env or update script")
        return
    
    print(f"Creating assistants with server URL: {server_url}")
    
    # Create inbound assistant
    print("\nCreating inbound assistant...")
    inbound_result = await create_inbound_assistant(server_url)
    inbound_id = inbound_result.get("id", "")
    print(f"Inbound Assistant ID: {inbound_id}")
    print(f"Save this ID for phone number configuration")
    
    # Create outbound assistant
    print("\nCreating outbound assistant...")
    outbound_result = await create_outbound_assistant(server_url)
    outbound_id = outbound_result.get("id", "")
    print(f"Outbound Assistant ID: {outbound_id}")
    print(f"Save this ID for webhook configuration")
    
    print("\n✅ Setup complete!")
    print(f"\nNext steps:")
    print(f"1. Configure phone number in Vapi dashboard to use Inbound Assistant ID: {inbound_id}")
    print(f"2. Update webhook handler to use Outbound Assistant ID: {outbound_id}")
    print(f"3. Test inbound calls")
    print(f"4. Test outbound calls via webhook")


if __name__ == "__main__":
    asyncio.run(main())


