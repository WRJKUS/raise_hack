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
from datetime import datetime
import uuid

from backend.core.config import settings


class ProposalAgentState(TypedDict):
    """State management for the proposal comparison workflow."""
    proposals: List[Dict[str, Any]]
    vector_store: Optional[Any]  # Chroma vector store
    current_analysis: str
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
of the following {num_proposals} proposals. Include:

1. Executive Summary
2. Budget Analysis (cost comparison and value assessment)
3. Timeline Comparison
4. Risk Assessment
5. Strategic Alignment
6. Recommendations with ranking

Proposals to analyze:
{proposal_summaries}

Please provide a detailed, professional analysis."""
        )

        self.question_template = PromptTemplate.from_template(
            """You are an expert proposal analyst. A user has asked the following question
about the proposals: "{user_question}"

Based on the following relevant proposal information, provide a comprehensive and helpful answer:

{context_info}

Previous analysis context:
{previous_analysis}

Please provide a detailed, accurate response that directly addresses the user's question."""
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
                summary = f"""Proposal: {proposal['title']}
Budget: ${proposal['budget']:,}
Timeline: {proposal['timeline_months']} months
Category: {proposal['category']}
Description: {proposal['content'][:200]}..."""
                proposal_summaries.append(summary)

            # Use PromptTemplate for structured prompt creation
            analysis_prompt = self.analysis_template.invoke({
                "num_proposals": len(state['proposals']),
                "proposal_summaries": "\n\n".join(proposal_summaries)
            })

            # Generate analysis using LLM
            messages = [SystemMessage(content=analysis_prompt.text)]
            response = self.llm.invoke(messages)

            # Update state with analysis
            state['current_analysis'] = response.content
            state['error_message'] = ""

            print("✅ Initial comparison analysis completed")

        except Exception as e:
            state['error_message'] = f"Comparison failed: {str(e)}"
            state['current_analysis'] = "Analysis could not be completed due to an error."
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

            # Prepare context from relevant documents
            context_info = []
            for doc in relevant_docs:
                context_info.append(f"""Proposal: {doc.metadata['title']}
Content: {doc.page_content}...
Budget: ${doc.metadata['budget']:,}
Timeline: {doc.metadata['timeline_months']} months""")

            # Use PromptTemplate for structured response prompt
            response_prompt = self.question_template.invoke({
                "user_question": state['user_question'],
                "context_info": "\n\n".join(context_info),
                "previous_analysis": state['current_analysis'][:500] + "..." if len(state['current_analysis']) > 500 else state['current_analysis']
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
            "has_errors": bool(state['error_message']),
            "error_message": state['error_message']
        }


# Global workflow service instance
workflow_service = ProposalWorkflowService()
