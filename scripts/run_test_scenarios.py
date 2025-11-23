"""
Run all test scenarios from TEST_PROTOCOL.txt
Tests each scenario and generates detailed logs
"""
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.vapi_test_client import VapiTestClient
from src.config import settings


# Test scenarios from TEST_PROTOCOL.txt
TEST_SCENARIOS = {
    "1_service_repair": {
        "name": "Inbound Call - Service/Repair Request",
        "assistant": "inbound",
        "questions": [
            "Hello, I need help with my heating system",
            "My furnace stopped working last night, it's really cold",
            "My name is John Smith, phone is 503-555-0101, email is john.smith@test.com",
            "My address is 123 Main St, Salem, OR 97301",
            "Yes, I'd like to receive text confirmations",
            "When can you come out to fix it?",
            "Yes, tomorrow at 2 PM works for me",
            "Yes, please send me a confirmation"
        ]
    },
    "2_installation_estimate": {
        "name": "Inbound Call - Installation/Estimate Request",
        "assistant": "inbound",
        "questions": [
            "I'm looking to replace my old air conditioning system",
            "My name is Sarah Johnson, phone 503-555-0102, email sarah.j@test.com",
            "My address is 456 Oak Ave, Keizer, OR 97303",
            "How much will it cost?",
            "Can you just give me a quote over the phone?",
            "When can someone come out for an estimate?",
            "Next Tuesday at 10 AM works"
        ]
    },
    "3_maintenance": {
        "name": "Inbound Call - Maintenance Request",
        "assistant": "inbound",
        "questions": [
            "I need my HVAC system serviced, it's been a while",
            "My name is Mike Davis, phone 503-555-0103",
            "My address is 789 Pine St, Salem, OR 97302",
            "When can you schedule maintenance?"
        ]
    },
    "4_appointment_change": {
        "name": "Inbound Call - Appointment Change",
        "assistant": "inbound",
        "questions": [
            "I need to reschedule my appointment for tomorrow",
            "Can we move it to next week instead?"
        ]
    },
    "5_emergency": {
        "name": "Inbound Call - Emergency Situation",
        "assistant": "inbound",
        "questions": [
            "My heat is out and I have a 2-month-old baby, it's freezing",
            "This is an emergency, I need someone today",
            "My name is Emergency Test, phone 503-555-0104",
            "My address is 321 Elm St, Salem, OR 97301"
        ]
    },
    "6_warm_transfer": {
        "name": "Inbound Call - Warm Transfer",
        "assistant": "inbound",
        "questions": [
            "I'd like to speak with the owner about pricing",
            "Yes, please transfer me"
        ]
    },
    "7_knowledge_base": {
        "name": "Inbound Call - Knowledge Base Testing",
        "assistant": "inbound",
        "questions": [
            "Do you service Portland?",
            "What are your hours?",
            "Do you work on boilers?",
            "How much is a diagnostic?",
            "Do you offer discounts for veterans?",
            "What makes you different?"
        ]
    },
    "8_out_of_area": {
        "name": "Inbound Call - Out of Service Area",
        "assistant": "inbound",
        "questions": [
            "I'm in Eugene, can you come out?",
            "My name is Out of Area Test, address 123 Test St, Eugene, OR 97401",
            "I understand, can you still schedule me?"
        ]
    },
    "9_brand_voice": {
        "name": "Inbound Call - Brand Voice Verification",
        "assistant": "inbound",
        "questions": [
            "Just give me a price over the phone",
            "I already bought the parts, can you install them?"
        ]
    }
}


class TestRunner:
    """Runs test scenarios and generates reports"""
    
    def __init__(self, api_key: str, test_phone: str):
        self.client = VapiTestClient(api_key=api_key)
        self.test_phone = test_phone
        self.results = []
        
        # Get assistant IDs
        self.inbound_id = settings.vapi_inbound_assistant_id or "d61d0517-4a65-496e-b97f-d3ad220f684e"
        self.outbound_id = settings.vapi_outbound_assistant_id or "d6c74f74-de2a-420d-ae59-aab8fa7cbabe"
    
    async def run_scenario(
        self,
        scenario_id: str,
        scenario: Dict[str, Any],
        wait_for_completion: bool = False
    ) -> Dict[str, Any]:
        """Run a single test scenario"""
        assistant_type = scenario["assistant"]
        assistant_id = self.inbound_id if assistant_type == "inbound" else self.outbound_id
        
        print(f"\n{'='*70}")
        print(f"🧪 TEST SCENARIO: {scenario['name']}")
        print(f"{'='*70}")
        print(f"Assistant: {assistant_type} ({assistant_id})")
        print(f"Phone: {self.test_phone}")
        print(f"Questions: {len(scenario['questions'])}")
        
        # Create call
        try:
            call = await self.client.create_test_call(
                assistant_id=assistant_id,
                phone_number=self.test_phone
            )
            call_id = call.get("id")
            
            print(f"✅ Call created: {call_id}")
            print(f"📞 Call URL: https://dashboard.vapi.ai/call/{call_id}")
            
            if wait_for_completion:
                print("⏳ Waiting for call to complete (this may take a few minutes)...")
                logs = await self.client.wait_for_call_completion(call_id, timeout=600)
            else:
                print("ℹ️  Call initiated. Analyzing initial state...")
                await asyncio.sleep(5)  # Wait a bit for call to start
                logs = await self.client.get_call_logs(call_id)
            
            # Analyze logs
            analysis = await self.client.analyze_call_logs(call_id)
            
            result = {
                "scenario_id": scenario_id,
                "scenario_name": scenario["name"],
                "call_id": call_id,
                "call_url": f"https://dashboard.vapi.ai/call/{call_id}",
                "assistant_id": assistant_id,
                "test_phone": self.test_phone,
                "questions": scenario["questions"],
                "status": logs.get("status"),
                "duration": logs.get("duration"),
                "analysis": analysis,
                "timestamp": datetime.now().isoformat(),
                "transcript": logs.get("transcript", ""),
                "errors": analysis.get("errors", []),
                "tool_calls": analysis.get("tool_calls", []),
                "function_calls": analysis.get("function_calls", [])
            }
            
            # Print summary
            print(f"\n📊 RESULTS:")
            print(f"  Status: {result['status']}")
            print(f"  Duration: {result['duration']}s" if result['duration'] else "  Duration: N/A")
            print(f"  Tool Calls: {len(result['tool_calls'])}")
            print(f"  Function Calls: {len(result['function_calls'])}")
            print(f"  Errors: {len(result['errors'])}")
            
            if result['errors']:
                print(f"\n❌ ERRORS FOUND:")
                for error in result['errors']:
                    print(f"  - {error.get('type')}: {error.get('message')}")
            
            if result['tool_calls']:
                print(f"\n🔧 TOOL CALLS:")
                for tool in result['tool_calls']:
                    status_icon = "✅" if tool.get('status') == 'completed' else "❌"
                    print(f"  {status_icon} {tool.get('name')}: {tool.get('status')}")
                    if tool.get('error'):
                        print(f"     Error: {tool.get('error')}")
            
            return result
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return {
                "scenario_id": scenario_id,
                "scenario_name": scenario["name"],
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def run_all_scenarios(
        self,
        scenario_ids: List[str] = None,
        wait_for_completion: bool = False
    ):
        """Run all or selected test scenarios"""
        if scenario_ids is None:
            scenario_ids = list(TEST_SCENARIOS.keys())
        
        print(f"\n🚀 Starting test run with {len(scenario_ids)} scenarios...")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        for scenario_id in scenario_ids:
            if scenario_id not in TEST_SCENARIOS:
                print(f"⚠️  Scenario {scenario_id} not found, skipping...")
                continue
            
            result = await self.run_scenario(
                scenario_id,
                TEST_SCENARIOS[scenario_id],
                wait_for_completion=wait_for_completion
            )
            self.results.append(result)
            
            # Wait between tests
            if scenario_id != scenario_ids[-1]:
                print("\n⏸️  Waiting 10 seconds before next test...")
                await asyncio.sleep(10)
        
        # Generate report
        await self.generate_report()
    
    async def generate_report(self):
        """Generate test report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = Path(__file__).parent.parent / f"test_results_{timestamp}.json"
        summary_file = Path(__file__).parent.parent / f"test_summary_{timestamp}.txt"
        
        # Save full results
        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)
        
        # Generate summary
        total = len(self.results)
        successful = sum(1 for r in self.results if r.get("status") in ["ended", "completed"])
        errors = sum(1 for r in self.results if r.get("errors"))
        
        summary = f"""
================================================================================
TEST EXECUTION SUMMARY
================================================================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total Scenarios: {total}
Successful: {successful}
With Errors: {errors}

================================================================================
DETAILED RESULTS
================================================================================
"""
        
        for result in self.results:
            summary += f"\n{result.get('scenario_name', 'Unknown')}\n"
            summary += f"  Call ID: {result.get('call_id', 'N/A')}\n"
            summary += f"  Status: {result.get('status', 'N/A')}\n"
            summary += f"  Duration: {result.get('duration', 'N/A')}s\n"
            summary += f"  URL: {result.get('call_url', 'N/A')}\n"
            
            if result.get('errors'):
                summary += f"  ❌ Errors: {len(result['errors'])}\n"
                for error in result['errors']:
                    summary += f"     - {error.get('type')}: {error.get('message')}\n"
            
            if result.get('tool_calls'):
                summary += f"  🔧 Tool Calls: {len(result['tool_calls'])}\n"
                for tool in result['tool_calls']:
                    summary += f"     - {tool.get('name')}: {tool.get('status')}\n"
            
            summary += "\n"
        
        summary += f"""
================================================================================
FULL RESULTS SAVED TO: {report_file}
================================================================================
"""
        
        with open(summary_file, "w") as f:
            f.write(summary)
        
        print(f"\n{'='*70}")
        print(f"📊 TEST REPORT GENERATED")
        print(f"{'='*70}")
        print(f"Full Results: {report_file}")
        print(f"Summary: {summary_file}")
        print(summary)


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Vapi test scenarios")
    parser.add_argument(
        "--api-key",
        default=os.getenv("VAPI_API_KEY") or "bee0337d-41cd-49c2-9038-98cd0e18c75b",
        help="Vapi API key"
    )
    parser.add_argument(
        "--phone",
        required=True,
        help="Test phone number (E.164 format, e.g., +15035550101)"
    )
    parser.add_argument(
        "--scenario",
        action="append",
        help="Specific scenario ID to run (can be used multiple times)"
    )
    parser.add_argument(
        "--wait",
        action="store_true",
        help="Wait for calls to complete (slower but more detailed)"
    )
    
    args = parser.parse_args()
    
    runner = TestRunner(api_key=args.api_key, test_phone=args.phone)
    
    scenario_ids = args.scenario if args.scenario else None
    
    await runner.run_all_scenarios(
        scenario_ids=scenario_ids,
        wait_for_completion=args.wait
    )


if __name__ == "__main__":
    asyncio.run(main())

