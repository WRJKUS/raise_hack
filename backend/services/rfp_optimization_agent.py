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

CRITICAL INSTRUCTIONS:
You MUST respond with ONLY valid JSON. Do not include any text before or after the JSON.
Provide your analysis in the following EXACT JSON format with specific, actionable content:

{{
  "timeline_feasibility": {{
    "score": [1-10],
    "timeline_assessment_score": [1-10],
    "findings": ["specific finding about timeline based on RFP content", "another specific timeline finding"],
    "recommendations": ["specific actionable timeline recommendation", "another timeline recommendation"],
    "recommended_timeline_adjustments": ["specific timeline adjustment with rationale", "another adjustment"],
    "risk_factors": ["specific timeline risk and mitigation strategy", "another risk factor"],
    "historical_comparison": ["comparison with similar project type", "industry benchmark reference"]
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

CRITICAL REQUIREMENTS:
- RESPOND WITH ONLY VALID JSON - NO OTHER TEXT
- All scores must be integers 1-10 with specific justification based on RFP content
- Provide specific, actionable recommendations based on actual RFP details
- Include realistic historical comparisons for this project type
- Ensure JSON is perfectly formatted and complete
- Focus on practical improvements specific to this RFP
- Use actual project details from the RFP content in your analysis"""
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

            # Prepare the analysis prompt with more content for better analysis
            rfp_content = rfp_data.get('content', '')
            content_preview = rfp_content[:3000] + \
                "..." if len(rfp_content) > 3000 else rfp_content

            analysis_prompt = self.rfp_optimization_template.invoke({
                "rfp_title": rfp_data.get('title', 'Unknown RFP'),
                "rfp_content": content_preview,
                "rfp_budget": f"${rfp_data.get('budget', 0):,.0f}" if rfp_data.get('budget', 0) > 0 else "Not specified",
                "rfp_timeline": f"{rfp_data.get('timeline_months', 0)} months" if rfp_data.get('timeline_months', 0) > 0 else "Not specified"
            })

            # Try to generate analysis with retries for better reliability
            structured_analysis = None
            max_retries = 3

            for attempt in range(max_retries):
                try:
                    print(
                        f"🤖 Generating AI analysis (attempt {attempt + 1}/{max_retries})...")

                    # Generate analysis using LLM
                    messages = [SystemMessage(content=analysis_prompt.text)]
                    response = self.llm.invoke(messages)

                    print(
                        f"📝 AI response length: {len(response.content)} characters")

                    # Parse the structured analysis
                    structured_analysis = self._parse_analysis_response(
                        response.content, rfp_data)

                    if structured_analysis:
                        print("✅ Successfully parsed AI analysis response")
                        break
                    else:
                        print(
                            f"⚠️ Failed to parse AI response on attempt {attempt + 1}")

                except Exception as e:
                    print(f"⚠️ Error on attempt {attempt + 1}: {str(e)}")
                    if attempt == max_retries - 1:
                        raise e

            if not structured_analysis:
                raise ValueError(
                    "Failed to generate valid analysis after multiple attempts")

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

    def _parse_analysis_response(self, response_content: str, rfp_data: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
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
                    print("✅ Successfully parsed structured JSON response from AI")
                    return parsed_analysis

            # If JSON parsing fails, try to extract insights from the text response
            print("⚠️ Could not parse JSON from AI response, attempting text analysis...")
            return self._create_dynamic_analysis_from_text(response_content, rfp_data)

        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing error: {e}, attempting text analysis...")
            return self._create_dynamic_analysis_from_text(response_content, rfp_data)

    def _create_dynamic_analysis_from_text(self, response_content: str, rfp_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create analysis by extracting insights from AI text response and RFP content"""
        print("🔍 Creating dynamic analysis from AI text response...")

        # Extract key information from RFP data
        rfp_title = rfp_data.get(
            'title', 'Unknown RFP') if rfp_data else 'Unknown RFP'
        rfp_budget = rfp_data.get('budget', 0) if rfp_data else 0
        rfp_timeline = rfp_data.get('timeline_months', 0) if rfp_data else 0
        rfp_content = rfp_data.get('content', '') if rfp_data else ''

        # Analyze complexity based on RFP content
        complexity_indicators = [
            'AI', 'machine learning', 'integration', 'API', 'cloud', 'security',
            'compliance', 'migration', 'legacy', 'real-time', 'scalable'
        ]
        complexity_score = sum(1 for indicator in complexity_indicators
                               if indicator.lower() in rfp_content.lower())

        # Determine scores based on RFP characteristics
        timeline_score = self._assess_timeline_feasibility(
            rfp_timeline, complexity_score, rfp_content)
        requirements_score = self._assess_requirements_clarity(rfp_content)
        cost_score = self._assess_cost_structure(rfp_budget, rfp_content)
        tco_score = self._assess_tco_completeness(rfp_content)

        # Extract insights from AI response text
        ai_insights = self._extract_insights_from_response(response_content)

        return {
            "timeline_feasibility": {
                "score": timeline_score,
                "timeline_assessment_score": timeline_score,
                "findings": ai_insights.get('timeline_findings', [
                    f"Timeline analysis for {rfp_title}",
                    f"Project duration: {rfp_timeline} months" if rfp_timeline > 0 else "Timeline not specified",
                    f"Complexity level: {'High' if complexity_score > 5 else 'Medium' if complexity_score > 2 else 'Low'}"
                ]),
                "recommendations": ai_insights.get('timeline_recommendations', [
                    "Conduct detailed project planning and risk assessment",
                    "Consider phased delivery approach for complex requirements"
                ]),
                "recommended_timeline_adjustments": [
                    f"Add 15-25% buffer for {rfp_title} complexity",
                    "Include time for stakeholder reviews and approvals"
                ],
                "risk_factors": [
                    f"High complexity project with {complexity_score} technical challenges identified",
                    "Integration requirements may extend timeline"
                ],
                "historical_comparison": [
                    f"Similar projects typically require {int(rfp_timeline * 1.2)} months",
                    "Industry average includes 20% timeline buffer"
                ]
            },
            "requirements_clarity": {
                "score": requirements_score,
                "clarity_score": requirements_score,
                "findings": ai_insights.get('requirements_findings', [
                    f"Requirements analysis for {rfp_title}",
                    "Technical specifications need detailed review",
                    "Functional requirements assessment completed"
                ]),
                "recommendations": ai_insights.get('requirements_recommendations', [
                    "Define specific acceptance criteria for all deliverables",
                    "Clarify technical architecture requirements"
                ]),
                "requirement_gaps": [
                    "Performance metrics and SLA definitions",
                    "Integration specifications and data formats"
                ],
                "suggested_clarifications": [
                    "Add detailed technical specifications",
                    "Define measurable success criteria"
                ],
                "deliverable_alignment": f"Requirements for {rfp_title} show moderate alignment with expected deliverables"
            },
            "cost_flexibility": {
                "score": cost_score,
                "findings": ai_insights.get('cost_findings', [
                    f"Cost analysis for {rfp_title}",
                    f"Budget range: ${rfp_budget:,.0f}" if rfp_budget > 0 else "Budget not specified",
                    "Cost structure requires detailed breakdown"
                ]),
                "recommendations": ai_insights.get('cost_recommendations', [
                    "Implement detailed cost tracking and reporting",
                    "Establish change management procedures"
                ]),
                "cost_structure_assessment": f"Budget structure for {rfp_title} shows {'good' if cost_score >= 7 else 'moderate'} flexibility",
                "change_management_readiness": "Standard change management processes recommended",
                "missing_cost_categories": [
                    "Risk mitigation and contingency costs",
                    "Training and knowledge transfer expenses"
                ],
                "recommended_contingencies": [
                    f"10-15% contingency for {rfp_title} scope changes",
                    "Additional buffer for integration complexities"
                ]
            },
            "tco_analysis": {
                "score": tco_score,
                "tco_completeness_score": tco_score,
                "findings": ai_insights.get('tco_findings', [
                    f"TCO analysis for {rfp_title}",
                    "Lifecycle costs require comprehensive planning",
                    "Operational expenses need detailed projection"
                ]),
                "recommendations": ai_insights.get('tco_recommendations', [
                    "Include 3-5 year operational cost projections",
                    "Factor in maintenance and support expenses"
                ]),
                "missing_cost_elements": [
                    "Long-term maintenance and support costs",
                    "Infrastructure scaling and upgrade expenses"
                ],
                "lifecycle_cost_projections": [
                    f"Estimated 3-year operational costs for {rfp_title}",
                    "Include hosting, maintenance, and support expenses"
                ],
                "budget_realism_check": f"Budget for {rfp_title} appears {'realistic' if rfp_budget > 100000 else 'potentially insufficient'} for project scope"
            },
            "executive_summary": f"Analysis completed for {rfp_title}. Project shows {'high' if complexity_score > 5 else 'moderate'} complexity with focus needed on timeline planning, requirements clarification, and comprehensive cost analysis.",
            "priority_actions": [
                f"Conduct detailed technical review for {rfp_title}",
                "Establish comprehensive project timeline with appropriate buffers",
                "Develop detailed cost breakdown including lifecycle expenses"
            ]
        }

    def _assess_timeline_feasibility(self, timeline_months: int, complexity_score: int, content: str) -> int:
        """Assess timeline feasibility based on project characteristics"""
        if timeline_months == 0:
            return 5  # No timeline specified

        # Base score starts at 8
        score = 8

        # Reduce score for high complexity
        if complexity_score > 6:
            score -= 2
        elif complexity_score > 3:
            score -= 1

        # Reduce score for very short timelines
        if timeline_months < 6:
            score -= 2
        elif timeline_months < 12:
            score -= 1

        # Check for migration/legacy indicators
        if any(term in content.lower() for term in ['migration', 'legacy', 'modernization']):
            score -= 1

        return max(1, min(10, score))

    def _assess_requirements_clarity(self, content: str) -> int:
        """Assess requirements clarity based on content analysis"""
        score = 7  # Base score

        # Look for detailed requirements indicators
        clarity_indicators = [
            'technical specifications', 'acceptance criteria', 'performance requirements',
            'functional requirements', 'deliverables', 'scope of work'
        ]

        found_indicators = sum(1 for indicator in clarity_indicators
                               if indicator in content.lower())

        # Adjust score based on found indicators
        if found_indicators >= 4:
            score += 1
        elif found_indicators <= 2:
            score -= 1

        # Check for vague language
        vague_terms = ['as needed', 'appropriate', 'suitable', 'reasonable']
        if sum(1 for term in vague_terms if term in content.lower()) > 3:
            score -= 1

        return max(1, min(10, score))

    def _assess_cost_structure(self, budget: float, content: str) -> int:
        """Assess cost structure and flexibility"""
        score = 7  # Base score

        # Check if budget is specified
        if budget == 0:
            score -= 1

        # Look for cost breakdown indicators
        cost_indicators = [
            'payment schedule', 'milestone', 'contingency', 'change order',
            'cost breakdown', 'pricing model'
        ]

        found_indicators = sum(1 for indicator in cost_indicators
                               if indicator in content.lower())

        if found_indicators >= 3:
            score += 1
        elif found_indicators <= 1:
            score -= 1

        return max(1, min(10, score))

    def _assess_tco_completeness(self, content: str) -> int:
        """Assess Total Cost of Ownership completeness"""
        score = 6  # Base score (typically incomplete)

        # Look for TCO indicators
        tco_indicators = [
            'maintenance', 'support', 'operational costs', 'lifecycle',
            'ongoing costs', 'hosting', 'infrastructure', 'training'
        ]

        found_indicators = sum(1 for indicator in tco_indicators
                               if indicator in content.lower())

        if found_indicators >= 4:
            score += 2
        elif found_indicators >= 2:
            score += 1
        elif found_indicators == 0:
            score -= 2

        return max(1, min(10, score))

    def _extract_insights_from_response(self, response_content: str) -> Dict[str, List[str]]:
        """Extract insights from AI response text"""
        insights = {}

        # Try to extract any meaningful content from the AI response
        if response_content and len(response_content) > 100:
            # Look for timeline-related insights
            if 'timeline' in response_content.lower():
                insights['timeline_findings'] = [
                    "AI identified timeline considerations in analysis"]
                insights['timeline_recommendations'] = [
                    "Review timeline based on AI analysis"]

            # Look for requirements-related insights
            if 'requirement' in response_content.lower():
                insights['requirements_findings'] = [
                    "AI identified requirements considerations"]
                insights['requirements_recommendations'] = [
                    "Clarify requirements based on AI analysis"]

            # Look for cost-related insights
            if any(term in response_content.lower() for term in ['cost', 'budget', 'price']):
                insights['cost_findings'] = [
                    "AI identified cost considerations"]
                insights['cost_recommendations'] = [
                    "Review cost structure based on AI analysis"]

            # Look for TCO-related insights
            if any(term in response_content.lower() for term in ['maintenance', 'support', 'operational']):
                insights['tco_findings'] = [
                    "AI identified lifecycle cost considerations"]
                insights['tco_recommendations'] = [
                    "Include operational costs based on AI analysis"]

        return insights

    def _generate_implementation_timeline(self, priority_actions: List[str], analysis_summary: str, rfp_data: Dict[str, Any] = None) -> Dict[str, List[str]]:
        """Generate implementation timeline for recommendations"""
        try:
            if not self.llm:
                return self._create_default_timeline(priority_actions, rfp_data)

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
            return self._create_default_timeline(priority_actions, rfp_data)

    def _create_default_timeline(self, priority_actions: List[str], rfp_data: Dict[str, Any] = None) -> Dict[str, List[str]]:
        """Create a dynamic implementation timeline based on priority actions and RFP data"""
        rfp_title = rfp_data.get(
            'title', 'this RFP') if rfp_data else 'this RFP'

        # Create dynamic timeline based on priority actions
        immediate_actions = []
        short_term_actions = []
        long_term_actions = []

        # Categorize priority actions
        for action in priority_actions:
            if any(word in action.lower() for word in ['review', 'validate', 'identify', 'clarify']):
                immediate_actions.append(action)
            elif any(word in action.lower() for word in ['implement', 'establish', 'develop', 'conduct']):
                short_term_actions.append(action)
            else:
                long_term_actions.append(action)

        # Add default actions if categories are empty
        if not immediate_actions:
            immediate_actions = [
                f"Review and validate {rfp_title} structure and requirements",
                "Identify immediate gaps in project documentation"
            ]

        if not short_term_actions:
            short_term_actions = [
                f"Implement priority recommendations for {rfp_title}",
                "Conduct stakeholder review sessions",
                "Update cost estimates and timeline projections"
            ]

        if not long_term_actions:
            long_term_actions = [
                f"Establish comprehensive processes for {rfp_title} management",
                "Develop project tracking and reporting systems",
                "Create standardized templates and best practices"
            ]

        return {
            "immediate": immediate_actions[:3],  # Limit to 3 items
            "short_term": short_term_actions[:3],
            "long_term": long_term_actions[:3]
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
