"""
LangGraph Proposal Analyzer - Chainlit Application

This application integrates with the existing LangGraph proposal comparison workflow
to provide an interactive web interface for proposal analysis and Q&A.
"""

import os
import json
import asyncio
import io
from typing import Dict, List, Any, Optional
from datetime import datetime

import chainlit as cl
from chainlit.types import AskFileResponse

# PDF processing
import PyPDF2

# LangGraph and LangChain imports
from typing import TypedDict
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize models
llm = ChatGroq(model='llama-3.1-8b-instant')
embeddings = OpenAIEmbeddings()

# Prompt templates
analysis_template = PromptTemplate.from_template(
    """You are an expert business analyst. Please provide a comprehensive comparison
of the following {num_proposals} proposals. Include:

1. Executive Summary
2. Key Differences and Similarities
3. Budget Analysis
4. Timeline Comparison
5. Technical Requirements
6. Risk Assessment
7. Recommendations

Proposals to analyze:
{proposal_summaries}

Please provide a detailed, professional analysis that would help decision-makers
choose the best proposal for their needs."""
)

question_template = PromptTemplate.from_template(
    """You are an expert business analyst helping to answer questions about proposal documents.

User Question: {user_question}

Relevant Proposal Information:
{context_info}

Previous Analysis Context:
{previous_analysis}

Please provide a comprehensive, accurate answer based on the proposal information provided.
Be specific and cite relevant details from the proposals when possible."""
)

class ProposalAgentState(TypedDict):
    """State management for the proposal comparison workflow."""
    proposals: List[Dict[str, Any]]
    vector_store: Optional[Any]
    current_analysis: str
    user_question: str
    conversation_history: List[Dict[str, str]]
    continue_conversation: bool
    error_message: str
    session_id: str

# Sample proposals for demonstration
SAMPLE_PROPOSALS = [
    {
        "id": "proposal_001",
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
        "id": "proposal_002",
        "title": "Digital Marketing Transformation",
        "content": """Comprehensive digital marketing transformation proposal focusing on social media
        automation, content management systems, and customer engagement platforms. The solution
        includes advanced analytics, A/B testing capabilities, and integration with existing
        marketing tools. Budget: $300,000. Timeline: 8 months. Key deliverables include:
        automated campaign management, customer journey mapping, and ROI tracking systems.""",
        "budget": 300000,
        "timeline_months": 8,
        "category": "Marketing"
    },
    {
        "id": "proposal_003",
        "title": "Cloud Infrastructure Modernization",
        "content": """Enterprise cloud infrastructure modernization proposal including migration to
        AWS/Azure, implementation of DevOps practices, and security enhancement. The project
        covers containerization, microservices architecture, and automated deployment pipelines.
        Budget: $750,000. Timeline: 15 months. Key components: cloud migration, security
        implementation, monitoring systems, and staff training programs.""",
        "budget": 750000,
        "timeline_months": 15,
        "category": "Infrastructure"
    }
]

def setup_node(state: ProposalAgentState) -> ProposalAgentState:
    """Initial Setup Node: Load proposals into vector store."""
    try:
        # Create documents from proposals for vector store
        documents = []
        for proposal in state['proposals']:
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

        # Create Chroma vector store with session-specific collection
        session_id = cl.context.session.id
        vector_store = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            collection_name=f"proposals_{session_id}",
            persist_directory="./chroma_proposal_db"
        )

        # Update state
        state['vector_store'] = vector_store
        state['error_message'] = ""
        state['session_id'] = session_id

    except Exception as e:
        state['error_message'] = f"Setup failed: {str(e)}"

    return state

def comparison_node(state: ProposalAgentState) -> ProposalAgentState:
    """Comparison Node: Generate initial analysis of proposals."""
    try:
        # Prepare proposal summaries for analysis
        proposal_summaries = []
        for i, proposal in enumerate(state['proposals'], 1):
            summary = f"""
Proposal {i}: {proposal['title']}
Budget: ${proposal['budget']:,}
Timeline: {proposal['timeline_months']} months
Category: {proposal['category']}
Content: {proposal['content'][:500]}...
"""
            proposal_summaries.append(summary)

        # Generate analysis prompt
        analysis_prompt = analysis_template.invoke({
            "num_proposals": len(state['proposals']),
            "proposal_summaries": "\n".join(proposal_summaries)
        })

        # Generate analysis using LLM
        messages = [SystemMessage(content=analysis_prompt.text)]
        response = llm.invoke(messages)

        # Update state with analysis
        state['current_analysis'] = response.content
        state['error_message'] = ""

    except Exception as e:
        state['error_message'] = f"Comparison failed: {str(e)}"
        state['current_analysis'] = "Analysis could not be completed due to an error."

    return state

def interactive_loop_node(state: ProposalAgentState) -> ProposalAgentState:
    """Interactive Loop Node: Allow users to ask questions about proposals."""
    try:
        if not state['vector_store']:
            raise ValueError("Vector store not initialized")

        # Search vector store for relevant information
        relevant_docs = state['vector_store'].similarity_search(
            state['user_question'],
            k=3
        )

        # Prepare context from relevant documents
        context_info = []
        for doc in relevant_docs:
            context_info.append(f"""Proposal: {doc.metadata['title']}
Content: {doc.page_content}
Budget: ${doc.metadata['budget']:,}
Timeline: {doc.metadata['timeline_months']} months""")

        # Generate response prompt
        response_prompt = question_template.invoke({
            "user_question": state['user_question'],
            "context_info": "\n\n".join(context_info),
            "previous_analysis": state['current_analysis'][:500] + "..." if len(state['current_analysis']) > 500 else state['current_analysis']
        })

        # Generate response
        messages = [SystemMessage(content=response_prompt.text)]
        response = llm.invoke(messages)

        # Update conversation history
        conversation_entry = {
            "timestamp": datetime.now().isoformat(),
            "question": state['user_question'],
            "response": response.content,
            "relevant_proposals": [doc.metadata['title'] for doc in relevant_docs]
        }

        state['conversation_history'].append(conversation_entry)
        state['error_message'] = ""

        return response.content

    except Exception as e:
        state['error_message'] = f"Question processing failed: {str(e)}"
        return f"I apologize, but I encountered an error while processing your question: {str(e)}"

# Global state management
workflow_states: Dict[str, ProposalAgentState] = {}

@cl.on_chat_start
async def on_chat_start():
    """Initialize the chat session with workflow setup."""
    session_id = cl.context.session.id

    # Create workflow status element
    workflow_status = cl.Message(
        content=create_workflow_status_display("Not Started")
    )
    await workflow_status.send()

    # Welcome message with action buttons
    actions = [
        cl.Action(name="demo", value="demo", label="🎯 Try Demo", payload={"action": "demo"}),
        cl.Action(name="upload", value="upload", label="📁 Upload Files", payload={"action": "upload"}),
        cl.Action(name="help", value="help", label="❓ Help", payload={"action": "help"})
    ]

    await cl.Message(
        content="# 🚀 Welcome to LangGraph Proposal Analyzer!\n\n"
                "I'm here to help you analyze and compare business proposals using advanced AI workflows.\n\n"
                "**Getting Started:**\n"
                "1. Upload your proposal documents, or\n"
                "2. Try the demo with sample proposals\n"
                "3. Ask questions about your proposals once they're loaded\n\n"
                "**What I can help with:**\n"
                "- Comprehensive proposal analysis and comparison\n"
                "- Budget and timeline analysis\n"
                "- Risk assessment and recommendations\n"
                "- Answering specific questions about proposals\n\n"
                "Choose an option below to get started! 👇",
        actions=actions
    ).send()

@cl.action_callback("demo")
async def on_demo_action(action):
    """Handle demo action button click."""
    await handle_demo_setup()

@cl.action_callback("upload")
async def on_upload_action(action):
    """Handle upload action button click."""
    await handle_file_upload()

@cl.action_callback("help")
async def on_help_action(action):
    """Handle help action button click."""
    await show_help()

def create_workflow_status_display(status: str) -> str:
    """Create a visual workflow status display."""
    steps = [
        ("Setup", "🔧"),
        ("Analysis", "🤖"),
        ("Interactive", "💬"),
        ("Complete", "✅")
    ]

    status_map = {
        "Not Started": 0,
        "Setting Up": 1,
        "Analyzing": 2,
        "Ready": 3,
        "Complete": 4
    }

    current_step = status_map.get(status, 0)

    display = "## 📊 Workflow Status\n\n"
    for i, (step_name, icon) in enumerate(steps):
        if i < current_step:
            display += f"✅ {icon} {step_name} - Complete\n"
        elif i == current_step:
            display += f"🔄 {icon} {step_name} - In Progress\n"
        else:
            display += f"⏳ {icon} {step_name} - Pending\n"

    return display

@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming messages and route to appropriate workflow nodes."""
    session_id = cl.context.session.id
    user_input = message.content.lower().strip()

    # Handle demo request
    if user_input == "demo":
        await handle_demo_setup()
        return

    # Handle file upload request
    if user_input in ["upload", "upload files", "add proposals"]:
        await handle_file_upload()
        return

    # Handle workflow status request
    if user_input in ["status", "workflow status", "progress"]:
        await show_workflow_status()
        return

    # Handle help request
    if user_input in ["help", "commands", "what can you do"]:
        await show_help()
        return

    # Check if workflow is initialized
    if session_id not in workflow_states:
        await cl.Message(
            content="⚠️ Please upload proposals first or type 'demo' to use sample data.\n\n"
                   "**Available commands:**\n"
                   "• `demo` - Use sample proposals\n"
                   "• `upload` - Upload your own proposals\n"
                   "• `help` - Show available commands"
        ).send()
        return

    # Process user question through workflow
    await process_user_question(message.content)

async def handle_demo_setup():
    """Set up the workflow with sample proposals."""
    session_id = cl.context.session.id

    # Show workflow status update
    status_msg = cl.Message(content=create_workflow_status_display("Setting Up"))
    await status_msg.send()

    # Show loading message with progress
    loading_msg = cl.Message(content="🔄 **Step 1/3:** Loading demo proposals...")
    await loading_msg.send()

    try:
        # Initialize state with sample proposals
        initial_state = ProposalAgentState(
            proposals=SAMPLE_PROPOSALS,
            vector_store=None,
            current_analysis="",
            user_question="",
            conversation_history=[],
            continue_conversation=True,
            error_message="",
            session_id=session_id
        )

        # Update progress
        loading_msg.content = "🔄 **Step 2/3:** Setting up vector database..."
        await loading_msg.update()

        # Run setup node
        state = setup_node(initial_state)
        if state['error_message']:
            loading_msg.content = f"❌ Setup failed: {state['error_message']}"
            await loading_msg.update()
            return

        # Update progress
        loading_msg.content = "🔄 **Step 3/3:** Analyzing proposals..."
        await loading_msg.update()
        status_msg.content = create_workflow_status_display("Analyzing")
        await status_msg.update()

        # Run comparison node
        state = comparison_node(state)
        if state['error_message']:
            loading_msg.content = f"❌ Analysis failed: {state['error_message']}"
            await loading_msg.update()
            return

        # Store state globally
        workflow_states[session_id] = state

        # Update status to complete
        status_msg.content = create_workflow_status_display("Ready")
        await status_msg.update()

        # Show proposal cards
        proposal_cards = create_proposal_cards(SAMPLE_PROPOSALS)
        loading_msg.content = f"✅ **Demo Setup Complete!**\n\n{proposal_cards}"
        await loading_msg.update()

        # Send analysis results with better formatting
        await cl.Message(
            content=f"# 📊 Comprehensive Proposal Analysis\n\n{state['current_analysis']}"
        ).send()

        # Create interactive question suggestions
        question_actions = [
            cl.Action(name="q1", value="Which proposal has the best ROI?", label="💰 Best ROI", payload={"question": "Which proposal has the best ROI?"}),
            cl.Action(name="q2", value="Compare the timelines of all proposals", label="⏰ Timeline Comparison", payload={"question": "Compare the timelines of all proposals"}),
            cl.Action(name="q3", value="What are the main technical differences?", label="🔧 Technical Differences", payload={"question": "What are the main technical differences?"}),
            cl.Action(name="q4", value="Which proposal carries the most risk?", label="⚠️ Risk Analysis", payload={"question": "Which proposal carries the most risk?"})
        ]

        await cl.Message(
            content="🤔 **Ready for questions!** Click a suggestion below or ask your own:",
            actions=question_actions
        ).send()

    except Exception as e:
        loading_msg.content = f"❌ Error setting up demo: {str(e)}"
        await loading_msg.update()

def create_proposal_cards(proposals: List[Dict[str, Any]]) -> str:
    """Create formatted proposal cards display."""
    cards = "## 📋 Loaded Proposals\n\n"
    for proposal in proposals:
        cards += f"""**{proposal['title']}**
💰 Budget: ${proposal['budget']:,}
⏰ Timeline: {proposal['timeline_months']} months
📂 Category: {proposal['category']}

---
"""
    return cards

# Action callbacks for question suggestions
@cl.action_callback("q1")
async def on_question_1(action):
    await process_user_question("Which proposal has the best ROI?")

@cl.action_callback("q2")
async def on_question_2(action):
    await process_user_question("Compare the timelines of all proposals")

@cl.action_callback("q3")
async def on_question_3(action):
    await process_user_question("What are the main technical differences?")

@cl.action_callback("q4")
async def on_question_4(action):
    await process_user_question("Which proposal carries the most risk?")

async def handle_file_upload():
    """Handle file upload for proposals."""
    # Show upload instructions
    await cl.Message(
        content="## 📁 Upload Your Proposals\n\n"
                "**Supported formats:** \n"
                "• 📄 **PDF** - Portable Document Format (recommended)\n"
                "• 📝 **TXT** - Plain text files\n"
                "• 📄 **DOCX** - Microsoft Word documents\n"
                "• 📝 **MD** - Markdown files\n\n"
                "**Max size:** 10MB per file\n"
                "**Tip:** PDF files work best! Make sure your proposals include budget and timeline information for better analysis."
    ).send()

    files = None
    while files is None:
        files = await cl.AskFileMessage(
            content="📎 **Select your proposal files:**",
            accept=["text/plain", "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/markdown"],
            max_size_mb=10,
            timeout=180,
        ).send()

    if not files:
        await cl.Message(content="❌ No files uploaded. Please try again or use the demo.").send()
        return

    # Show workflow status
    status_msg = cl.Message(content=create_workflow_status_display("Setting Up"))
    await status_msg.send()

    # Process uploaded files with progress updates
    loading_msg = cl.Message(content=f"🔄 **Step 1/4:** Processing {len(files)} file(s)...")
    await loading_msg.send()

    try:
        proposals = []
        for i, file in enumerate(files, 1):
            loading_msg.content = f"🔄 **Step 1/4:** Processing file {i}/{len(files)}: {file.name}"
            await loading_msg.update()

            # Read file content using the appropriate method based on file type
            content = get_file_content(file, file.name)

            # Extract metadata from content if possible
            budget = extract_budget_from_content(content)
            timeline = extract_timeline_from_content(content)

            # Create proposal object
            proposal = {
                "id": f"uploaded_{len(proposals) + 1}",
                "title": clean_filename(file.name),
                "content": content,
                "budget": budget,
                "timeline_months": timeline,
                "category": "Uploaded"
            }
            proposals.append(proposal)

        # Update progress
        loading_msg.content = "🔄 **Step 2/4:** Setting up vector database..."
        await loading_msg.update()

        # Initialize workflow with uploaded proposals
        await setup_workflow_with_proposals(proposals, status_msg, loading_msg)

        # Show uploaded proposal cards
        proposal_cards = create_proposal_cards(proposals)
        loading_msg.content = f"✅ **Upload Complete!**\n\n{proposal_cards}"
        await loading_msg.update()

    except Exception as e:
        loading_msg.content = f"❌ Error processing files: {str(e)}"
        await loading_msg.update()

def clean_filename(filename: str) -> str:
    """Clean filename to create a proper title."""
    # Remove file extensions
    title = filename.replace('.txt', '').replace('.pdf', '').replace('.docx', '').replace('.md', '')
    # Replace underscores and hyphens with spaces
    title = title.replace('_', ' ').replace('-', ' ')
    # Capitalize words
    return ' '.join(word.capitalize() for word in title.split())

def extract_budget_from_content(content: str) -> int:
    """Extract budget information from content."""
    import re
    # Look for budget patterns like $500,000 or Budget: $500,000
    budget_patterns = [
        r'\$[\d,]+',
        r'budget[:\s]+\$?([\d,]+)',
        r'cost[:\s]+\$?([\d,]+)',
        r'price[:\s]+\$?([\d,]+)'
    ]

    print(f"DEBUG: Extracting budget from content of length {len(content)}")
    if len(content) > 0:
        print(f"DEBUG: Content preview: {content[:200]}")

    for pattern in budget_patterns:
        matches = re.findall(pattern, content.lower())
        print(f"DEBUG: Pattern '{pattern}' found matches: {matches}")
        if matches:
            # Extract numeric value
            budget_str = matches[0].replace('$', '').replace(',', '')
            try:
                budget_value = int(budget_str)
                print(f"DEBUG: Successfully extracted budget: ${budget_value:,}")
                return budget_value
            except ValueError:
                print(f"DEBUG: Failed to convert '{budget_str}' to int")
                continue
    print("DEBUG: No budget found, returning 0")
    return 0

def extract_timeline_from_content(content: str) -> int:
    """Extract timeline information from content."""
    import re
    # Look for timeline patterns like "12 months" or "Timeline: 12 months"
    timeline_patterns = [
        r'(\d+)\s*months?',
        r'timeline[:\s]+(\d+)\s*months?',
        r'duration[:\s]+(\d+)\s*months?',
        r'(\d+)\s*month\s*timeline'
    ]

    print(f"DEBUG: Extracting timeline from content of length {len(content)}")

    for pattern in timeline_patterns:
        matches = re.findall(pattern, content.lower())
        print(f"DEBUG: Pattern '{pattern}' found matches: {matches}")
        if matches:
            try:
                timeline_value = int(matches[0])
                print(f"DEBUG: Successfully extracted timeline: {timeline_value} months")
                return timeline_value
            except ValueError:
                print(f"DEBUG: Failed to convert '{matches[0]}' to int")
                continue
    print("DEBUG: No timeline found, returning 0")
    return 0

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text content from PDF file."""
    try:
        # Create a BytesIO object from the file content
        pdf_file = io.BytesIO(file_content)

        # Create PDF reader object
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        # Extract text from all pages
        text_content = []
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text_content.append(page.extract_text())

        # Join all pages with newlines
        full_text = '\n'.join(text_content)

        # Clean up the text (remove excessive whitespace)
        full_text = ' '.join(full_text.split())

        # Debug: Print extracted text length
        print(f"DEBUG: Extracted {len(full_text)} characters from PDF")
        if len(full_text) > 0:
            print(f"DEBUG: First 200 chars: {full_text[:200]}")

        return full_text

    except Exception as e:
        # If PDF extraction fails, return error message
        error_msg = f"Error extracting PDF content: {str(e)}"
        print(f"DEBUG: {error_msg}")
        return error_msg

def get_file_content(file, filename: str) -> str:
    """Extract content from uploaded file based on file type."""
    try:
        # Get file extension
        file_ext = filename.lower().split('.')[-1] if '.' in filename else ''

        # For Chainlit AskFileResponse, the correct way is to read from the file path
        # Chainlit saves uploaded files to a temporary location accessible via file.path
        if hasattr(file, 'path') and file.path:
            print(f"DEBUG: Reading file from path: {file.path}")

            # Handle PDF files
            if file_ext == 'pdf':
                with open(file.path, 'rb') as f:
                    file_content = f.read()
                print(f"DEBUG: Read {len(file_content)} bytes from PDF file")
                return extract_text_from_pdf(file_content)

            # Handle text-based files (TXT, MD, DOCX)
            else:
                with open(file.path, 'rb') as f:
                    file_content = f.read()
                print(f"DEBUG: Read {len(file_content)} bytes from text file")
                try:
                    return file_content.decode('utf-8')
                except UnicodeDecodeError:
                    return file_content.decode('utf-8', errors='ignore')

        # Fallback: try other methods if path doesn't work
        elif hasattr(file, 'content'):
            print("DEBUG: Using file.content attribute")
            file_content = file.content
            if file_ext == 'pdf':
                return extract_text_from_pdf(file_content)
            else:
                if isinstance(file_content, bytes):
                    return file_content.decode('utf-8', errors='ignore')
                else:
                    return str(file_content)

        else:
            return f"Error: Could not access file content. File object type: {type(file)}, attributes: {[attr for attr in dir(file) if not attr.startswith('_')]}"

    except Exception as e:
        return f"Error processing file {filename}: {str(e)}"

async def setup_workflow_with_proposals(proposals: List[Dict[str, Any]], status_msg=None, loading_msg=None):
    """Set up workflow with provided proposals."""
    session_id = cl.context.session.id

    # Initialize state
    initial_state = ProposalAgentState(
        proposals=proposals,
        vector_store=None,
        current_analysis="",
        user_question="",
        conversation_history=[],
        continue_conversation=True,
        error_message="",
        session_id=session_id
    )

    # Update progress if loading message provided
    if loading_msg:
        loading_msg.content = "🔄 **Step 3/4:** Setting up vector database..."
        await loading_msg.update()

    # Run setup node
    state = setup_node(initial_state)
    if state['error_message']:
        raise Exception(state['error_message'])

    # Update status and progress
    if status_msg:
        status_msg.content = create_workflow_status_display("Analyzing")
        await status_msg.update()
    if loading_msg:
        loading_msg.content = "🔄 **Step 4/4:** Analyzing proposals..."
        await loading_msg.update()

    # Run comparison node
    state = comparison_node(state)
    if state['error_message']:
        raise Exception(state['error_message'])

    # Store state globally
    workflow_states[session_id] = state

    # Update final status
    if status_msg:
        status_msg.content = create_workflow_status_display("Ready")
        await status_msg.update()

    # Send analysis results
    await cl.Message(
        content=f"# 📊 Comprehensive Analysis Results\n\n{state['current_analysis']}"
    ).send()

    # Create question suggestion actions
    question_actions = [
        cl.Action(name="budget_q", value="Which proposal has the highest budget?", label="💰 Budget Analysis", payload={"question": "Which proposal has the highest budget?"}),
        cl.Action(name="timeline_q", value="Compare the timelines", label="⏰ Timeline Comparison", payload={"question": "Compare the timelines"}),
        cl.Action(name="features_q", value="What are the key features?", label="🔧 Feature Analysis", payload={"question": "What are the key features?"}),
        cl.Action(name="risk_q", value="What are the risks?", label="⚠️ Risk Assessment", payload={"question": "What are the risks?"})
    ]

    # Prompt for questions with actions
    await cl.Message(
        content="🤔 **Analysis complete! Ready for your questions.**\n\n"
               "Click a suggestion below or ask your own question:",
        actions=question_actions
    ).send()

# Additional action callbacks for uploaded proposal questions
@cl.action_callback("budget_q")
async def on_budget_question(action):
    await process_user_question("Which proposal has the highest budget?")

@cl.action_callback("timeline_q")
async def on_timeline_question(action):
    await process_user_question("Compare the timelines")

@cl.action_callback("features_q")
async def on_features_question(action):
    await process_user_question("What are the key features?")

@cl.action_callback("risk_q")
async def on_risk_question(action):
    await process_user_question("What are the risks?")

async def show_workflow_status():
    """Show current workflow status."""
    session_id = cl.context.session.id

    if session_id not in workflow_states:
        await cl.Message(content="❌ No active workflow. Please upload proposals or use demo data.").send()
        return

    state = workflow_states[session_id]

    status_content = f"""# 📊 Workflow Status

**Session ID:** `{state['session_id']}`
**Proposals Loaded:** {len(state['proposals'])}
**Analysis Status:** {'✅ Complete' if state['current_analysis'] else '❌ Pending'}
**Questions Asked:** {len(state['conversation_history'])}
**Vector Store:** {'✅ Initialized' if state['vector_store'] else '❌ Not initialized'}
**Errors:** {'❌ ' + state['error_message'] if state['error_message'] else '✅ None'}

**Loaded Proposals:**
""" + "\n".join([f"• {p['title']} (${p['budget']:,}, {p['timeline_months']} months)" for p in state['proposals']])

    await cl.Message(content=status_content).send()

async def show_help():
    """Show help information."""
    help_content = """# 🆘 Help & Commands

**Getting Started:**
• `demo` - Load sample proposals for testing
• `upload` - Upload your own proposal documents
• `status` - Check current workflow status

**Asking Questions:**
Once proposals are loaded, you can ask natural language questions like:
• "Which proposal has the highest budget?"
• "Compare the timelines of all proposals"
• "What are the technical requirements?"
• "Which proposal offers the best value?"
• "What are the main risks in each proposal?"

**Supported File Types:**
• PDF documents (.pdf)
• Text files (.txt)
• Word documents (.docx)
• Markdown files (.md)

**Features:**
• 🤖 AI-powered proposal analysis
• 🔍 Vector-based similarity search
• 📊 Comprehensive comparisons
• 💬 Interactive Q&A
• 📈 Budget and timeline analysis

**Tips:**
• Be specific in your questions for better results
• You can ask follow-up questions to dive deeper
• Use the `status` command to check your session info
"""

    await cl.Message(content=help_content).send()

async def process_user_question(question: str):
    """Process user question through the interactive workflow node."""
    session_id = cl.context.session.id

    # Validate session state
    if session_id not in workflow_states:
        await cl.Message(
            content="❌ **Session Error:** No active workflow found.\n\n"
                   "Please start over by uploading proposals or using the demo."
        ).send()
        return

    state = workflow_states[session_id]

    # Validate workflow state
    if not state.get('vector_store'):
        await cl.Message(
            content="❌ **Workflow Error:** Vector database not initialized.\n\n"
                   "Please restart the workflow."
        ).send()
        return

    # Show processing message with question preview
    question_preview = question[:100] + "..." if len(question) > 100 else question
    processing_msg = cl.Message(
        content=f"🤔 **Analyzing your question:**\n\n*\"{question_preview}\"*\n\n"
                "🔍 Searching through proposals..."
    )
    await processing_msg.send()

    try:
        # Update state with user question
        state['user_question'] = question

        # Add progress indicator
        processing_msg.content = f"🤔 **Analyzing your question:**\n\n*\"{question_preview}\"*\n\n🧠 Generating response..."
        await processing_msg.update()

        # Process through interactive loop node
        response = interactive_loop_node(state)

        # Validate response
        if not response or response.strip() == "":
            response = "I apologize, but I couldn't generate a proper response to your question. Please try rephrasing it or ask a different question."

        # Update processing message with response
        processing_msg.content = f"## 💬 Response\n\n{response}"
        await processing_msg.update()

        # Update global state
        workflow_states[session_id] = state

        # Add follow-up suggestions
        follow_up_actions = [
            cl.Action(name="follow_up", value="Tell me more about this", label="📖 Tell me more", payload={"question": "Tell me more about this"}),
            cl.Action(name="compare", value="How does this compare to other proposals?", label="⚖️ Compare", payload={"question": "How does this compare to other proposals?"}),
            cl.Action(name="details", value="What are the specific details?", label="🔍 More details", payload={"question": "What are the specific details?"})
        ]

        await cl.Message(
            content="**Want to explore further?** Choose an option:",
            actions=follow_up_actions
        ).send()

    except Exception as e:
        error_msg = str(e)
        processing_msg.content = f"❌ **Error Processing Question**\n\n**Error:** {error_msg}\n\n**Troubleshooting:**\n• Try rephrasing your question\n• Make sure your question is about the loaded proposals\n• Check if the workflow is properly initialized\n\n**Need help?** Type `help` for assistance."
        await processing_msg.update()

# Additional action callbacks for follow-up questions
@cl.action_callback("follow_up")
async def on_follow_up(action):
    await process_user_question("Tell me more about this")

@cl.action_callback("compare")
async def on_compare(action):
    await process_user_question("How does this compare to other proposals?")

@cl.action_callback("details")
async def on_details(action):
    await process_user_question("What are the specific details?")

# Enhanced error handling for workflow nodes
def safe_setup_node(state: ProposalAgentState) -> ProposalAgentState:
    """Safely execute setup node with comprehensive error handling."""
    try:
        return setup_node(state)
    except Exception as e:
        state['error_message'] = f"Setup failed: {str(e)}"
        return state

def safe_comparison_node(state: ProposalAgentState) -> ProposalAgentState:
    """Safely execute comparison node with comprehensive error handling."""
    try:
        return comparison_node(state)
    except Exception as e:
        state['error_message'] = f"Analysis failed: {str(e)}"
        state['current_analysis'] = "Analysis could not be completed due to an error."
        return state

def safe_interactive_loop_node(state: ProposalAgentState) -> str:
    """Safely execute interactive loop node with comprehensive error handling."""
    try:
        return interactive_loop_node(state)
    except Exception as e:
        state['error_message'] = f"Question processing failed: {str(e)}"
        return f"I apologize, but I encountered an error while processing your question: {str(e)}"

if __name__ == "__main__":
    cl.run()
