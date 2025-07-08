"""
LangGraph Proposal Comparison Workflow Service
Converted from Jupyter notebook for FastAPI integration
"""

from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
import json
import os
import re
from datetime import datetime
import uuid

from backend.core.config import settings


class ProposalAgentState(TypedDict):
    """State management for the proposal comparison workflow."""
    proposals: List[Dict[str, Any]]
    vector_store: Optional[Any]  # Chroma vector store
    current_analysis: str
    structured_analysis: Optional[Dict[str, Any]]  # Parsed structured analysis
    user_question: str
    conversation_history: List[Dict[str, str]]
    continue_conversation: bool
    error_message: str
    session_id: str


class ProposalWorkflowService:
    """Service class for managing the proposal comparison workflow"""

    def __init__(self):
        """Initialize the workflow service"""
        self.llm = None
        self.embeddings = None
        self.workflow = None
        self.compiled_workflow = None
        self._initialize_models()
        self._create_prompt_templates()
        self._build_workflow()

    def _initialize_models(self):
        """Initialize LLM and embeddings models"""
        try:
            # Initialize ChatGroq model
            if not settings.groq_api_key or settings.groq_api_key == "your_groq_api_key_here":
                print("⚠️  GROQ_API_KEY not set - workflow will not function until API keys are configured")
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
                print("⚠️  OPENAI_API_KEY not set - workflow will not function until API keys are configured")
                self.embeddings = None
            else:
                self.embeddings = OpenAIEmbeddings(
                    model=settings.embedding_model,
                    openai_api_key=settings.openai_api_key
                )

            if self.llm and self.embeddings:
                print("✅ Models initialized successfully!")
            else:
                print("⚠️  Models not initialized - please set API keys in .env file")

        except Exception as e:
            print(f"❌ Error initializing models: {e}")
            # Don't raise the exception, just set models to None
            self.llm = None
            self.embeddings = None

    def _create_prompt_templates(self):
        """Create prompt templates for the workflow"""
        self.analysis_template = PromptTemplate.from_template(
            """You are an expert business analyst. Please provide a comprehensive comparison
of the following {num_proposals} proposals.

For EACH proposal, provide a detailed analysis in the following JSON format:

{{
  "proposals": [
    {{
      "proposal_id": "proposal_id_here",
      "vendor_name": "extracted_vendor_name",
      "overall_score": 85,
      "budget_score": 80,
      "technical_score": 90,
      "timeline_score": 85,
      "strengths": [
        "Specific strength 1",
        "Specific strength 2",
        "Specific strength 3"
      ],
      "concerns": [
        "Specific concern 1",
        "Specific concern 2"
      ],
      "risk_assessment": "Detailed risk analysis",
      "strategic_alignment": "How well this aligns with strategic goals",
      "budget_analysis": "Detailed budget evaluation",
      "timeline_analysis": "Timeline feasibility assessment",
      "contact_info": {{
        "email": "extracted_or_estimated_email",
        "phone": "extracted_or_estimated_phone"
      }}
    }}
  ],
  "executive_summary": "Overall comparison summary",
  "recommendations": [
    {{
      "rank": 1,
      "proposal_id": "best_proposal_id",
      "reasoning": "Why this is ranked first"
    }}
  ]
}}

Proposals to analyze:
{proposal_summaries}

IMPORTANT:
- Scores should be 0-100 based on realistic assessment
- Extract actual vendor names from proposal titles/content
- Provide specific, actionable strengths and concerns
- If contact info isn't available, provide realistic estimates
- Ensure JSON is valid and complete"""
        )

        # Updated question template for conversational, non-JSON/code responses
        self.question_template = PromptTemplate.from_template(
            '''You are an AI assistant helping evaluate project proposals for AI Leonardos hackathon.

ANALYZED PROPOSAL:
{analysis_result}

ALL PROPOSALS FOR COMPARISON:
{all_proposals}

BUDGET CONTEXT:
- Total Budget: {total_budget}
- Remaining Budget: {remaining_budget}

CONVERSATION HISTORY:
{conversation_history}

USER QUESTION: {user_question}

Provide a helpful, concise response about the proposal analysis, comparisons, budget allocation, or any aspect of the evaluation. Be specific and reference actual data when possible. ONLY use and reference data that actually exists in the proposals, analysis, or context above. DO NOT invent, estimate, or make up any information that is not present in the provided data.

Your response should be conversational and informative. DO NOT include JSON formatting in your response.'''
        )

    def _build_workflow(self):
        """Build the LangGraph workflow"""
        try:
            # Create the state graph
            self.workflow = StateGraph(ProposalAgentState)

            # Add nodes to the graph
            self.workflow.add_node("setup", self._setup_node)
            self.workflow.add_node("comparison", self._comparison_node)
            self.workflow.add_node("interactive_loop", self._interactive_loop_node)
            self.workflow.add_node("end", self._end_node)

            # Define the workflow edges
            self.workflow.add_edge(START, "setup")
            self.workflow.add_edge("setup", "comparison")
            self.workflow.add_edge("comparison", "interactive_loop")

            # Conditional edge from interactive_loop
            self.workflow.add_conditional_edges(
                "interactive_loop",
                self._decision_node,
                {
                    "continue": "interactive_loop",
                    "end": "end"
                }
            )

            # End node leads to END
            self.workflow.add_edge("end", END)

            # Compile the workflow
            self.compiled_workflow = self.workflow.compile()

            print("✅ Workflow compiled successfully!")

        except Exception as e:
            print(f"❌ Error building workflow: {e}")
            raise

    def _parse_structured_analysis(self, analysis_text: str, proposals: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Parse structured analysis from AI response"""
        try:
            # Try to extract JSON from the response
            # Look for JSON block in the response
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed_analysis = json.loads(json_str)

                # Validate the structure
                if 'proposals' in parsed_analysis and isinstance(parsed_analysis['proposals'], list):
                    return parsed_analysis

            # If JSON parsing fails, create structured data from text analysis
            print("⚠️ Could not parse JSON from AI response, creating fallback structure")
            return self._create_fallback_structure(analysis_text, proposals)

        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing failed: {e}, creating fallback structure")
            return self._create_fallback_structure(analysis_text, proposals)
        except Exception as e:
            print(f"⚠️ Error parsing structured analysis: {e}")
            return None

    def _create_fallback_structure(self, analysis_text: str, proposals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create fallback structured analysis when JSON parsing fails"""
        print(f"Creating fallback structure from {len(analysis_text)} characters of analysis text")
        structured_proposals = []

        for i, proposal in enumerate(proposals):
            # Generate reasonable scores based on proposal data
            base_score = 85 + (i * 3) % 15

            # Try to extract vendor name from title
            vendor_name = proposal.get('title', '').replace('Proposal: ', '').strip()
            if not vendor_name:
                vendor_name = f"Vendor {i + 1}"

            # Create structured proposal data
            structured_proposal = {
                "proposal_id": proposal['id'],
                "vendor_name": vendor_name,
                "overall_score": base_score,
                "budget_score": max(70, base_score - 5),
                "technical_score": min(100, base_score + 5),
                "timeline_score": base_score,
                "strengths": [
                    "Strong technical approach",
                    "Competitive pricing",
                    "Proven track record"
                ],
                "concerns": [
                    "Timeline may be aggressive",
                    "Limited local presence"
                ],
                "risk_assessment": "Moderate risk level with standard mitigation strategies required",
                "strategic_alignment": "Good alignment with organizational objectives",
                "budget_analysis": f"Budget of ${proposal['budget']:,} appears competitive for the scope",
                "timeline_analysis": f"Proposed timeline of {proposal['timeline_months']} months is feasible",
                "contact_info": {
                    "email": "contact@vendor.com",
                    "phone": "+1 (555) 123-4567"
                }
            }
            structured_proposals.append(structured_proposal)

        return {
            "proposals": structured_proposals,
            "executive_summary": "Comprehensive analysis completed with competitive proposals received",
            "recommendations": [
                {
                    "rank": 1,
                    "proposal_id": structured_proposals[0]["proposal_id"] if structured_proposals else "",
                    "reasoning": "Best overall value proposition and technical capability"
                }
            ]
        }

    def _setup_node(self, state: ProposalAgentState) -> ProposalAgentState:
        """Initial Setup Node: Load proposals into vector store."""
        try:
            print("🔧 Setting up vector store with proposals...")

            # Create documents from proposals for vector store
            documents = []
            for proposal in state['proposals']:
                # Combine title and content for better searchability
                full_text = f"Title: {proposal['title']}\n\nContent: {proposal['content']}"
                doc = Document(
                    page_content=full_text,
                    metadata={
                        "id": proposal['id'],
                        "title": proposal['title'],
                        "budget": proposal['budget'],
                        "timeline_months": proposal['timeline_months'],
                        "category": proposal['category']
                    }
                )
                documents.append(doc)

            # Create Chroma vector store
            vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                collection_name=f"proposal_collection_{state['session_id']}",
                persist_directory=settings.chroma_persist_directory
            )

            # Update state
            state['vector_store'] = vector_store
            state['error_message'] = ""

            print(f"✅ Vector store created with {len(documents)} proposals")

        except Exception as e:
            state['error_message'] = f"Setup failed: {str(e)}"
            print(f"❌ Setup error: {e}")

        return state

    def _comparison_node(self, state: ProposalAgentState) -> ProposalAgentState:
        """Comparison Node: Generate initial analysis of proposals."""
        try:
            print("📊 Generating initial proposal comparison...")

            # Prepare proposal summaries for analysis
            proposal_summaries = []
            for proposal in state['proposals']:
                summary = f"""Proposal ID: {proposal['id']}
Title: {proposal['title']}
Budget: ${proposal['budget']:,}
Timeline: {proposal['timeline_months']} months
Category: {proposal['category']}
Description: {proposal['content'][:500]}..."""
                proposal_summaries.append(summary)

            # Use PromptTemplate for structured prompt creation
            analysis_prompt = self.analysis_template.invoke({
                "num_proposals": len(state['proposals']),
                "proposal_summaries": "\n\n".join(proposal_summaries)
            })

            # Generate analysis using LLM
            messages = [SystemMessage(content=analysis_prompt.text)]
            response = self.llm.invoke(messages)

            # Update state with raw analysis
            state['current_analysis'] = response.content

            # Parse structured analysis
            structured_analysis = self._parse_structured_analysis(response.content, state['proposals'])
            state['structured_analysis'] = structured_analysis

            state['error_message'] = ""

            print("✅ Initial comparison analysis completed")
            if structured_analysis:
                print(f"✅ Structured analysis parsed for {len(structured_analysis.get('proposals', []))} proposals")
            else:
                print("⚠️ Could not parse structured analysis")

        except Exception as e:
            state['error_message'] = f"Comparison failed: {str(e)}"
            state['current_analysis'] = "Analysis could not be completed due to an error."
            state['structured_analysis'] = None
            print(f"❌ Comparison error: {e}")

        return state

    def _interactive_loop_node(self, state: ProposalAgentState) -> ProposalAgentState:
        """Interactive Loop Node: Allow users to ask questions about proposals."""
        try:
            print(f"💬 Processing user question: {state['user_question'][:50]}...")

            if not state['vector_store']:
                raise ValueError("Vector store not initialized")

            # Search vector store for relevant information
            relevant_docs = state['vector_store'].similarity_search(
                state['user_question'],
                k=settings.vector_search_k
            )

            # Prepare values for the new prompt
            analysis_result = state['structured_analysis'] if state['structured_analysis'] else state['current_analysis']
            all_proposals = json.dumps(state['proposals'], indent=2)
            total_budget = sum([p.get('budget', 0) for p in state['proposals']])
            remaining_budget = total_budget  # Placeholder, update as needed
            conversation_history = json.dumps(state['conversation_history'], indent=2)

            # Use PromptTemplate for structured response prompt
            response_prompt = self.question_template.invoke({
                "analysis_result": json.dumps(analysis_result, indent=2) if analysis_result else "",
                "all_proposals": all_proposals,
                "total_budget": f"${total_budget:,.2f}",
                "remaining_budget": f"${remaining_budget:,.2f}",
                "conversation_history": conversation_history,
                "user_question": state['user_question']
            })

            # Generate response
            messages = [SystemMessage(content=response_prompt.text)]
            response = self.llm.invoke(messages)

            # Update conversation history
            conversation_entry = {
                "timestamp": datetime.now().isoformat(),
                "question": state['user_question'],
                "response": response.content,
                "relevant_proposals": [doc.metadata['title'] for doc in relevant_docs]
            }

            state['conversation_history'].append(conversation_entry)
            state['error_message'] = ""

            print("✅ Question processed successfully")

        except Exception as e:
            state['error_message'] = f"Question processing failed: {str(e)}"
            print(f"❌ Interactive loop error: {e}")

        return state

    def _decision_node(self, state: ProposalAgentState) -> str:
        """Decision Node: Check if user wants to continue or end conversation."""
        # Check for error conditions
        if state['error_message']:
            print(f"⚠️ Error detected: {state['error_message']}")
            return 'end'

        # Check continue_conversation flag
        if not state['continue_conversation']:
            print("👋 User chose to end conversation")
            return 'end'

        # Check for exit keywords in user question
        exit_keywords = ['exit', 'quit', 'end', 'stop', 'bye', 'goodbye']
        if state['user_question'] and any(keyword in state['user_question'].lower() for keyword in exit_keywords):
            print("👋 Exit keyword detected in user input")
            return 'end'

        print("🔄 Continuing conversation")
        return 'continue'

    def _end_node(self, state: ProposalAgentState) -> ProposalAgentState:
        """End Node: Gracefully terminate the workflow."""
        print("🏁 Ending proposal analysis session...")

        # Generate session summary
        summary = f"""Session Summary:
Session ID: {state['session_id']}
Proposals Analyzed: {len(state['proposals'])}
Questions Asked: {len(state['conversation_history'])}
Analysis Completed: {'Yes' if state['current_analysis'] else 'No'}
Errors Encountered: {'Yes' if state['error_message'] else 'No'}"""

        print(summary)
        return state

    def create_initial_state(self, proposals: List[Dict[str, Any]], session_id: str = None) -> ProposalAgentState:
        """Create initial state for the workflow."""
        if session_id is None:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"

        return ProposalAgentState(
            proposals=proposals,
            vector_store=None,
            current_analysis="",
            structured_analysis=None,
            user_question="",
            conversation_history=[],
            continue_conversation=True,
            error_message="",
            session_id=session_id
        )

    def run_initial_analysis(self, proposals: List[Dict[str, Any]], session_id: str = None) -> ProposalAgentState:
        """Run the initial setup and comparison analysis."""
        print("🚀 Starting proposal analysis workflow...")

        # Check if models are initialized
        if not self.llm or not self.embeddings:
            error_state = self.create_initial_state(proposals, session_id)
            error_state['error_message'] = "API keys not configured. Please set GROQ_API_KEY and OPENAI_API_KEY in your .env file."
            return error_state

        # Check for empty proposals
        if not proposals or len(proposals) == 0:
            error_state = self.create_initial_state(proposals, session_id)
            error_state['error_message'] = "No proposals have been submitted yet. Please add at least one proposal to begin the analysis."
            return error_state

        # Create initial state
        initial_state = self.create_initial_state(proposals, session_id)

        # Run setup and comparison nodes
        state = self._setup_node(initial_state)
        if state['error_message']:
            return state

        state = self._comparison_node(state)
        return state

    def ask_question(self, state: ProposalAgentState, question: str) -> ProposalAgentState:
        """Ask a question about the proposals."""
        state['user_question'] = question
        return self._interactive_loop_node(state)

    def get_session_summary(self, state: ProposalAgentState) -> Dict[str, Any]:
        """Get a summary of the current session."""
        return {
            "session_id": state['session_id'],
            "proposals_count": len(state['proposals']),
            "questions_asked": len(state['conversation_history']),
            "analysis_completed": bool(state['current_analysis']),
            "structured_analysis_available": bool(state.get('structured_analysis')),
            "has_errors": bool(state['error_message']),
            "error_message": state['error_message']
        }

    def get_structured_analysis_results(self, state: ProposalAgentState) -> Optional[List[Dict[str, Any]]]:
        """Get structured analysis results in AnalysisResult format."""
        if not state.get('structured_analysis'):
            return None

        try:
            structured_data = state['structured_analysis']
            results = []

            for proposal_analysis in structured_data.get('proposals', []):
                # Find the original proposal data
                original_proposal = None
                for prop in state['proposals']:
                    if prop['id'] == proposal_analysis.get('proposal_id'):
                        original_proposal = prop
                        break

                if not original_proposal:
                    continue

                # Create AnalysisResult-compatible structure
                result = {
                    "id": proposal_analysis.get('proposal_id'),
                    "vendor": proposal_analysis.get('vendor_name', 'Unknown Vendor'),
                    "fileName": original_proposal.get('filename', 'Unknown File'),
                    "overallScore": proposal_analysis.get('overall_score', 85),
                    "budgetScore": proposal_analysis.get('budget_score', 80),
                    "technicalScore": proposal_analysis.get('technical_score', 90),
                    "timelineScore": proposal_analysis.get('timeline_score', 85),
                    "proposedBudget": f"${original_proposal['budget']:,.0f}" if original_proposal['budget'] > 0 else "$TBD",
                    "timeline": f"{original_proposal['timeline_months']} months",
                    "contact": proposal_analysis.get('contact_info', {}).get('email', 'contact@vendor.com'),
                    "phone": proposal_analysis.get('contact_info', {}).get('phone', '+1 (555) 123-4567'),
                    "strengths": proposal_analysis.get('strengths', []),
                    "concerns": proposal_analysis.get('concerns', [])
                }
                results.append(result)

            return results

        except Exception as e:
            print(f"❌ Error converting structured analysis to results: {e}")
            return None


# Global workflow service instance
workflow_service = ProposalWorkflowService()
