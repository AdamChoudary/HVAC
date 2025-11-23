"""
Check and analyze Vapi call logs
"""
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.vapi_test_client import VapiTestClient
from src.config import settings


async def check_call_logs(
    call_id: Optional[str] = None,
    assistant_id: Optional[str] = None,
    limit: int = 10
):
    """Check call logs for a specific call or list recent calls"""
    api_key = os.getenv("VAPI_API_KEY") or "bee0337d-41cd-49c2-9038-98cd0e18c75b"
    client = VapiTestClient(api_key=api_key)
    
    if call_id:
        # Get specific call logs
        print(f"\n{'='*70}")
        print(f"📋 CALL LOGS: {call_id}")
        print(f"{'='*70}\n")
        
        logs = await client.get_call_logs(call_id)
        analysis = await client.analyze_call_logs(call_id)
        
        print(f"Status: {logs.get('status')}")
        print(f"Duration: {logs.get('duration')}s" if logs.get('duration') else "Duration: N/A")
        print(f"Started: {logs.get('started_at')}")
        print(f"Ended: {logs.get('ended_at')}")
        
        if logs.get('transcript'):
            print(f"\n📝 TRANSCRIPT:")
            print(f"{'-'*70}")
            print(logs['transcript'])
            print(f"{'-'*70}")
        
        if analysis.get('errors'):
            print(f"\n❌ ERRORS ({len(analysis['errors'])}):")
            for error in analysis['errors']:
                print(f"  - {error.get('type')}: {error.get('message')}")
        
        if analysis.get('tool_calls'):
            print(f"\n🔧 TOOL CALLS ({len(analysis['tool_calls'])}):")
            for tool in analysis['tool_calls']:
                status_icon = "✅" if tool.get('status') == 'completed' else "❌"
                print(f"  {status_icon} {tool.get('name')}: {tool.get('status')}")
                if tool.get('error'):
                    print(f"     Error: {tool.get('error')}")
                if tool.get('result'):
                    result_str = json.dumps(tool.get('result'), indent=2)
                    if len(result_str) < 200:
                        print(f"     Result: {result_str}")
        
        if analysis.get('function_calls'):
            print(f"\n⚙️  FUNCTION CALLS ({len(analysis['function_calls'])}):")
            for func in analysis['function_calls']:
                status_icon = "✅" if func.get('status') == 'completed' else "❌"
                print(f"  {status_icon} {func.get('name')}: {func.get('status')}")
                if func.get('error'):
                    print(f"     Error: {func.get('error')}")
        
        if logs.get('recording_url'):
            print(f"\n🎙️  RECORDING: {logs['recording_url']}")
        
        # Save detailed log
        log_file = Path(__file__).parent.parent / f"call_log_{call_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, "w") as f:
            json.dump({
                "call_id": call_id,
                "logs": logs,
                "analysis": analysis
            }, f, indent=2)
        print(f"\n💾 Full log saved to: {log_file}")
        
    else:
        # List recent calls
        print(f"\n{'='*70}")
        print(f"📋 RECENT CALLS")
        print(f"{'='*70}\n")
        
        params = {"limit": limit}
        if assistant_id:
            params["assistantId"] = assistant_id
        
        calls = await client.list_calls(**params)
        
        if not calls:
            print("No calls found.")
            return
        
        print(f"Found {len(calls)} calls:\n")
        
        for i, call in enumerate(calls, 1):
            call_id = call.get('id')
            status = call.get('status', 'unknown')
            duration = call.get('duration', 0)
            started = call.get('startedAt', 'N/A')
            
            status_icon = {
                'ended': '✅',
                'completed': '✅',
                'failed': '❌',
                'no-answer': '⚠️',
                'busy': '⚠️'
            }.get(status, '❓')
            
            print(f"{i}. {status_icon} {call_id}")
            print(f"   Status: {status}")
            print(f"   Duration: {duration}s")
            print(f"   Started: {started}")
            print(f"   URL: https://dashboard.vapi.ai/call/{call_id}")
            print()


async def check_tool_executions(call_id: str):
    """Check tool execution logs for a call"""
    api_key = os.getenv("VAPI_API_KEY") or "bee0337d-41cd-49c2-9038-98cd0e18c75b"
    client = VapiTestClient(api_key=api_key)
    
    print(f"\n{'='*70}")
    print(f"🔧 TOOL EXECUTION LOGS: {call_id}")
    print(f"{'='*70}\n")
    
    logs = await client.get_call_logs(call_id)
    analysis = await client.analyze_call_logs(call_id)
    
    tool_calls = analysis.get('tool_calls', [])
    function_calls = analysis.get('function_calls', [])
    
    all_calls = []
    for tool in tool_calls:
        all_calls.append({
            "type": "tool",
            "name": tool.get('name'),
            "status": tool.get('status'),
            "error": tool.get('error'),
            "result": tool.get('result')
        })
    
    for func in function_calls:
        all_calls.append({
            "type": "function",
            "name": func.get('name'),
            "status": func.get('status'),
            "error": func.get('error'),
            "result": func.get('result')
        })
    
    if not all_calls:
        print("No tool or function calls found.")
        return
    
    print(f"Found {len(all_calls)} tool/function calls:\n")
    
    for i, call in enumerate(all_calls, 1):
        status_icon = "✅" if call.get('status') == 'completed' else "❌"
        print(f"{i}. {status_icon} [{call['type'].upper()}] {call['name']}")
        print(f"   Status: {call.get('status')}")
        
        if call.get('error'):
            print(f"   ❌ Error: {call['error']}")
        
        if call.get('result'):
            result_str = json.dumps(call['result'], indent=2)
            if len(result_str) < 500:
                print(f"   Result:\n{result_str}")
            else:
                print(f"   Result: (too long, see full log)")
        
        print()


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Check Vapi call logs")
    parser.add_argument(
        "--call-id",
        help="Specific call ID to check"
    )
    parser.add_argument(
        "--assistant-id",
        help="Filter calls by assistant ID"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of recent calls to list"
    )
    parser.add_argument(
        "--tools",
        action="store_true",
        help="Show detailed tool execution logs"
    )
    
    args = parser.parse_args()
    
    if args.tools and args.call_id:
        await check_tool_executions(args.call_id)
    else:
        await check_call_logs(
            call_id=args.call_id,
            assistant_id=args.assistant_id,
            limit=args.limit
        )


if __name__ == "__main__":
    asyncio.run(main())

