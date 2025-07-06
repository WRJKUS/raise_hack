#!/usr/bin/env python3
"""
Integration test script for Leonardo's RFQ Alchemy Platform
Tests the FastAPI backend and LangGraph integration
"""

import requests
import json
import time
import os
from pathlib import Path

API_BASE_URL = "http://localhost:8000/api"

def test_health_check():
    """Test the health check endpoint"""
    print("🏥 Testing health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['message']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_proposal_upload():
    """Test proposal upload functionality"""
    print("\n📄 Testing proposal upload...")

    # Create a test PDF file if it doesn't exist
    test_pdf_path = "test_proposal.pdf"
    if not os.path.exists(test_pdf_path):
        print("📝 Creating test PDF file...")
        # Create a simple test PDF content
        test_content = """
        Test Proposal Document

        Title: AI-Powered Customer Service Platform
        Budget: $125,000
        Timeline: 8 months
        Category: Technology

        This is a test proposal for the AI-powered customer service platform.
        The solution includes natural language processing, machine learning,
        and integration with existing CRM systems.
        """

        # For testing, we'll create a simple text file instead of PDF
        with open("test_proposal.txt", "w") as f:
            f.write(test_content)
        print("📝 Created test_proposal.txt (use a real PDF for full testing)")
        return False

    try:
        with open(test_pdf_path, "rb") as f:
            files = {"file": (test_pdf_path, f, "application/pdf")}
            response = requests.post(f"{API_BASE_URL}/proposals/upload", files=files)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Upload successful: {data['message']}")
            print(f"   File ID: {data['file_id']}")
            return data['file_id']
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None

def test_proposal_list():
    """Test listing proposals"""
    print("\n📋 Testing proposal list...")
    try:
        response = requests.get(f"{API_BASE_URL}/proposals/list")
        if response.status_code == 200:
            proposals = response.json()
            print(f"✅ Found {len(proposals)} proposals")
            for proposal in proposals:
                print(f"   - {proposal['title']} (${proposal['budget']:,})")
            return proposals
        else:
            print(f"❌ List failed: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ List error: {e}")
        return []

def test_analysis_start():
    """Test starting analysis"""
    print("\n🔬 Testing analysis start...")
    try:
        response = requests.post(f"{API_BASE_URL}/analysis/start", json={})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analysis started: {data['session_id']}")
            print(f"   Proposals analyzed: {data['proposals_count']}")
            print(f"   Analysis preview: {data['analysis'][:100]}...")
            return data['session_id']
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return None

def test_chat_message(session_id=None):
    """Test sending a chat message"""
    print("\n💬 Testing chat message...")
    try:
        message_data = {
            "message": "What is the average budget of the proposals?",
            "session_id": session_id
        }
        response = requests.post(f"{API_BASE_URL}/chat/message", json=message_data)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat response received")
            print(f"   Session ID: {data['session_id']}")
            print(f"   Response: {data['message']['content'][:150]}...")
            if data['relevant_proposals']:
                print(f"   Relevant proposals: {', '.join(data['relevant_proposals'])}")
            return data['session_id']
        else:
            print(f"❌ Chat failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return None

def test_analysis_results():
    """Test getting analysis results"""
    print("\n📊 Testing analysis results...")
    try:
        response = requests.get(f"{API_BASE_URL}/proposals/analysis/results")
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Found {len(results)} analysis results")
            for result in results:
                print(f"   - {result['vendor']}: {result['overallScore']}/100")
            return results
        else:
            print(f"❌ Results failed: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Results error: {e}")
        return []

def main():
    """Run all integration tests"""
    print("🎭 Leonardo's RFQ Alchemy - Integration Test Suite")
    print("=" * 60)

    # Test health check first
    if not test_health_check():
        print("\n❌ Backend is not running. Please start the FastAPI server first:")
        print("   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload")
        print("   or")
        print("   python start_backend.py")
        return

    # Test proposal upload
    file_id = test_proposal_upload()

    # Test proposal listing
    proposals = test_proposal_list()

    # Test analysis (only if we have proposals)
    session_id = None
    if proposals:
        session_id = test_analysis_start()
        time.sleep(2)  # Give analysis time to complete

    # Test chat functionality
    chat_session = test_chat_message(session_id)

    # Test analysis results
    results = test_analysis_results()

    print("\n" + "=" * 60)
    print("🎉 Integration test completed!")
    print(f"✅ Health check: {'✓' if True else '✗'}")
    print(f"✅ File upload: {'✓' if file_id else '✗'}")
    print(f"✅ Proposal list: {'✓' if proposals else '✗'}")
    print(f"✅ Analysis: {'✓' if session_id else '✗'}")
    print(f"✅ Chat: {'✓' if chat_session else '✗'}")
    print(f"✅ Results: {'✓' if results else '✗'}")

    if all([file_id, proposals, session_id, chat_session, results]):
        print("\n🎊 All tests passed! The integration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()
