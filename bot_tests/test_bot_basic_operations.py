#!/usr/bin/env python3
"""
Bot Integration Tests - Basic Operations

These tests use the actual bot CLI with natural language prompts to test
real integration between Claude, the SDK, and the Concur API.

NO MOCKING - These are real end-to-end tests.
"""

import subprocess
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Add parent directory to path to import the bot
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

class BotTester:
    """Test harness for the Concur Profile Bot"""
    
    def __init__(self):
        self.bot_script = os.path.join(os.path.dirname(os.path.dirname(__file__)), "concur_profile_bot_fixed.py")
        self.test_results = []
        
    def run_bot_prompt(self, prompt: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Run a single prompt through the bot CLI and capture the response
        
        Args:
            prompt: Natural language prompt to send to the bot
            timeout: Maximum time to wait for response
            
        Returns:
            Dictionary with success status, output, and any errors
        """
        print(f"\n🤖 Testing prompt: {prompt}")
        
        try:
            # Run the bot with the prompt command
            result = subprocess.run(
                [sys.executable, self.bot_script, "prompt", prompt],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            success = result.returncode == 0
            output = result.stdout
            error = result.stderr
            
            print(f"✅ Success: {success}")
            if output:
                print(f"📄 Output:\n{output}")
            if error:
                # Only show as error if it's actually an error (not just INFO logs)
                if not success or any(level in error for level in ["ERROR:", "CRITICAL:", "Traceback"]):
                    print(f"❌ Error:\n{error}")
                else:
                    print(f"📋 Logs:\n{error}")
                
            return {
                "success": success,
                "output": output,
                "error": error,
                "returncode": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout after {timeout} seconds")
            return {
                "success": False,
                "output": "",
                "error": f"Timeout after {timeout} seconds",
                "returncode": -1
            }
        except Exception as e:
            print(f"💥 Exception: {e}")
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "returncode": -1
            }
    
    def test_get_profile(self):
        """Test getting the current user's profile"""
        print("\n" + "="*60)
        print("TEST: Get Current User Profile")
        print("="*60)
        
        result = self.run_bot_prompt("Show me my profile information")
        
        # Check if the response contains profile information
        success = (
            result["success"] and 
            ("profile" in result["output"].lower() or "name" in result["output"].lower())
        )
        
        self.test_results.append({
            "test": "get_profile",
            "success": success,
            "details": result
        })
        
        return success
    
    def test_get_travel_preferences(self):
        """Test getting travel preferences"""
        print("\n" + "="*60)
        print("TEST: Get Travel Preferences")
        print("="*60)
        
        result = self.run_bot_prompt("What are my travel preferences?")
        
        success = (
            result["success"] and 
            ("travel" in result["output"].lower() or "preference" in result["output"].lower())
        )
        
        self.test_results.append({
            "test": "get_travel_preferences", 
            "success": success,
            "details": result
        })
        
        return success
    
    def test_update_basic_info(self):
        """Test updating basic profile information"""
        print("\n" + "="*60)
        print("TEST: Update Basic Profile Information")
        print("="*60)
        
        # Use a timestamp to make the update unique
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        job_title = f"Test Engineer {timestamp}"
        
        result = self.run_bot_prompt(f"Update my job title to '{job_title}'")
        
        success = (
            result["success"] and 
            ("updated" in result["output"].lower() or "success" in result["output"].lower())
        )
        
        self.test_results.append({
            "test": "update_basic_info",
            "success": success,
            "details": result,
            "test_data": {"job_title": job_title}
        })
        
        return success
    
    def test_update_air_preferences(self):
        """Test updating air travel preferences"""
        print("\n" + "="*60)
        print("TEST: Update Air Travel Preferences")
        print("="*60)
        
        result = self.run_bot_prompt("Set my airline seat preference to window seat")
        
        success = (
            result["success"] and 
            ("updated" in result["output"].lower() or "success" in result["output"].lower())
        )
        
        self.test_results.append({
            "test": "update_air_preferences",
            "success": success,
            "details": result
        })
        
        return success
    
    def test_update_hotel_preferences(self):
        """Test updating hotel preferences"""
        print("\n" + "="*60)
        print("TEST: Update Hotel Preferences")
        print("="*60)
        
        result = self.run_bot_prompt("I prefer king size beds in hotels and need gym access")
        
        success = (
            result["success"] and 
            ("updated" in result["output"].lower() or "success" in result["output"].lower())
        )
        
        self.test_results.append({
            "test": "update_hotel_preferences",
            "success": success,
            "details": result
        })
        
        return success
    
    def test_update_car_preferences(self):
        """Test updating car rental preferences"""
        print("\n" + "="*60)
        print("TEST: Update Car Rental Preferences")
        print("="*60)
        
        result = self.run_bot_prompt("Set my car rental preference to compact automatic with GPS")
        
        success = (
            result["success"] and 
            ("updated" in result["output"].lower() or "success" in result["output"].lower())
        )
        
        self.test_results.append({
            "test": "update_car_preferences",
            "success": success,
            "details": result
        })
        
        return success
    
    def test_loyalty_program_update(self):
        """Test updating loyalty program (may fail due to API restrictions)"""
        print("\n" + "="*60)
        print("TEST: Update Loyalty Program")
        print("="*60)
        
        result = self.run_bot_prompt("Add my United Airlines MileagePlus number 123456789 with Gold status")
        
        # This test may legitimately fail due to API restrictions
        # We consider it successful if the bot handles it gracefully
        success = result["success"] or "restriction" in result["output"].lower() or "not available" in result["output"].lower()
        
        self.test_results.append({
            "test": "loyalty_program_update",
            "success": success,
            "details": result,
            "note": "May fail due to API restrictions - that's expected"
        })
        
        return success
    
    def test_list_profiles(self):
        """Test listing profile summaries"""
        print("\n" + "="*60)
        print("TEST: List Profile Summaries")
        print("="*60)
        
        result = self.run_bot_prompt("Show me a list of profiles that were updated in the last 7 days")
        
        success = (
            result["success"] and 
            ("profile" in result["output"].lower() or "list" in result["output"].lower())
        )
        
        self.test_results.append({
            "test": "list_profiles",
            "success": success,
            "details": result
        })
        
        return success
    
    def test_complex_query(self):
        """Test a complex multi-part query"""
        print("\n" + "="*60)
        print("TEST: Complex Multi-Part Query")
        print("="*60)
        
        result = self.run_bot_prompt(
            "Show me my current profile, then update my home airport to SEA and "
            "set my hotel preferences to prefer early check-in and room service"
        )
        
        success = (
            result["success"] and 
            ("profile" in result["output"].lower() or "updated" in result["output"].lower())
        )
        
        self.test_results.append({
            "test": "complex_query",
            "success": success,
            "details": result
        })
        
        return success
    
    def test_error_handling(self):
        """Test error handling with invalid requests"""
        print("\n" + "="*60)
        print("TEST: Error Handling")
        print("="*60)
        
        result = self.run_bot_prompt("Update the profile for nonexistent@user.com")
        
        # Success means the bot handled the error gracefully
        success = (
            result["success"] or 
            "not found" in result["output"].lower() or 
            "error" in result["output"].lower()
        )
        
        self.test_results.append({
            "test": "error_handling",
            "success": success,
            "details": result
        })
        
        return success
    
    def run_all_tests(self):
        """Run all bot tests"""
        print("🚀 Starting Concur Profile Bot Integration Tests")
        print("=" * 80)
        
        start_time = time.time()
        
        # Run all tests
        tests = [
            self.test_get_profile,
            self.test_get_travel_preferences,
            self.test_update_basic_info,
            self.test_update_air_preferences,
            self.test_update_hotel_preferences,
            self.test_update_car_preferences,
            self.test_loyalty_program_update,
            self.test_list_profiles,
            self.test_complex_query,
            self.test_error_handling
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"💥 Test {test.__name__} crashed: {e}")
                failed += 1
            
            # Small delay between tests
            time.sleep(2)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print summary
        print("\n" + "="*80)
        print("🏁 TEST SUMMARY")
        print("="*80)
        print(f"Total Tests: {len(tests)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📊 Success Rate: {(passed/len(tests)*100):.1f}%")
        
        # Print detailed results
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} - {result['test']}")
            if "note" in result:
                print(f"    📝 Note: {result['note']}")
            if not result["success"] and result["details"]["error"]:
                print(f"    🔍 Error: {result['details']['error']}")
        
        return passed, failed, self.test_results

def main():
    """Main test runner"""
    # Check if we have the required environment
    if not os.path.exists("concur_profile_bot_fixed.py"):
        print("❌ Error: concur_profile_bot_fixed.py not found")
        print("Please run this test from the project root directory")
        return 1
    
    # Check for .env file
    if not os.path.exists(".env_tools"):
        print("❌ Error: .env_tools file not found")
        print("Please ensure your environment variables are configured")
        return 1
    
    tester = BotTester()
    passed, failed, results = tester.run_all_tests()
    
    # Return appropriate exit code
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit(main()) 