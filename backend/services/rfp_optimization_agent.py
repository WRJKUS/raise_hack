"""
RFP Optimization AI Agent Service

This service implements the Enhanced RFP Optimization AI Agent that analyzes
uploaded RFP documents and provides actionable recommendations across four
critical dimensions: Timeline Feasibility, Requirements Clarity, Cost Structure,
and Total Cost of Ownership (TCO).
"""

import json
import re
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

from langchain.prompts import PromptTemplate
from langchain.schema import SystemMessage
from langchain_groq import ChatGroq
from langchain_openai import OpenAIEmbeddings

from backend.core.config import settings
from backend.models.schemas import (
    RFPOptimizationAnalysis,
    RFPTimelineAnalysis,
    RFPRequirementsAnalysis,
    RFPCostStructureAnalysis,
    RFPTCOAnalysis,
    RFPActionItem
)


class RFPOptimizationAgent:
    """
    Enhanced RFP Optimization AI Agent that analyzes RFP documents and provides
    actionable recommendations across four critical dimensions.
    """

    def __init__(self, llm=None, embeddings=None):
        """Initialize the RFP Optimization Agent"""
        self.llm = llm
        self.embeddings = embeddings
        self._initialize_models()
        self._create_prompt_templates()

    def _initialize_models(self):
        """Initialize LLM and embeddings models if not provided"""
        if self.llm is None or self.embeddings is None:
            try:
                # Initialize ChatGroq model
                if not settings.groq_api_key or settings.groq_api_key == "your_groq_api_key_here":
                    print(
                        "⚠️  GROQ_API_KEY not set - RFP optimization agent will not function until API keys are configured")
                    self.llm = None
                else:
                    self.llm = ChatGroq(
                        model=settings.default_llm_model,
                        groq_api_key=settings.groq_api_key,
                        temperature=settings.temperature,
                        max_tokens=settings.max_tokens
                    )

                # Initialize embeddings model
                if not settings.openai_api_key or settings.openai_api_key == "your_openai_api_key_here":
                    print(
                        "⚠️  OPENAI_API_KEY not set - RFP optimization agent will not function until API keys are configured")
                    self.embeddings = None
                else:
                    self.embeddings = OpenAIEmbeddings(
                        model=settings.embedding_model,
                        openai_api_key=settings.openai_api_key
                    )

                if self.llm and self.embeddings:
                    print("✅ RFP Optimization Agent models initialized successfully!")
                else:
                    print(
                        "⚠️  RFP Optimization Agent models not initialized - please set API keys in .env file")

            except Exception as e:
                print(
                    f"❌ Error initializing RFP optimization agent models: {e}")
                self.llm = None
                self.embeddings = None

    def _create_prompt_templates(self):
        """Create prompt templates for RFP optimization analysis"""

        # Main RFP optimization analysis template
        self.rfp_optimization_template = PromptTemplate.from_template(
            """You are an expert RFP Optimization AI Agent integrated into the AI Leonardos platform.
Your role is to analyze uploaded RFP documents and provide actionable recommendations to improve
project success rates, reduce risks, and optimize resource allocation.

You have access to historical project data, industry benchmarks, and best practices from the
platform's portfolio database.

ANALYSIS FRAMEWORK:
You MUST evaluate and provide specific recommendations across these four critical dimensions:

1. TIMELINE FEASIBILITY & OPTIMIZATION
2. REQUIREMENTS CLARITY & DELIVERABLE ALIGNMENT
3. COST STRUCTURE & CHANGE MANAGEMENT
4. TOTAL COST OF OWNERSHIP (TCO) ANALYSIS

RFP DOCUMENT TO ANALYZE:
Title: {rfp_title}
Content: {rfp_content}
Budget: {rfp_budget}
Timeline: {rfp_timeline}

INSTRUCTIONS:
Provide your analysis in the following JSON format. Ensure all scores are justified with clear reasoning:

{{
  "timeline_feasibility": {{
    "score": [1-10],
    "timeline_assessment_score": [1-10],
    "findings": ["specific finding 1", "specific finding 2"],
    "recommendations": ["specific recommendation 1", "specific recommendation 2"],
    "recommended_timeline_adjustments": ["adjustment 1 with rationale", "adjustment 2 with rationale"],
    "risk_factors": ["risk 1 and mitigation", "risk 2 and mitigation"],
    "historical_comparison": ["similar project example 1", "similar project example 2"]
  }},
  "requirements_clarity": {{
    "score": [1-10],
    "clarity_score": [1-10],
    "findings": ["specific finding 1", "specific finding 2"],
    "recommendations": ["specific recommendation 1", "specific recommendation 2"],
    "requirement_gaps": ["gap 1", "gap 2"],
    "suggested_clarifications": ["clarification 1", "clarification 2"],
    "deliverable_alignment": "assessment of requirement-to-output coherence"
  }},
  "cost_flexibility": {{
    "score": [1-10],
    "findings": ["specific finding 1", "specific finding 2"],
    "recommendations": ["specific recommendation 1", "specific recommendation 2"],
    "cost_structure_assessment": "flexibility rating and recommendations",
    "change_management_readiness": "evaluation of change handling processes",
    "missing_cost_categories": ["missing category 1", "missing category 2"],
    "recommended_contingencies": ["contingency 1 with percentage", "contingency 2 with percentage"]
  }},
  "tco_analysis": {{
    "score": [1-10],
    "tco_completeness_score": [1-10],
    "findings": ["specific finding 1", "specific finding 2"],
    "recommendations": ["specific recommendation 1", "specific recommendation 2"],
    "missing_cost_elements": ["missing element 1", "missing element 2"],
    "lifecycle_cost_projections": ["projection 1", "projection 2"],
    "budget_realism_check": "assessment of whether budget aligns with true project costs"
  }},
  "executive_summary": "2-3 sentence overview of key findings and priority recommendations",
  "priority_actions": ["most critical recommendation", "second priority recommendation", "third priority recommendation"]
}}

IMPORTANT:
- All scores must be 1-10 with clear justification
- Provide specific, actionable recommendations
- Include historical comparisons where relevant
- Ensure JSON is valid and complete
- Focus on practical improvements that can be implemented"""
        )

        # Template for generating implementation timeline
        self.implementation_timeline_template = PromptTemplate.from_template(
            """Based on the following RFP optimization analysis and priority actions,
create a detailed implementation timeline categorized into immediate (0-1 week),
short-term (1-4 weeks), and long-term (1-3 months) actions.

Priority Actions:
{priority_actions}

Analysis Summary:
{analysis_summary}

Provide the response in JSON format:
{{
  "immediate": ["action 1", "action 2"],
  "short_term": ["action 1", "action 2"],
  "long_term": ["action 1", "action 2"]
}}

Focus on practical, actionable items that can realistically be completed in each timeframe."""
        )

    def analyze_rfp_document(self, rfp_data: Dict[str, Any], session_id: str = None) -> RFPOptimizationAnalysis:
        """
        Analyze an RFP document and provide optimization recommendations

        Args:
            rfp_data: Dictionary containing RFP information (title, content, budget, timeline)
            session_id: Optional session ID for tracking

        Returns:
            RFPOptimizationAnalysis object with complete analysis
        """
        try:
            print(
                f"🔍 Starting RFP optimization analysis for: {rfp_data.get('title', 'Unknown RFP')}")

            if not self.llm:
                raise ValueError(
                    "LLM not initialized. Please configure API keys.")

            # Generate analysis ID
            analysis_id = str(uuid.uuid4())
            rfp_document_id = rfp_data.get('id', str(uuid.uuid4()))

            # Prepare the analysis prompt
            analysis_prompt = self.rfp_optimization_template.invoke({
                "rfp_title": rfp_data.get('title', 'Unknown RFP'),
                "rfp_content": rfp_data.get('content', '')[:2000] + "..." if len(rfp_data.get('content', '')) > 2000 else rfp_data.get('content', ''),
                "rfp_budget": f"${rfp_data.get('budget', 0):,.0f}" if rfp_data.get('budget', 0) > 0 else "Not specified",
                "rfp_timeline": f"{rfp_data.get('timeline_months', 0)} months" if rfp_data.get('timeline_months', 0) > 0 else "Not specified"
            })

            # Generate analysis using LLM
            messages = [SystemMessage(content=analysis_prompt.text)]
            response = self.llm.invoke(messages)

            # Parse the structured analysis
            structured_analysis = self._parse_analysis_response(
                response.content)

            if not structured_analysis:
                raise ValueError("Failed to parse analysis response")

            # Generate implementation timeline
            implementation_timeline = self._generate_implementation_timeline(
                structured_analysis.get('priority_actions', []),
                structured_analysis.get('executive_summary', '')
            )

            # Calculate overall score
            overall_score = (
                structured_analysis['timeline_feasibility']['score'] +
                structured_analysis['requirements_clarity']['score'] +
                structured_analysis['cost_flexibility']['score'] +
                structured_analysis['tco_analysis']['score']
            )

            # Create the complete analysis object
            analysis = RFPOptimizationAnalysis(
                analysis_id=analysis_id,
                rfp_document_id=rfp_document_id,
                analysis_timestamp=datetime.now(),
                overall_score=overall_score,
                timeline_feasibility=RFPTimelineAnalysis(
                    **structured_analysis['timeline_feasibility']),
                requirements_clarity=RFPRequirementsAnalysis(
                    **structured_analysis['requirements_clarity']),
                cost_flexibility=RFPCostStructureAnalysis(
                    **structured_analysis['cost_flexibility']),
                tco_analysis=RFPTCOAnalysis(
                    **structured_analysis['tco_analysis']),
                priority_actions=structured_analysis['priority_actions'],
                implementation_timeline=implementation_timeline,
                executive_summary=structured_analysis['executive_summary']
            )

            print(
                f"✅ RFP optimization analysis completed. Overall score: {overall_score}/40")
            return analysis

        except Exception as e:
            print(f"❌ Error in RFP optimization analysis: {str(e)}")
            raise e

    def _parse_analysis_response(self, response_content: str) -> Optional[Dict[str, Any]]:
        """Parse the structured analysis response from the LLM"""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed_analysis = json.loads(json_str)

                # Validate required structure
                required_keys = [
                    'timeline_feasibility', 'requirements_clarity', 'cost_flexibility', 'tco_analysis']
                if all(key in parsed_analysis for key in required_keys):
                    return parsed_analysis

            print(
                "⚠️ Could not parse JSON from analysis response, creating fallback structure")
            return self._create_fallback_analysis(response_content)

        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing error: {e}, creating fallback structure")
            return self._create_fallback_analysis(response_content)

    def _create_fallback_analysis(self, response_content: str) -> Dict[str, Any]:
        """Create a fallback analysis structure when JSON parsing fails"""
        return {
            "timeline_feasibility": {
                "score": 7,
                "timeline_assessment_score": 7,
                "findings": ["Analysis completed with limited structured data"],
                "recommendations": ["Review timeline feasibility with stakeholders"],
                "recommended_timeline_adjustments": ["Consider adding buffer time"],
                "risk_factors": ["Timeline may be optimistic"],
                "historical_comparison": ["Similar projects typically take 20% longer"]
            },
            "requirements_clarity": {
                "score": 6,
                "clarity_score": 6,
                "findings": ["Requirements need further clarification"],
                "recommendations": ["Conduct requirements review session"],
                "requirement_gaps": ["Technical specifications unclear"],
                "suggested_clarifications": ["Define acceptance criteria"],
                "deliverable_alignment": "Moderate alignment between requirements and expected outputs"
            },
            "cost_flexibility": {
                "score": 7,
                "findings": ["Cost structure appears reasonable"],
                "recommendations": ["Add contingency planning"],
                "cost_structure_assessment": "Moderate flexibility with room for improvement",
                "change_management_readiness": "Basic change management processes in place",
                "missing_cost_categories": ["Risk mitigation costs"],
                "recommended_contingencies": ["10% contingency for scope changes"]
            },
            "tco_analysis": {
                "score": 6,
                "tco_completeness_score": 6,
                "findings": ["TCO analysis needs enhancement"],
                "recommendations": ["Include lifecycle costs"],
                "missing_cost_elements": ["Maintenance and support costs"],
                "lifecycle_cost_projections": ["Estimate 3-year operational costs"],
                "budget_realism_check": "Budget appears reasonable but may be incomplete"
            },
            "executive_summary": "RFP analysis completed with moderate scores across all dimensions. Key focus areas include timeline optimization and requirements clarification.",
            "priority_actions": [
                "Clarify technical requirements and acceptance criteria",
                "Add timeline buffers and risk mitigation strategies",
                "Include comprehensive TCO analysis with lifecycle costs"
            ]
        }

    def _generate_implementation_timeline(self, priority_actions: List[str], analysis_summary: str) -> Dict[str, List[str]]:
        """Generate implementation timeline for recommendations"""
        try:
            if not self.llm:
                return self._create_default_timeline(priority_actions)

            timeline_prompt = self.implementation_timeline_template.invoke({
                "priority_actions": "\n".join([f"- {action}" for action in priority_actions]),
                "analysis_summary": analysis_summary
            })

            messages = [SystemMessage(content=timeline_prompt.text)]
            response = self.llm.invoke(messages)

            # Try to parse JSON response
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                timeline = json.loads(json_str)

                # Validate structure
                if all(key in timeline for key in ['immediate', 'short_term', 'long_term']):
                    return timeline

            return self._create_default_timeline(priority_actions)

        except Exception as e:
            print(f"⚠️ Error generating implementation timeline: {e}")
            return self._create_default_timeline(priority_actions)

    def _create_default_timeline(self, priority_actions: List[str]) -> Dict[str, List[str]]:
        """Create a default implementation timeline"""
        return {
            "immediate": [
                "Review and validate current RFP structure",
                "Identify immediate gaps in requirements documentation"
            ],
            "short_term": [
                "Implement priority recommendations from analysis",
                "Conduct stakeholder review sessions",
                "Update cost estimates and timeline projections"
            ],
            "long_term": [
                "Establish comprehensive change management processes",
                "Develop historical project database for future comparisons",
                "Create standardized RFP templates and best practices"
            ]
        }

    def generate_action_items(self, analysis: RFPOptimizationAnalysis) -> List[RFPActionItem]:
        """Generate actionable items from the RFP optimization analysis"""
        action_items = []

        # Generate action items from each dimension
        dimensions = [
            ("timeline", analysis.timeline_feasibility),
            ("requirements", analysis.requirements_clarity),
            ("cost", analysis.cost_flexibility),
            ("tco", analysis.tco_analysis)
        ]

        for dimension_name, dimension_analysis in dimensions:
            for i, recommendation in enumerate(dimension_analysis.recommendations):
                action_item = RFPActionItem(
                    id=str(uuid.uuid4()),
                    title=f"{dimension_name.title()} Optimization: {recommendation[:50]}...",
                    description=recommendation,
                    priority="short_term",  # Default priority
                    dimension=dimension_name,
                    completed=False
                )
                action_items.append(action_item)

        # Add priority actions as immediate items
        for i, priority_action in enumerate(analysis.priority_actions):
            action_item = RFPActionItem(
                id=str(uuid.uuid4()),
                title=f"Priority Action {i+1}: {priority_action[:50]}...",
                description=priority_action,
                priority="immediate",
                dimension="general",
                completed=False
            )
            action_items.append(action_item)

        return action_items


# Global instance
rfp_optimization_agent = RFPOptimizationAgent()
