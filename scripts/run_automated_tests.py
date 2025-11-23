"""
Automated test runner - Tests API endpoints and configurations without making calls
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
from src.integrations.ghl import GHLClient
from src.integrations.vapi import VapiClient


class AutomatedTester:
    """Run automated tests that don't require phone calls"""
    
    def __init__(self, api_key: str):
        self.vapi_client = VapiTestClient(api_key=api_key)
        self.ghl_client = GHLClient()
        self.results = []
        self.errors = []
    
    async def test_vapi_connection(self) -> Dict[str, Any]:
        """Test 1: Vapi API Connection"""
        print("\n" + "="*70)
        print("TEST 1: Vapi API Connection")
        print("="*70)
        
        try:
            calls = await self.vapi_client.list_calls(limit=1)
            result = {
                "test": "vapi_connection",
                "status": "✅ PASSED",
                "details": f"Successfully connected to Vapi API. Found {len(calls)} recent calls."
            }
            print(f"✅ PASSED: Connected to Vapi API")
            return result
        except Exception as e:
            result = {
                "test": "vapi_connection",
                "status": "❌ FAILED",
                "error": str(e)
            }
            print(f"❌ FAILED: {e}")
            self.errors.append(result)
            return result
    
    async def test_assistants_configuration(self) -> Dict[str, Any]:
        """Test 2: Assistants Configuration"""
        print("\n" + "="*70)
        print("TEST 2: Assistants Configuration")
        print("="*70)
        
        inbound_id = settings.vapi_inbound_assistant_id or "d61d0517-4a65-496e-b97f-d3ad220f684e"
        outbound_id = settings.vapi_outbound_assistant_id or "d6c74f74-de2a-420d-ae59-aab8fa7cbabe"
        
        issues = []
        
        try:
            # Check inbound assistant
            inbound = await self.vapi_client.get_assistant(inbound_id)
            print(f"✅ Inbound Assistant: {inbound.get('name')}")
            print(f"   ID: {inbound_id}")
            
            voice = inbound.get("voice", {})
            if isinstance(voice, dict):
                voice_name = voice.get("name", voice.get("voiceId", "Unknown"))
            else:
                voice_name = "Unknown"
            print(f"   Voice: {voice_name}")
            
            functions = inbound.get("functions", [])
            print(f"   Functions: {len(functions)}")
            
            if len(functions) < 7:
                issues.append(f"Inbound assistant has only {len(functions)} functions (expected 7)")
            
            # Check outbound assistant
            outbound = await self.vapi_client.get_assistant(outbound_id)
            print(f"✅ Outbound Assistant: {outbound.get('name')}")
            print(f"   ID: {outbound_id}")
            
            voice = outbound.get("voice", {})
            if isinstance(voice, dict):
                voice_name = voice.get("name", voice.get("voiceId", "Unknown"))
            else:
                voice_name = "Unknown"
            print(f"   Voice: {voice_name}")
            
            functions = outbound.get("functions", [])
            print(f"   Functions: {len(functions)}")
            
            if len(functions) < 7:
                issues.append(f"Outbound assistant has only {len(functions)} functions (expected 7)")
            
            result = {
                "test": "assistants_configuration",
                "status": "✅ PASSED" if not issues else "⚠️ WARNINGS",
                "inbound": {
                    "id": inbound_id,
                    "name": inbound.get("name"),
                    "voice": voice_name,
                    "functions_count": len(functions)
                },
                "outbound": {
                    "id": outbound_id,
                    "name": outbound.get("name"),
                    "voice": voice_name,
                    "functions_count": len(functions)
                },
                "issues": issues
            }
            
            if issues:
                print(f"\n⚠️  WARNINGS:")
                for issue in issues:
                    print(f"   - {issue}")
            
            return result
            
        except Exception as e:
            result = {
                "test": "assistants_configuration",
                "status": "❌ FAILED",
                "error": str(e)
            }
            print(f"❌ FAILED: {e}")
            self.errors.append(result)
            return result
    
    async def test_ghl_connection(self) -> Dict[str, Any]:
        """Test 3: GHL API Connection"""
        print("\n" + "="*70)
        print("TEST 3: GHL API Connection")
        print("="*70)
        
        try:
            calendars = await self.ghl_client.get_calendars()
            result = {
                "test": "ghl_connection",
                "status": "✅ PASSED",
                "details": f"Successfully connected to GHL API. Found {len(calendars)} calendars."
            }
            print(f"✅ PASSED: Connected to GHL API")
            print(f"   Found {len(calendars)} calendars")
            return result
        except Exception as e:
            result = {
                "test": "ghl_connection",
                "status": "❌ FAILED",
                "error": str(e)
            }
            print(f"❌ FAILED: {e}")
            self.errors.append(result)
            return result
    
    async def test_ghl_calendars(self) -> Dict[str, Any]:
        """Test 4: GHL Calendars"""
        print("\n" + "="*70)
        print("TEST 4: GHL Calendars")
        print("="*70)
        
        try:
            calendars = await self.ghl_client.get_calendars()
            calendar_names = [cal.get("name", "").lower() for cal in calendars]
            
            required = ["diagnostic", "proposal"]
            found = []
            missing = []
            
            for req in required:
                if any(req in name for name in calendar_names):
                    found.append(req)
                    print(f"✅ {req.capitalize()} calendar found")
                else:
                    missing.append(req)
                    print(f"❌ {req.capitalize()} calendar NOT found")
            
            result = {
                "test": "ghl_calendars",
                "status": "✅ PASSED" if not missing else "⚠️ WARNINGS",
                "found": found,
                "missing": missing,
                "total_calendars": len(calendars)
            }
            
            return result
        except Exception as e:
            result = {
                "test": "ghl_calendars",
                "status": "❌ FAILED",
                "error": str(e)
            }
            print(f"❌ FAILED: {e}")
            self.errors.append(result)
            return result
    
    async def test_ghl_custom_fields(self) -> Dict[str, Any]:
        """Test 5: GHL Custom Fields"""
        print("\n" + "="*70)
        print("TEST 5: GHL Custom Fields")
        print("="*70)
        
        try:
            fields = await self.ghl_client.get_custom_fields()
            
            required_fields = {
                'ai_call_summary', 'call_transcript_url', 'sms_consent',
                'lead_quality_score', 'equipment_type_tags', 'call_duration',
                'call_type', 'call_outcome', 'vapi_called', 'vapi_call_id',
                'lead_source', 'sms_fallback_sent', 'sms_fallback_date', 'sms_fallback_reason'
            }
            
            found_fields = {}
            for field in fields:
                key = field.get('fieldKey', '')
                if key.startswith('contact.'):
                    short = key.replace('contact.', '')
                    if short in required_fields:
                        found_fields[short] = key
            
            missing = required_fields - set(found_fields.keys())
            
            print(f"Found {len(found_fields)}/{len(required_fields)} required fields")
            
            if missing:
                print(f"⚠️  Missing fields: {missing}")
            
            result = {
                "test": "ghl_custom_fields",
                "status": "✅ PASSED" if not missing else "⚠️ WARNINGS",
                "found": len(found_fields),
                "required": len(required_fields),
                "missing": list(missing)
            }
            
            return result
        except Exception as e:
            result = {
                "test": "ghl_custom_fields",
                "status": "❌ FAILED",
                "error": str(e)
            }
            print(f"❌ FAILED: {e}")
            self.errors.append(result)
            return result
    
    async def test_recent_calls(self) -> Dict[str, Any]:
        """Test 6: Recent Calls Analysis"""
        print("\n" + "="*70)
        print("TEST 6: Recent Calls Analysis")
        print("="*70)
        
        try:
            calls = await self.vapi_client.list_calls(limit=10)
            
            print(f"Found {len(calls)} recent calls")
            
            statuses = {}
            for call in calls:
                status = call.get("status", "unknown")
                statuses[status] = statuses.get(status, 0) + 1
            
            print("\nCall Status Breakdown:")
            for status, count in statuses.items():
                print(f"  {status}: {count}")
            
            result = {
                "test": "recent_calls",
                "status": "✅ PASSED",
                "total_calls": len(calls),
                "statuses": statuses
            }
            
            return result
        except Exception as e:
            result = {
                "test": "recent_calls",
                "status": "❌ FAILED",
                "error": str(e)
            }
            print(f"❌ FAILED: {e}")
            self.errors.append(result)
            return result
    
    async def run_all_tests(self):
        """Run all automated tests"""
        print("\n" + "="*70)
        print("🚀 AUTOMATED TEST SUITE")
        print("="*70)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        tests = [
            self.test_vapi_connection,
            self.test_assistants_configuration,
            self.test_ghl_connection,
            self.test_ghl_calendars,
            self.test_ghl_custom_fields,
            self.test_recent_calls
        ]
        
        for test_func in tests:
            result = await test_func()
            self.results.append(result)
            await asyncio.sleep(1)  # Small delay between tests
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.get("status") == "✅ PASSED")
        warnings = sum(1 for r in self.results if "⚠️" in str(r.get("status", "")))
        failed = sum(1 for r in self.results if "❌" in str(r.get("status", "")))
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"❌ Failed: {failed}")
        
        if self.errors:
            print(f"\n❌ ERRORS:")
            for error in self.errors:
                print(f"  - {error.get('test')}: {error.get('error')}")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = Path(__file__).parent.parent / f"automated_test_results_{timestamp}.json"
        
        with open(report_file, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": total,
                    "passed": passed,
                    "warnings": warnings,
                    "failed": failed
                },
                "results": self.results,
                "errors": self.errors
            }, f, indent=2)
        
        print(f"\n💾 Full results saved to: {report_file}")
        print("="*70)


async def main():
    """Main entry point"""
    api_key = os.getenv("VAPI_API_KEY") or "bee0337d-41cd-49c2-9038-98cd0e18c75b"
    
    tester = AutomatedTester(api_key=api_key)
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())


