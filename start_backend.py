#!/usr/bin/env python3
"""
Startup script for Leonardo's RFQ Alchemy FastAPI backend
"""

import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ["GROQ_API_KEY", "OPENAI_API_KEY"]
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these environment variables or create a .env file")
        print("You can copy .env.example to .env and fill in your API keys")
        return False

    print("✅ Environment variables configured")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                      check=True, capture_output=True, text=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ["uploads", "chroma_proposal_db"]

    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Created directory: {directory}")

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting FastAPI server...")
    print("📍 API will be available at: http://localhost:8000")
    print("📖 API documentation at: http://localhost:8000/api/docs")
    print("🔄 Press Ctrl+C to stop the server")

    try:
        # Change to the project root directory
        os.chdir(Path(__file__).parent)

        # Start uvicorn server
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "backend.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--log-level", "info"
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")

def main():
    """Main startup function"""
    print("🎭 Leonardo's RFQ Alchemy - FastAPI Backend Startup")
    print("=" * 50)

    # Check environment
    if not check_environment():
        sys.exit(1)

    # Install dependencies
    # if not install_dependencies():
    #     print("⚠️  Continuing without installing dependencies...")
    #     print("   Make sure you have installed the requirements manually")

    # Create directories
    create_directories()

    # Start server
    start_server()

if __name__ == "__main__":
    main()
