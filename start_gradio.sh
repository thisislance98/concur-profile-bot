#!/bin/bash

# Concur Profile Bot Gradio Interface Launcher
# This script activates the virtual environment and starts the Gradio interface

echo "🚀 Starting Concur Profile Bot Gradio Interface..."
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please create one with: python -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if .env_tools exists
if [ ! -f ".env_tools" ]; then
    echo "❌ .env_tools file not found!"
    echo "Please create it with your API credentials"
    exit 1
fi

# Install dependencies if needed
echo "📦 Checking dependencies..."
python -c "import gradio" 2>/dev/null || {
    echo "📥 Installing Gradio dependencies..."
    pip install -r requirements_gradio.txt
}

# Start the interface
echo "🌐 Starting Gradio interface..."
echo "📱 The interface will open in your browser at http://localhost:7860"
echo "🛑 Press Ctrl+C to stop the interface"
echo ""

python launch_gradio_bot.py 