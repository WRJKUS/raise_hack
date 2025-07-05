#!/usr/bin/env python3
"""
LangGraph Proposal Analyzer - Startup Script

This script provides a convenient way to start the Chainlit application
with proper environment setup and configuration validation.
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

def check_environment():
    """Check if required environment variables are set."""
    load_dotenv()
    
    required_vars = ['GROQ_API_KEY', 'OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   • {var}")
        print("\n💡 Please set these variables in your .env file or environment.")
        print("   You can copy .env.example to .env and fill in your API keys.")
        return False
    
    print("✅ Environment variables configured correctly!")
    return True

def check_dependencies():
    """Check if required packages are installed."""
    try:
        import chainlit
        import langgraph
        import langchain_chroma
        import langchain_groq
        print("✅ All required packages are installed!")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("\n💡 Please install dependencies:")
        print("   pip install -r requirements.txt")
        return False

def create_directories():
    """Create necessary directories."""
    directories = [
        'chroma_proposal_db',
        'public',
        '.chainlit'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Directories created/verified!")

def main():
    """Main startup function."""
    print("🚀 Starting LangGraph Proposal Analyzer...")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Start Chainlit
    print("\n🌟 Launching Chainlit application...")
    print("📱 The app will be available at: http://localhost:8000")
    print("🔄 Auto-reload is enabled for development")
    print("\n" + "=" * 50)
    
    try:
        # Run chainlit with auto-reload
        subprocess.run([
            sys.executable, "-m", "chainlit", "run", "app.py", 
            "-w", "--port", "8000"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error starting Chainlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
