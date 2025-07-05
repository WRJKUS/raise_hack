#!/usr/bin/env python3
"""
Test script for LangGraph Proposal Analyzer

This script performs basic validation of the application components
without requiring API keys or running the full Chainlit server.
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        # Test core imports
        from typing import TypedDict, List, Dict, Any, Optional
        from datetime import datetime
        print("  ✅ Core Python modules")
        
        # Test Chainlit
        import chainlit as cl
        print("  ✅ Chainlit")
        
        # Test LangChain/LangGraph
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
        from langchain_core.prompts import PromptTemplate
        from langgraph.graph import StateGraph, START, END
        print("  ✅ LangChain/LangGraph")
        
        # Test vector store
        from langchain_chroma import Chroma
        from langchain_core.documents import Document
        print("  ✅ Vector store components")
        
        # Test utilities
        from dotenv import load_dotenv
        print("  ✅ Utilities")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False

def test_file_structure():
    """Test that required files and directories exist."""
    print("\n📁 Testing file structure...")
    
    required_files = [
        'app.py',
        'run.py',
        'requirements.txt',
        '.env.example',
        'README.md',
        '.chainlit/config.toml',
        'public/style.css'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    if missing_files:
        print("  ❌ Missing files:")
        for file_path in missing_files:
            print(f"    • {file_path}")
        return False
    
    return True

def test_configuration():
    """Test configuration files."""
    print("\n⚙️ Testing configuration...")
    
    # Test .env.example
    try:
        with open('.env.example', 'r') as f:
            env_content = f.read()
            required_vars = ['GROQ_API_KEY', 'OPENAI_API_KEY']
            for var in required_vars:
                if var in env_content:
                    print(f"  ✅ {var} in .env.example")
                else:
                    print(f"  ❌ {var} missing from .env.example")
                    return False
    except FileNotFoundError:
        print("  ❌ .env.example not found")
        return False
    
    # Test config.toml
    try:
        with open('.chainlit/config.toml', 'r') as f:
            config_content = f.read()
            if '[project]' in config_content and '[UI]' in config_content:
                print("  ✅ Chainlit configuration valid")
            else:
                print("  ❌ Invalid Chainlit configuration")
                return False
    except FileNotFoundError:
        print("  ❌ .chainlit/config.toml not found")
        return False
    
    return True

def test_app_structure():
    """Test that the main app has required components."""
    print("\n🏗️ Testing app structure...")
    
    try:
        # Import the app module
        sys.path.insert(0, '.')
        
        # Test that key functions exist (without executing them)
        with open('app.py', 'r') as f:
            app_content = f.read()
            
            required_functions = [
                'on_chat_start',
                'on_message',
                'handle_demo_setup',
                'handle_file_upload',
                'process_user_question',
                'setup_node',
                'comparison_node',
                'interactive_loop_node'
            ]
            
            for func in required_functions:
                if f"def {func}" in app_content or f"async def {func}" in app_content:
                    print(f"  ✅ {func} function defined")
                else:
                    print(f"  ❌ {func} function missing")
                    return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing app structure: {e}")
        return False

def test_sample_data():
    """Test that sample data is properly structured."""
    print("\n📊 Testing sample data...")
    
    try:
        with open('app.py', 'r') as f:
            app_content = f.read()
            
            if 'SAMPLE_PROPOSALS' in app_content:
                print("  ✅ Sample proposals defined")
                
                # Check for required fields
                required_fields = ['id', 'title', 'content', 'budget', 'timeline_months', 'category']
                for field in required_fields:
                    if f'"{field}"' in app_content:
                        print(f"  ✅ {field} field present")
                    else:
                        print(f"  ❌ {field} field missing")
                        return False
            else:
                print("  ❌ SAMPLE_PROPOSALS not found")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing sample data: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 LangGraph Proposal Analyzer - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("File Structure", test_file_structure),
        ("Configuration", test_configuration),
        ("App Structure", test_app_structure),
        ("Sample Data", test_sample_data)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"\n❌ {test_name} test failed")
        except Exception as e:
            print(f"\n❌ {test_name} test error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to run.")
        print("\n🚀 Next steps:")
        print("  1. Set up your .env file with API keys")
        print("  2. Run: python run.py")
        print("  3. Open: http://localhost:8000")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues before running.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
