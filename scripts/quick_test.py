"""
Quick test script - Test a single scenario quickly
"""
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.vapi_test_client import VapiTestClient
from src.config import settings


async def quick_test(question: str, phone: str):
    """Quick test with a single question"""
    api_key = os.getenv("VAPI_API_KEY") or "bee0337d-41cd-49c2-9038-98cd0e18c75b"
    client = VapiTestClient(api_key=api_key)
    
    inbound_id = settings.vapi_inbound_assistant_id or "d61d0517-4a65-496e-b97f-d3ad220f684e"
    
    print(f"\n{'='*70}")
    print(f"🚀 QUICK TEST")
    print(f"{'='*70}")
    print(f"Question: {question}")
    print(f"Phone: {phone}")
    print(f"Assistant: {inbound_id}")
    print()
    
    # Create call
    call = await client.create_test_call(
        assistant_id=inbound_id,
        phone_number=phone
    )
    
    call_id = call.get("id")
    print(f"✅ Call created: {call_id}")
    print(f"📞 Dashboard: https://dashboard.vapi.ai/call/{call_id}")
    print(f"\n💡 Answer the call and ask: '{question}'")
    print(f"⏳ Waiting 30 seconds for call to start...")
    
    await asyncio.sleep(30)
    
    # Check status
    logs = await client.get_call_logs(call_id)
    analysis = await client.analyze_call_logs(call_id)
    
    print(f"\n📊 STATUS:")
    print(f"  Status: {logs.get('status')}")
    print(f"  Duration: {logs.get('duration')}s" if logs.get('duration') else "  Duration: N/A")
    
    if analysis.get('errors'):
        print(f"\n❌ ERRORS:")
        for error in analysis['errors']:
            print(f"  - {error.get('message')}")
    
    if analysis.get('tool_calls'):
        print(f"\n🔧 TOOLS USED:")
        for tool in analysis['tool_calls']:
            print(f"  - {tool.get('name')}: {tool.get('status')}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Quick test with a single question")
    parser.add_argument("question", help="Question to ask")
    parser.add_argument("--phone", required=True, help="Phone number (E.164 format)")
    
    args = parser.parse_args()
    
    asyncio.run(quick_test(args.question, args.phone))

