#!/usr/bin/env python3
"""
Test script for the LangGraph workflow functionality
"""

import os
import sys
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_workflow_import():
    """Test if we can import the workflow service"""
    print("📦 Testing workflow imports...")
    try:
        from backend.services.workflow import workflow_service, ProposalAgentState
        print("✅ Workflow service imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_sample_proposals():
    """Test with sample proposal data"""
    print("\n📄 Testing with sample proposals...")
    
    try:
        from backend.services.workflow import workflow_service
        
        # Sample proposals for testing
        sample_proposals = [
            {
                "id": "test_001",
                "title": "AI-Powered Customer Service Platform",
                "content": """This proposal outlines the development of an AI-powered customer service platform
                that leverages natural language processing and machine learning to provide 24/7 automated
                customer support. The system will integrate with existing CRM systems and provide
                real-time analytics on customer interactions. Budget: $500,000. Timeline: 12 months.
                Key features include: multilingual support, sentiment analysis, escalation protocols,
                and integration with popular messaging platforms.""",
                "budget": 500000,
                "timeline_months": 12,
                "category": "Technology"
            },
            {
                "id": "test_002", 
                "title": "Sustainable Energy Infrastructure Project",
                "content": """A comprehensive proposal for implementing renewable energy infrastructure
                across multiple facilities. This includes solar panel installation, wind energy systems,
                and battery storage solutions. The project aims to reduce carbon footprint by 60%
                and achieve energy independence within 18 months. Budget: $750,000. Timeline: 18 months.
                Expected ROI: 15% annually after implementation. Includes maintenance contracts and
                staff training programs.""",
                "budget": 750000,
                "timeline_months": 18,
                "category": "Sustainability"
            }
        ]
        
        print(f"✅ Created {len(sample_proposals)} sample proposals")
        return sample_proposals
        
    except Exception as e:
        print(f"❌ Sample proposal creation failed: {e}")
        return []

def test_workflow_execution():
    """Test the workflow execution without API dependencies"""
    print("\n🔬 Testing workflow execution...")
    
    # Check if API keys are available
    if not os.getenv("GROQ_API_KEY") or not os.getenv("OPENAI_API_KEY"):
        print("⚠️  API keys not found. Skipping workflow execution test.")
        print("   Set GROQ_API_KEY and OPENAI_API_KEY environment variables to test workflow.")
        return False
    
    try:
        from backend.services.workflow import workflow_service
        
        # Get sample proposals
        sample_proposals = test_sample_proposals()
        if not sample_proposals:
            return False
        
        print("🚀 Starting workflow analysis...")
        
        # Run initial analysis
        workflow_state = workflow_service.run_initial_analysis(sample_proposals)
        
        if workflow_state["error_message"]:
            print(f"❌ Workflow failed: {workflow_state['error_message']}")
            return False
        
        print(f"✅ Analysis completed for session: {workflow_state['session_id']}")
        print(f"📊 Analysis length: {len(workflow_state['current_analysis'])} characters")
        
        # Test asking a question
        print("\n💬 Testing question asking...")
        question = "What are the main differences between these proposals?"
        updated_state = workflow_service.ask_question(workflow_state, question)
        
        if updated_state["conversation_history"]:
            latest_conversation = updated_state["conversation_history"][-1]
            print(f"✅ Question processed successfully")
            print(f"📝 Response length: {len(latest_conversation['response'])} characters")
            return True
        else:
            print("❌ Question processing failed")
            return False
            
    except Exception as e:
        print(f"❌ Workflow execution failed: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("\n⚙️  Testing configuration...")
    
    try:
        from backend.core.config import settings
        
        print(f"✅ Configuration loaded")
        print(f"   App name: {settings.app_name}")
        print(f"   LLM model: {settings.default_llm_model}")
        print(f"   Max file size: {settings.max_file_size} bytes")
        print(f"   Upload directory: {settings.upload_directory}")
        print(f"   Chroma directory: {settings.chroma_persist_directory}")
        
        # Check if directories exist
        import os
        if os.path.exists(settings.upload_directory):
            print(f"✅ Upload directory exists: {settings.upload_directory}")
        else:
            print(f"⚠️  Upload directory missing: {settings.upload_directory}")
            
        if os.path.exists(settings.chroma_persist_directory):
            print(f"✅ Chroma directory exists: {settings.chroma_persist_directory}")
        else:
            print(f"⚠️  Chroma directory missing: {settings.chroma_persist_directory}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Run all workflow tests"""
    print("🎭 Leonardo's RFQ Alchemy - Workflow Test Suite")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_workflow_import),
        ("Configuration Test", test_configuration),
        ("Sample Proposals", lambda: bool(test_sample_proposals())),
        ("Workflow Execution", test_workflow_execution),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! The workflow is ready to use.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
        if not os.getenv("GROQ_API_KEY") or not os.getenv("OPENAI_API_KEY"):
            print("\n💡 Tip: Set API keys to enable full workflow testing:")
            print("   export GROQ_API_KEY=your_key_here")
            print("   export OPENAI_API_KEY=your_key_here")

if __name__ == "__main__":
    main()
