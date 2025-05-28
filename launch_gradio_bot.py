#!/usr/bin/env python3
"""
Simple launcher for the Concur Profile Bot Gradio Interface

This script ensures the virtual environment is properly set up and launches the Gradio interface.
"""

import os
import sys
import subprocess

def main():
    """Main launcher function"""
    print("🚀 Concur Profile Bot Gradio Launcher")
    print("=" * 50)
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Not running in a virtual environment")
        print("It's recommended to use a virtual environment")
        print()
    
    # Check if gradio is installed
    try:
        import gradio
        print(f"✅ Gradio {gradio.__version__} is installed")
    except ImportError:
        print("❌ Gradio is not installed")
        print("Installing required packages...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_gradio.txt"])
            print("✅ Packages installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages")
            print("Please run: pip install -r requirements_gradio.txt")
            return 1
    
    # Check for .env_tools file
    if not os.path.exists(".env_tools"):
        print("❌ Error: .env_tools file not found")
        print("Please ensure your environment variables are configured")
        return 1
    
    print("🌐 Starting Gradio interface...")
    print()
    
    # Import and run the Gradio interface
    try:
        from gradio_bot_interface import main as gradio_main
        gradio_main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return 0
    except Exception as e:
        print(f"❌ Error starting interface: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 