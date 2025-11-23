"""
Vapi Test Client - Extended client for testing scenarios
"""
import asyncio
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
from pathlib import Path

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.integrations.vapi import VapiClient
from src.config import settings


class VapiTestClient(VapiClient):
    """Extended Vapi client for testing"""
    
    def __init__(self, api_key: Optional[str] = None):
        if api_key:
            self.api_key = api_key
            self.base_url = "https://api.vapi.ai"
            self.headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        else:
            super().__init__()
    
    async def create_test_call(
        self,
        assistant_id: str,
        phone_number: str,
        customer: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a test call"""
        call_config = {
            "assistantId": assistant_id,
            "customer": {
                "number": phone_number
            }
        }
        if customer:
            call_config["customer"].update(customer)
        return await self.create_call(call_config)
    
    async def get_call_logs(self, call_id: str) -> Dict[str, Any]:
        """Get detailed call logs including tool executions"""
        call_data = await self.get_call(call_id)
        
        # Try to get transcript
        transcript = None
        try:
            transcript_data = await self.get_call_transcript(call_id)
            transcript = transcript_data.get("transcript", "")
        except:
            pass
        
        # Try to get recording
        recording_url = None
        try:
            recording_data = await self.get_call_recording(call_id)
            recording_url = recording_data.get("url", "")
        except:
            pass
        
        return {
            "call": call_data,
            "transcript": transcript,
            "recording_url": recording_url,
            "status": call_data.get("status"),
            "duration": call_data.get("duration"),
            "started_at": call_data.get("startedAt"),
            "ended_at": call_data.get("endedAt"),
            "messages": call_data.get("messages", []),
            "function_calls": call_data.get("functionCalls", []),
            "tool_calls": call_data.get("toolCalls", []),
        }
    
    async def wait_for_call_completion(
        self,
        call_id: str,
        timeout: int = 300,
        check_interval: int = 5
    ) -> Dict[str, Any]:
        """Wait for call to complete and return logs"""
        start_time = datetime.now().timestamp()
        
        while True:
            call_data = await self.get_call(call_id)
            status = call_data.get("status")
            
            if status in ["ended", "failed", "no-answer", "busy"]:
                return await self.get_call_logs(call_id)
            
            elapsed = datetime.now().timestamp() - start_time
            if elapsed > timeout:
                return {
                    "error": "Timeout waiting for call completion",
                    "current_status": status,
                    "call_data": call_data
                }
            
            await asyncio.sleep(check_interval)
    
    async def test_scenario(
        self,
        scenario_name: str,
        assistant_id: str,
        phone_number: str,
        questions: List[str],
        wait_for_completion: bool = False
    ) -> Dict[str, Any]:
        """Test a scenario with a list of questions"""
        print(f"\n{'='*70}")
        print(f"TESTING SCENARIO: {scenario_name}")
        print(f"{'='*70}")
        
        # Create call
        print(f"📞 Creating call to {phone_number}...")
        call = await self.create_test_call(assistant_id, phone_number)
        call_id = call.get("id")
        print(f"✅ Call created: {call_id}")
        
        if wait_for_completion:
            print("⏳ Waiting for call to complete...")
            logs = await self.wait_for_call_completion(call_id)
        else:
            print("ℹ️  Call initiated. Check Vapi dashboard for real-time updates.")
            logs = await self.get_call_logs(call_id)
        
        return {
            "scenario": scenario_name,
            "call_id": call_id,
            "questions": questions,
            "logs": logs,
            "timestamp": datetime.now().isoformat()
        }
    
    async def analyze_call_logs(self, call_id: str) -> Dict[str, Any]:
        """Analyze call logs for errors and tool executions"""
        logs = await self.get_call_logs(call_id)
        
        analysis = {
            "call_id": call_id,
            "status": logs.get("status"),
            "duration": logs.get("duration"),
            "errors": [],
            "tool_calls": [],
            "function_calls": [],
            "messages_count": len(logs.get("messages", [])),
            "transcript_available": bool(logs.get("transcript")),
        }
        
        # Check for errors
        call_data = logs.get("call", {})
        if call_data.get("error"):
            analysis["errors"].append({
                "type": "call_error",
                "message": call_data.get("error")
            })
        
        # Extract tool calls
        tool_calls = logs.get("tool_calls", []) or call_data.get("toolCalls", [])
        for tool_call in tool_calls:
            analysis["tool_calls"].append({
                "name": tool_call.get("name"),
                "status": tool_call.get("status"),
                "error": tool_call.get("error"),
                "result": tool_call.get("result")
            })
            if tool_call.get("error"):
                analysis["errors"].append({
                    "type": "tool_error",
                    "tool": tool_call.get("name"),
                    "message": tool_call.get("error")
                })
        
        # Extract function calls
        function_calls = logs.get("function_calls", []) or call_data.get("functionCalls", [])
        for func_call in function_calls:
            analysis["function_calls"].append({
                "name": func_call.get("name"),
                "status": func_call.get("status"),
                "error": func_call.get("error"),
                "result": func_call.get("result")
            })
            if func_call.get("error"):
                analysis["errors"].append({
                    "type": "function_error",
                    "function": func_call.get("name"),
                    "message": func_call.get("error")
                })
        
        return analysis


async def main():
    """Main test function"""
    # Get API key from environment or use provided
    api_key = os.getenv("VAPI_API_KEY") or "bee0337d-41cd-49c2-9038-98cd0e18c75b"
    
    client = VapiTestClient(api_key=api_key)
    
    # Get assistant IDs
    inbound_id = settings.vapi_inbound_assistant_id or "d61d0517-4a65-496e-b97f-d3ad220f684e"
    outbound_id = settings.vapi_outbound_assistant_id or "d6c74f74-de2a-420d-ae59-aab8fa7cbabe"
    
    print("Vapi Test Client")
    print(f"Inbound Assistant ID: {inbound_id}")
    print(f"Outbound Assistant ID: {outbound_id}")
    
    # Example: List recent calls
    print("\n📋 Recent Calls:")
    try:
        calls = await client.list_calls(limit=10)
        for call in calls[:5]:
            print(f"  - {call.get('id')}: {call.get('status')} ({call.get('duration')}s)")
    except Exception as e:
        print(f"  Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())

