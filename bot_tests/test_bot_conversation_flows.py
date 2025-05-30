#!/usr/bin/env python3
"""
Bot Integration Tests - Conversation Flows

These tests focus on natural language understanding and conversational flows
with the Concur Profile Bot. Tests realistic user interactions.

NO MOCKING - These are real end-to-end conversation tests.
"""

import subprocess
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

class ConversationTester:
    """Test harness for conversational flows with the bot"""
    
    def __init__(self):
        self.bot_script = os.path.join(os.path.dirname(os.path.dirname(__file__)), "concur_profile_bot.py")
        self.test_results = []
        
    def run_bot_prompt(self, prompt: str, timeout: int = 45) -> Dict[str, Any]:
        """Run a single prompt through the bot CLI"""
        print(f"\n💬 User: {prompt}")
        
        try:
            result = subprocess.run(
                [sys.executable, self.bot_script, "prompt", prompt],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            success = result.returncode == 0
            output = result.stdout
            error = result.stderr
            
            if output:
                print(f"🤖 Bot: {output}")
            if error and not success:
                print(f"❌ Error: {error}")
                
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
    
    def test_casual_profile_inquiry(self):
        """Test casual ways of asking for profile information"""
        print("\n" + "="*70)
        print("TEST: Casual Profile Inquiry")
        print("="*70)
        
        casual_prompts = [
            "Who am I?",
            "Tell me about myself",
            "What's in my profile?",
            "Show me my info",
            "What do you know about me?"
        ]
        
        success_count = 0
        for prompt in casual_prompts:
            result = self.run_bot_prompt(prompt)
            if (result["success"] and 
                ("profile" in result["output"].lower() or 
                 "name" in result["output"].lower() or
                 "information" in result["output"].lower())):
                success_count += 1
            time.sleep(1)
        
        success = success_count >= len(casual_prompts) // 2  # At least half should work
        
        self.test_results.append({
            "test": "casual_profile_inquiry",
            "success": success,
            "details": f"Successful prompts: {success_count}/{len(casual_prompts)}"
        })
        
        return success
    
    def test_travel_preference_variations(self):
        """Test different ways of expressing travel preferences"""
        print("\n" + "="*70)
        print("TEST: Travel Preference Variations")
        print("="*70)
        
        preference_prompts = [
            "I like window seats on planes",
            "Set my airline preference to aisle seat",
            "I prefer king beds in hotels",
            "I want automatic transmission cars",
            "I need GPS in my rental cars",
            "I don't want smoking rooms",
            "I like early check-in at hotels"
        ]
        
        success_count = 0
        for prompt in preference_prompts:
            result = self.run_bot_prompt(prompt)
            if (result["success"] and 
                ("updated" in result["output"].lower() or 
                 "set" in result["output"].lower() or
                 "preference" in result["output"].lower())):
                success_count += 1
            time.sleep(2)  # Longer delay for updates
        
        success = success_count >= len(preference_prompts) // 2
        
        self.test_results.append({
            "test": "travel_preference_variations",
            "success": success,
            "details": f"Successful updates: {success_count}/{len(preference_prompts)}"
        })
        
        return success
    
    def test_complex_travel_requests(self):
        """Test complex, multi-part travel preference requests"""
        print("\n" + "="*70)
        print("TEST: Complex Travel Requests")
        print("="*70)
        
        complex_prompts = [
            "I'm a business traveler who prefers window seats, king beds, and compact cars with GPS",
            "Set up my travel profile: I like aisle seats, need gym access at hotels, and want automatic cars",
            "Update my preferences - I want vegetarian meals on flights and early check-in at hotels",
            "I'm traveling for work: set my home airport to LAX and prefer non-smoking everything"
        ]
        
        success_count = 0
        for prompt in complex_prompts:
            result = self.run_bot_prompt(prompt, timeout=60)  # Longer timeout for complex requests
            if (result["success"] and 
                ("updated" in result["output"].lower() or 
                 "set" in result["output"].lower() or
                 "preference" in result["output"].lower())):
                success_count += 1
            time.sleep(3)  # Longer delay for complex updates
        
        success = success_count >= len(complex_prompts) // 2
        
        self.test_results.append({
            "test": "complex_travel_requests",
            "success": success,
            "details": f"Successful complex requests: {success_count}/{len(complex_prompts)}"
        })
        
        return success
    
    def test_profile_update_variations(self):
        """Test different ways of updating profile information"""
        print("\n" + "="*70)
        print("TEST: Profile Update Variations")
        print("="*70)
        
        timestamp = datetime.now().strftime("%H%M%S")
        
        update_prompts = [
            f"Change my job title to Software Engineer {timestamp}",
            f"My new title is Data Scientist {timestamp}",
            f"Update my position to Product Manager {timestamp}",
            f"I'm now a DevOps Engineer {timestamp}",
            f"Set my role as QA Engineer {timestamp}"
        ]
        
        success_count = 0
        for prompt in update_prompts:
            result = self.run_bot_prompt(prompt)
            if (result["success"] and 
                ("updated" in result["output"].lower() or 
                 "changed" in result["output"].lower() or
                 "set" in result["output"].lower())):
                success_count += 1
            time.sleep(2)
        
        success = success_count >= len(update_prompts) // 2
        
        self.test_results.append({
            "test": "profile_update_variations",
            "success": success,
            "details": f"Successful updates: {success_count}/{len(update_prompts)}"
        })
        
        return success
    
    def test_question_variations(self):
        """Test different ways of asking questions"""
        print("\n" + "="*70)
        print("TEST: Question Variations")
        print("="*70)
        
        question_prompts = [
            "What's my current job title?",
            "Where do I work?",
            "What are my travel settings?",
            "Do I have any loyalty programs?",
            "What's my home airport?",
            "How am I set up for hotels?",
            "What car preferences do I have?"
        ]
        
        success_count = 0
        for prompt in question_prompts:
            result = self.run_bot_prompt(prompt)
            if result["success"] and len(result["output"].strip()) > 10:  # Got a substantial response
                success_count += 1
            time.sleep(1)
        
        success = success_count >= len(question_prompts) // 2
        
        self.test_results.append({
            "test": "question_variations",
            "success": success,
            "details": f"Successful questions: {success_count}/{len(question_prompts)}"
        })
        
        return success
    
    def test_polite_requests(self):
        """Test polite and conversational requests"""
        print("\n" + "="*70)
        print("TEST: Polite Requests")
        print("="*70)
        
        polite_prompts = [
            "Could you please show me my profile?",
            "Would you mind updating my travel preferences?",
            "I'd like to see my current settings, please",
            "Can you help me change my job title?",
            "Please set my airline preference to window seat"
        ]
        
        success_count = 0
        for prompt in polite_prompts:
            result = self.run_bot_prompt(prompt)
            if result["success"]:
                success_count += 1
            time.sleep(2)
        
        success = success_count >= len(polite_prompts) // 2
        
        self.test_results.append({
            "test": "polite_requests",
            "success": success,
            "details": f"Successful polite requests: {success_count}/{len(polite_prompts)}"
        })
        
        return success
    
    def test_ambiguous_requests(self):
        """Test how the bot handles ambiguous requests"""
        print("\n" + "="*70)
        print("TEST: Ambiguous Requests")
        print("="*70)
        
        ambiguous_prompts = [
            "Change my preferences",
            "Update my info",
            "Set my travel stuff",
            "Fix my profile",
            "I need to change something"
        ]
        
        success_count = 0
        for prompt in ambiguous_prompts:
            result = self.run_bot_prompt(prompt)
            # Success means the bot responded (even if asking for clarification)
            if result["success"] and len(result["output"].strip()) > 10:
                success_count += 1
            time.sleep(1)
        
        success = success_count >= len(ambiguous_prompts) // 2
        
        self.test_results.append({
            "test": "ambiguous_requests",
            "success": success,
            "details": f"Handled ambiguous requests: {success_count}/{len(ambiguous_prompts)}"
        })
        
        return success
    
    def test_error_scenarios(self):
        """Test various error scenarios and recovery"""
        print("\n" + "="*70)
        print("TEST: Error Scenarios")
        print("="*70)
        
        error_prompts = [
            "Update profile for fake@user.com",
            "Set my airline to XYZ Airlines",  # Invalid airline
            "Change my seat preference to middle-back-window",  # Invalid preference
            "Add loyalty program for Fake Airlines",
            "Set my home airport to INVALID"
        ]
        
        success_count = 0
        for prompt in error_prompts:
            result = self.run_bot_prompt(prompt)
            # Success means the bot handled the error gracefully (responded with error message)
            if (result["success"] or 
                "error" in result["output"].lower() or 
                "not found" in result["output"].lower() or
                "invalid" in result["output"].lower()):
                success_count += 1
            time.sleep(1)
        
        success = success_count >= len(error_prompts) // 2
        
        self.test_results.append({
            "test": "error_scenarios",
            "success": success,
            "details": f"Gracefully handled errors: {success_count}/{len(error_prompts)}"
        })
        
        return success
    
    def test_context_understanding(self):
        """Test contextual understanding in requests"""
        print("\n" + "="*70)
        print("TEST: Context Understanding")
        print("="*70)
        
        contextual_prompts = [
            "I'm going on a business trip next week, set me up for travel",
            "I have back problems, so I need aisle seats and firm beds",
            "I'm a vegetarian and prefer eco-friendly options",
            "I travel internationally a lot, set appropriate preferences",
            "I'm a frequent flyer with status, update my profile accordingly"
        ]
        
        success_count = 0
        for prompt in contextual_prompts:
            result = self.run_bot_prompt(prompt, timeout=60)
            if result["success"] and len(result["output"].strip()) > 20:  # Got a substantial response
                success_count += 1
            time.sleep(3)
        
        success = success_count >= len(contextual_prompts) // 3  # Lower threshold for complex context
        
        self.test_results.append({
            "test": "context_understanding",
            "success": success,
            "details": f"Understood context: {success_count}/{len(contextual_prompts)}"
        })
        
        return success
    
    def run_all_tests(self):
        """Run all conversation flow tests"""
        print("🗣️  Starting Concur Profile Bot Conversation Tests")
        print("=" * 80)
        
        start_time = time.time()
        
        # Run all tests
        tests = [
            self.test_casual_profile_inquiry,
            self.test_travel_preference_variations,
            self.test_complex_travel_requests,
            self.test_profile_update_variations,
            self.test_question_variations,
            self.test_polite_requests,
            self.test_ambiguous_requests,
            self.test_error_scenarios,
            self.test_context_understanding
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
            
            # Delay between test groups
            time.sleep(3)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print summary
        print("\n" + "="*80)
        print("🏁 CONVERSATION TEST SUMMARY")
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
            if "details" in result:
                print(f"    📝 Details: {result['details']}")
        
        return passed, failed, self.test_results

def main():
    """Main test runner"""
    # Check if we have the required environment
    if not os.path.exists("concur_profile_bot.py"):
        print("❌ Error: concur_profile_bot.py not found")
        print("Please run this test from the project root directory")
        return 1
    
    # Check for .env file
    if not os.path.exists(".env_tools"):
        print("❌ Error: .env_tools file not found")
        print("Please ensure your environment variables are configured")
        return 1
    
    tester = ConversationTester()
    passed, failed, results = tester.run_all_tests()
    
    # Return appropriate exit code
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit(main()) 