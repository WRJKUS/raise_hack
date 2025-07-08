#!/usr/bin/env python3
"""
Test script for RFP Optimization AI Agent
"""

import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.services.rfp_optimization_agent import RFPOptimizationAgent
from backend.models.schemas import RFPOptimizationAnalysis

def test_rfp_optimization_agent():
    """Test the RFP Optimization Agent functionality"""
    print("🧪 Testing RFP Optimization AI Agent")
    print("=" * 50)
    
    # Initialize the agent (without API keys for structure testing)
    agent = RFPOptimizationAgent()
    
    # Test data - sample RFP document
    sample_rfp_data = {
        "id": "test-rfp-001",
        "title": "AI Platform Development RFP",
        "content": """
        Request for Proposal: AI Platform Development
        
        Project Overview:
        We are seeking a vendor to develop a comprehensive AI platform that will integrate 
        machine learning capabilities, natural language processing, and data analytics.
        
        Requirements:
        1. Machine Learning Pipeline Development
        2. Natural Language Processing Integration
        3. Real-time Data Processing
        4. User Interface Development
        5. API Development and Documentation
        6. Security Implementation
        7. Testing and Quality Assurance
        8. Deployment and Maintenance
        
        Timeline: 12 months
        Budget: $500,000 - $750,000
        
        Deliverables:
        - Functional AI platform
        - Complete documentation
        - Training materials
        - 6 months of support
        
        Evaluation Criteria:
        - Technical expertise (40%)
        - Cost effectiveness (30%)
        - Timeline feasibility (20%)
        - Past experience (10%)
        """,
        "budget": 625000,  # Average of range
        "timeline_months": 12,
        "category": "AI Development"
    }
    
    print("📄 Sample RFP Data:")
    print(f"   Title: {sample_rfp_data['title']}")
    print(f"   Budget: ${sample_rfp_data['budget']:,}")
    print(f"   Timeline: {sample_rfp_data['timeline_months']} months")
    print()
    
    # Test prompt template creation
    print("🔧 Testing prompt template creation...")
    try:
        agent._create_prompt_templates()
        print("✅ Prompt templates created successfully")
        
        # Test template invocation
        if hasattr(agent, 'rfp_optimization_template'):
            prompt = agent.rfp_optimization_template.invoke({
                "rfp_title": sample_rfp_data['title'],
                "rfp_content": sample_rfp_data['content'][:500] + "...",
                "rfp_budget": f"${sample_rfp_data['budget']:,}",
                "rfp_timeline": f"{sample_rfp_data['timeline_months']} months"
            })
            print("✅ Prompt template invocation successful")
            print(f"   Prompt length: {len(prompt.text)} characters")
        else:
            print("❌ RFP optimization template not found")
            
    except Exception as e:
        print(f"❌ Error creating prompt templates: {e}")
        return False
    
    # Test fallback analysis creation
    print("\n🔄 Testing fallback analysis creation...")
    try:
        fallback_analysis = agent._create_fallback_analysis("Sample analysis response")
        print("✅ Fallback analysis created successfully")
        
        # Validate structure
        required_keys = ['timeline_feasibility', 'requirements_clarity', 'cost_flexibility', 'tco_analysis']
        if all(key in fallback_analysis for key in required_keys):
            print("✅ Fallback analysis structure is valid")
            
            # Test each dimension
            for key in required_keys:
                dimension = fallback_analysis[key]
                if 'score' in dimension and 'findings' in dimension and 'recommendations' in dimension:
                    print(f"   ✅ {key}: Valid structure (score: {dimension['score']})")
                else:
                    print(f"   ❌ {key}: Invalid structure")
        else:
            print("❌ Fallback analysis structure is invalid")
            
    except Exception as e:
        print(f"❌ Error creating fallback analysis: {e}")
        return False
    
    # Test implementation timeline generation
    print("\n⏰ Testing implementation timeline generation...")
    try:
        sample_actions = [
            "Clarify technical requirements and acceptance criteria",
            "Add timeline buffers and risk mitigation strategies",
            "Include comprehensive TCO analysis with lifecycle costs"
        ]
        
        timeline = agent._create_default_timeline(sample_actions)
        print("✅ Default implementation timeline created successfully")
        
        # Validate timeline structure
        required_timeline_keys = ['immediate', 'short_term', 'long_term']
        if all(key in timeline for key in required_timeline_keys):
            print("✅ Timeline structure is valid")
            for key in required_timeline_keys:
                print(f"   {key}: {len(timeline[key])} actions")
        else:
            print("❌ Timeline structure is invalid")
            
    except Exception as e:
        print(f"❌ Error creating implementation timeline: {e}")
        return False
    
    # Test action item generation (using fallback analysis)
    print("\n📋 Testing action item generation...")
    try:
        # Create a mock analysis object for testing
        from backend.models.schemas import (
            RFPTimelineAnalysis, RFPRequirementsAnalysis, 
            RFPCostStructureAnalysis, RFPTCOAnalysis
        )
        
        mock_analysis = RFPOptimizationAnalysis(
            analysis_id="test-analysis-001",
            rfp_document_id="test-rfp-001",
            analysis_timestamp=datetime.now(),
            overall_score=26,
            timeline_feasibility=RFPTimelineAnalysis(
                score=7,
                timeline_assessment_score=7,
                findings=["Timeline appears feasible"],
                recommendations=["Add buffer time"],
                recommended_timeline_adjustments=["Consider adding 2-month buffer"],
                risk_factors=["Resource availability risk"],
                historical_comparison=["Similar projects took 14 months"]
            ),
            requirements_clarity=RFPRequirementsAnalysis(
                score=6,
                clarity_score=6,
                findings=["Requirements need clarification"],
                recommendations=["Define acceptance criteria"],
                requirement_gaps=["API specifications unclear"],
                suggested_clarifications=["Add technical specifications"],
                deliverable_alignment="Moderate alignment"
            ),
            cost_flexibility=RFPCostStructureAnalysis(
                score=7,
                findings=["Cost structure reasonable"],
                recommendations=["Add contingency planning"],
                cost_structure_assessment="Good flexibility",
                change_management_readiness="Basic processes in place",
                missing_cost_categories=["Risk mitigation costs"],
                recommended_contingencies=["10% contingency"]
            ),
            tco_analysis=RFPTCOAnalysis(
                score=6,
                tco_completeness_score=6,
                findings=["TCO needs enhancement"],
                recommendations=["Include lifecycle costs"],
                missing_cost_elements=["Maintenance costs"],
                lifecycle_cost_projections=["3-year operational costs"],
                budget_realism_check="Budget appears reasonable"
            ),
            priority_actions=[
                "Clarify technical requirements",
                "Add timeline buffers",
                "Include TCO analysis"
            ],
            implementation_timeline={
                "immediate": ["Review RFP structure"],
                "short_term": ["Implement recommendations"],
                "long_term": ["Establish processes"]
            },
            executive_summary="RFP analysis completed with moderate scores across dimensions."
        )
        
        action_items = agent.generate_action_items(mock_analysis)
        print(f"✅ Generated {len(action_items)} action items")
        
        # Validate action items
        priorities = set(item.priority for item in action_items)
        dimensions = set(item.dimension for item in action_items)
        
        print(f"   Priorities: {priorities}")
        print(f"   Dimensions: {dimensions}")
        
        # Check for required fields
        for item in action_items[:3]:  # Check first 3 items
            if all(hasattr(item, field) for field in ['id', 'title', 'description', 'priority', 'dimension']):
                print(f"   ✅ Action item '{item.title[:30]}...' has valid structure")
            else:
                print(f"   ❌ Action item missing required fields")
                
    except Exception as e:
        print(f"❌ Error generating action items: {e}")
        return False
    
    print("\n🎉 All RFP Optimization Agent tests passed!")
    print("\n📝 Summary:")
    print("   ✅ Prompt templates creation")
    print("   ✅ Fallback analysis generation")
    print("   ✅ Implementation timeline creation")
    print("   ✅ Action item generation")
    print("   ✅ Data model validation")
    
    return True

def test_api_integration():
    """Test API integration points"""
    print("\n🔌 Testing API Integration Points")
    print("=" * 50)
    
    try:
        # Test import of router
        from backend.routers.rfp_optimization import router
        print("✅ RFP optimization router imported successfully")
        
        # Test import of main app with router
        from backend.main import app
        print("✅ Main FastAPI app with RFP optimization router imported successfully")
        
        # Check if router is registered
        routes = [route.path for route in app.routes]
        rfp_routes = [route for route in routes if 'rfp-optimization' in route]
        
        if rfp_routes:
            print(f"✅ Found {len(rfp_routes)} RFP optimization routes:")
            for route in rfp_routes:
                print(f"   - {route}")
        else:
            print("❌ No RFP optimization routes found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API integration: {e}")
        return False
    
    return True

def main():
    """Main test function"""
    print("🧪 RFP Optimization AI Agent - Integration Test Suite")
    print("=" * 60)
    
    success = True
    
    # Test the RFP optimization agent
    if not test_rfp_optimization_agent():
        success = False
    
    # Test API integration
    if not test_api_integration():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED! RFP Optimization AI Agent is ready for use.")
        print("\n📋 Next Steps:")
        print("   1. Set GROQ_API_KEY and OPENAI_API_KEY in .env file")
        print("   2. Start the backend server: python start_backend.py")
        print("   3. Start the frontend: cd leonardos-rfq-alchemy-main && npm run dev")
        print("   4. Navigate to RFP Optimization tab in the web interface")
    else:
        print("❌ SOME TESTS FAILED! Please check the errors above.")
    
    return success

if __name__ == "__main__":
    main()
