#!/usr/bin/env python3
"""
Demo Script for Concur Profile Bot Gradio Interface

This script demonstrates how to use the Gradio interface programmatically and provides
example usage patterns.
"""

import time
import requests
import json
from datetime import datetime

def test_gradio_api():
    """Test the Gradio API endpoints"""
    base_url = "http://localhost:7860"
    
    print("🧪 Testing Gradio API Endpoints")
    print("=" * 50)
    
    # Test if the interface is running
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Gradio interface is running")
        else:
            print(f"❌ Interface returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Gradio interface")
        print("Please make sure the interface is running on http://localhost:7860")
        return False
    
    return True

def demo_chat_examples():
    """Demonstrate example chat interactions"""
    print("\n💬 Example Chat Interactions")
    print("=" * 50)
    
    examples = [
        {
            "title": "Get Profile Information",
            "prompt": "Show me my current profile information",
            "description": "Retrieves and displays the user's complete profile"
        },
        {
            "title": "Update Job Title",
            "prompt": "Update my job title to Senior Software Engineer",
            "description": "Updates the job title field in the profile"
        },
        {
            "title": "Set Travel Preferences",
            "prompt": "I prefer window seats and vegetarian meals on flights",
            "description": "Updates air travel preferences for seat and meal"
        },
        {
            "title": "Hotel Preferences",
            "prompt": "Set my hotel preference to king size beds and non-smoking rooms",
            "description": "Updates hotel room preferences"
        },
        {
            "title": "Car Rental Preferences",
            "prompt": "I prefer compact automatic cars for rentals",
            "description": "Updates car rental preferences"
        },
        {
            "title": "List Recent Profiles",
            "prompt": "Show me profiles that were updated in the last 7 days",
            "description": "Lists profiles with recent modifications"
        },
        {
            "title": "Complex Multi-step Request",
            "prompt": "Update my job title to Lead Engineer and set my airline preference to aisle seats",
            "description": "Performs multiple updates in a single request"
        },
        {
            "title": "Contact Information",
            "prompt": "Update my work phone number to +1-555-123-4567",
            "description": "Updates contact information"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['title']}")
        print(f"   Prompt: \"{example['prompt']}\"")
        print(f"   Description: {example['description']}")
    
    print("\n💡 Tips for Using the Interface:")
    print("- Use natural language - the bot understands conversational requests")
    print("- Be specific about what you want to update")
    print("- You can combine multiple requests in one message")
    print("- Check the status panel if you encounter issues")
    print("- Use quick action buttons for common tasks")

def demo_features():
    """Demonstrate interface features"""
    print("\n🌟 Interface Features")
    print("=" * 50)
    
    features = [
        {
            "name": "Chat Interface",
            "description": "Natural language conversation with the bot",
            "usage": "Type your requests in the message box and press Enter or click Send"
        },
        {
            "name": "Quick Actions",
            "description": "One-click buttons for common tasks",
            "usage": "Click the buttons to auto-fill common prompts"
        },
        {
            "name": "Status Panel",
            "description": "Real-time system status monitoring",
            "usage": "Check connection status and refresh when needed"
        },
        {
            "name": "Conversation History",
            "description": "Persistent chat history during your session",
            "usage": "Scroll up to see previous interactions"
        },
        {
            "name": "Clear Chat",
            "description": "Reset the conversation",
            "usage": "Click 'Clear Chat' to start fresh"
        },
        {
            "name": "Tool Integration",
            "description": "Seamless integration with Concur Profile SDK",
            "usage": "The bot automatically uses appropriate tools based on your requests"
        }
    ]
    
    for feature in features:
        print(f"\n📋 {feature['name']}")
        print(f"   {feature['description']}")
        print(f"   Usage: {feature['usage']}")

def demo_troubleshooting():
    """Demonstrate troubleshooting steps"""
    print("\n🔧 Troubleshooting Guide")
    print("=" * 50)
    
    issues = [
        {
            "problem": "Bot not initialized error",
            "solutions": [
                "Check the Status Panel for specific error messages",
                "Verify .env_tools file contains all required credentials",
                "Click 'Refresh Status' to retry connections",
                "Restart the interface if needed"
            ]
        },
        {
            "problem": "API connection errors",
            "solutions": [
                "Verify your Anthropic API key is valid and has credits",
                "Check Concur credentials and permissions",
                "Ensure network connectivity",
                "Check for any firewall or proxy issues"
            ]
        },
        {
            "problem": "Slow responses",
            "solutions": [
                "Check your internet connection",
                "Verify API rate limits aren't exceeded",
                "Try simpler requests first",
                "Clear chat history if it's very long"
            ]
        },
        {
            "problem": "Interface won't load",
            "solutions": [
                "Ensure Gradio is properly installed",
                "Check if port 7860 is available",
                "Try restarting the launcher script",
                "Check console output for error messages"
            ]
        }
    ]
    
    for issue in issues:
        print(f"\n❌ Problem: {issue['problem']}")
        print("   Solutions:")
        for solution in issue['solutions']:
            print(f"   • {solution}")

def main():
    """Main demo function"""
    print("🎭 Concur Profile Bot Gradio Interface Demo")
    print("=" * 60)
    print(f"Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test if interface is running
    if not test_gradio_api():
        print("\n🚀 To start the interface, run:")
        print("   python launch_gradio_bot.py")
        print("\nOr manually:")
        print("   python gradio_bot_interface.py")
        return
    
    # Show demo content
    demo_chat_examples()
    demo_features()
    demo_troubleshooting()
    
    print("\n" + "=" * 60)
    print("🎉 Demo Complete!")
    print("\n🌐 Access the interface at: http://localhost:7860")
    print("📚 For more information, see: GRADIO_README.md")
    print("\n💡 Try the example prompts in the web interface!")

if __name__ == "__main__":
    main() 