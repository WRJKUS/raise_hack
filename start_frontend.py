#!/usr/bin/env python3
"""
Startup script for Leonardo's RFQ Alchemy React frontend
"""

import os
import sys
import subprocess
from pathlib import Path

def check_node_environment():
    """Check if Node.js and npm are installed and available"""
    print("🔍 Checking Node.js environment...")

    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"],
                              capture_output=True, text=True, check=True)
        node_version = result.stdout.strip()
        print(f"✅ Node.js found: {node_version}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js is not installed or not available in PATH")
        print("Please install Node.js from https://nodejs.org/")
        return False

    # Check npm
    try:
        result = subprocess.run(["npm", "--version"],
                              capture_output=True, text=True, check=True)
        npm_version = result.stdout.strip()
        print(f"✅ npm found: {npm_version}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ npm is not installed or not available in PATH")
        print("Please install npm (usually comes with Node.js)")
        return False

    return True

def check_frontend_directory():
    """Check if frontend directory exists"""
    frontend_dir = Path("leonardos-rfq-alchemy-main")

    if not frontend_dir.exists():
        print("❌ Frontend directory 'leonardos-rfq-alchemy-main' not found")
        print("Please ensure you're running this script from the project root directory")
        return False

    if not frontend_dir.is_dir():
        print("❌ 'leonardos-rfq-alchemy-main' exists but is not a directory")
        return False

    # Check for package.json
    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        print("❌ package.json not found in frontend directory")
        print("This doesn't appear to be a valid Node.js project")
        return False

    print("✅ Frontend directory structure validated")
    return True

def install_dependencies():
    """Install Node.js dependencies if node_modules doesn't exist"""
    frontend_dir = Path("leonardos-rfq-alchemy-main")
    node_modules = frontend_dir / "node_modules"

    if node_modules.exists() and node_modules.is_dir():
        print("✅ Dependencies already installed (node_modules exists)")
        return True

    print("📦 Installing Node.js dependencies...")
    print("This may take a few minutes on first run...")

    try:
        # Change to frontend directory
        original_cwd = os.getcwd()
        os.chdir(frontend_dir)

        # Run npm install
        subprocess.run(["npm", "install"], check=True)

        # Change back to original directory
        os.chdir(original_cwd)

        print("✅ Dependencies installed successfully")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("Try running 'npm install' manually in the leonardos-rfq-alchemy-main directory")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during dependency installation: {e}")
        return False
    finally:
        # Ensure we're back in the original directory
        try:
            os.chdir(original_cwd)
        except:
            pass

def check_port_availability():
    """Check if the default port (8080) is available"""
    try:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', 8080))
        print("✅ Port 8080 is available")
        return True
    except OSError:
        print("⚠️  Port 8080 appears to be in use")
        print("The development server will try to use an alternative port")
        return True  # Vite will handle port conflicts automatically

def start_development_server():
    """Start the React development server"""
    print("🚀 Starting React development server...")
    print("📍 Frontend will be available at: http://localhost:8080")
    print("🔄 Press Ctrl+C to stop the server")
    print("⏳ Starting up... (this may take a moment)")

    try:
        # Change to frontend directory
        frontend_dir = Path("leonardos-rfq-alchemy-main")
        original_cwd = os.getcwd()
        os.chdir(frontend_dir)

        # Start the development server
        subprocess.run(["npm", "run", "dev"])

    except KeyboardInterrupt:
        print("\n👋 Development server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start development server: {e}")
        print("Try running 'npm run dev' manually in the leonardos-rfq-alchemy-main directory")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        # Ensure we're back in the original directory
        try:
            os.chdir(original_cwd)
        except:
            pass

def main():
    """Main startup function"""
    # Check for help flag
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        print("⚛️  Leonardo's RFQ Alchemy - React Frontend Startup")
        print("=" * 50)
        print("This script starts the React development server for the frontend.")
        print("\nWhat it does:")
        print("• Checks if Node.js and npm are installed")
        print("• Validates the frontend directory structure")
        print("• Installs dependencies if node_modules is missing")
        print("• Starts the Vite development server on http://localhost:8080")
        print("\nUsage:")
        print("  python start_frontend.py")
        print("  python start_frontend.py --help")
        print("\nRequirements:")
        print("• Node.js 16+ and npm")
        print("• Run from the project root directory")
        return

    print("⚛️  Leonardo's RFQ Alchemy - React Frontend Startup")
    print("=" * 50)

    # Check Node.js environment
    if not check_node_environment():
        sys.exit(1)

    # Check frontend directory structure
    if not check_frontend_directory():
        sys.exit(1)

    # Install dependencies if needed
    if not install_dependencies():
        print("⚠️  Continuing without installing dependencies...")
        print("   You may need to run 'npm install' manually")

    # Check port availability (informational)
    check_port_availability()

    # Start development server
    start_development_server()

if __name__ == "__main__":
    main()
