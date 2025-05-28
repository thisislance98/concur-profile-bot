#!/usr/bin/env python3
"""
Deployment helper script for Concur Profile Bot
Supports multiple deployment platforms
"""

import os
import sys
import subprocess
import json

def check_requirements():
    """Check if all required files exist"""
    required_files = [
        'gradio_bot_interface.py',
        'requirements.txt',
        'README.md'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files present")
    return True

def check_environment_variables():
    """Check if required environment variables are set"""
    required_vars = [
        'CONCUR_CLIENT_ID',
        'CONCUR_CLIENT_SECRET', 
        'CONCUR_USERNAME',
        'CONCUR_PASSWORD',
        'ANTHROPIC_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Make sure to set these in your deployment platform's settings")
        return False
    
    print("✅ All environment variables set")
    return True

def deploy_to_huggingface():
    """Deploy to Hugging Face Spaces using gradio deploy"""
    print("🚀 Deploying to Hugging Face Spaces...")
    
    try:
        # Check if gradio is installed
        subprocess.run(['gradio', '--version'], check=True, capture_output=True)
        
        # Run gradio deploy
        result = subprocess.run(['gradio', 'deploy'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Successfully deployed to Hugging Face Spaces!")
            print(result.stdout)
        else:
            print("❌ Deployment failed:")
            print(result.stderr)
            
    except subprocess.CalledProcessError:
        print("❌ Gradio not found. Install with: pip install gradio")
    except Exception as e:
        print(f"❌ Deployment error: {e}")

def deploy_to_railway():
    """Deploy to Railway using Railway CLI"""
    print("🚂 Deploying to Railway...")
    
    try:
        # Check if railway CLI is installed
        result = subprocess.run(['railway', '--version'], check=True, capture_output=True)
        print("✅ Railway CLI found")
        
        # Check if already logged in
        try:
            subprocess.run(['railway', 'whoami'], check=True, capture_output=True)
            print("✅ Already logged in to Railway")
        except subprocess.CalledProcessError:
            print("🔐 Please log in to Railway first:")
            print("Run: railway login")
            return
        
        # Initialize or link project
        print("🔗 Setting up Railway project...")
        try:
            # Try to link to existing project
            subprocess.run(['railway', 'link'], check=True)
        except subprocess.CalledProcessError:
            # Create new project if linking fails
            print("📝 Creating new Railway project...")
            subprocess.run(['railway', 'init'], check=True)
        
        # Deploy the application
        print("🚀 Deploying to Railway...")
        result = subprocess.run(['railway', 'up'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Successfully deployed to Railway!")
            print(result.stdout)
            print("\n🌐 Your app should be available at your Railway project URL")
        else:
            print("❌ Railway deployment failed:")
            print(result.stderr)
            
    except subprocess.CalledProcessError:
        print("❌ Railway CLI not found. Install it first:")
        print("\n📦 Installation options:")
        print("• Homebrew (macOS): brew install railway")
        print("• npm: npm install -g @railway/cli")
        print("• Bash: bash <(curl -fsSL cli.new)")
        print("• Scoop (Windows): scoop install railway")
    except Exception as e:
        print(f"❌ Railway deployment error: {e}")

def create_railway_config():
    """Create railway.json configuration file"""
    railway_config = {
        "build": {
            "builder": "NIXPACKS"
        },
        "deploy": {
            "startCommand": "python gradio_bot_interface.py",
            "healthcheckPath": "/",
            "healthcheckTimeout": 100,
            "restartPolicyType": "ON_FAILURE",
            "restartPolicyMaxRetries": 10
        }
    }
    
    with open('railway.json', 'w') as f:
        json.dump(railway_config, f, indent=2)
    
    print("✅ Created railway.json configuration file")

def create_dockerfile():
    """Create a Dockerfile for container deployment"""
    dockerfile_content = """FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose the port Gradio runs on
EXPOSE 7860

# Set environment variables for Gradio
ENV GRADIO_SERVER_NAME="0.0.0.0"
ENV GRADIO_SERVER_PORT="7860"

# Run the application
CMD ["python", "gradio_bot_interface.py"]
"""
    
    with open('Dockerfile', 'w') as f:
        f.write(dockerfile_content)
    
    print("✅ Created Dockerfile for container deployment")

def create_docker_compose():
    """Create docker-compose.yml for local development"""
    compose_content = """version: '3.8'

services:
  concur-bot:
    build: .
    ports:
      - "7860:7860"
    environment:
      - CONCUR_CLIENT_ID=${CONCUR_CLIENT_ID}
      - CONCUR_CLIENT_SECRET=${CONCUR_CLIENT_SECRET}
      - CONCUR_USERNAME=${CONCUR_USERNAME}
      - CONCUR_PASSWORD=${CONCUR_PASSWORD}
      - CONCUR_BASE_URL=${CONCUR_BASE_URL:-https://us2.api.concursolutions.com}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - .:/app
    restart: unless-stopped
"""
    
    with open('docker-compose.yml', 'w') as f:
        f.write(compose_content)
    
    print("✅ Created docker-compose.yml for local development")

def show_deployment_options():
    """Show available deployment options"""
    print("""
🚀 Deployment Options:

1. Hugging Face Spaces (Recommended - Free)
   - Run: python deploy.py --huggingface
   - Or: gradio deploy

2. Railway (Easy CLI deployment)
   - Install: brew install railway (or npm install -g @railway/cli)
   - Run: python deploy.py --railway
   - Or: railway login && railway up

3. Docker Container
   - Run: python deploy.py --docker
   - Then: docker build -t concur-bot . && docker run -p 7860:7860 concur-bot

4. Render (Free tier available)
   - Push to GitHub  
   - Connect Render to your repo
   - Set environment variables in Render dashboard

5. Vercel (Serverless)
   - Push to GitHub
   - Connect Vercel to your repo
   - Configure build settings

6. Local Development
   - Run: python gradio_bot_interface.py
   - Access: http://localhost:7860

🔧 Railway CLI Commands:
   railway login          # Authenticate with Railway
   railway init           # Create new project
   railway link           # Link to existing project
   railway up             # Deploy your app
   railway logs           # View deployment logs
   railway open           # Open your app in browser
   railway run <cmd>      # Run commands with Railway env vars
""")

def main():
    """Main deployment function"""
    print("🤖 Concur Profile Bot Deployment Helper")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check environment variables (warning only)
    check_environment_variables()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        option = sys.argv[1]
        
        if option == '--huggingface' or option == '-hf':
            deploy_to_huggingface()
        elif option == '--railway' or option == '-r':
            create_railway_config()
            deploy_to_railway()
        elif option == '--docker' or option == '-d':
            create_dockerfile()
            create_docker_compose()
            print("🐳 Docker files created. Build with: docker build -t concur-bot .")
        elif option == '--help' or option == '-h':
            show_deployment_options()
        else:
            print(f"Unknown option: {option}")
            show_deployment_options()
    else:
        show_deployment_options()

if __name__ == "__main__":
    main() 