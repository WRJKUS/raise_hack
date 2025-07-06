"""
API router for chat assistant functionality
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime

from backend.models.schemas import (
    ChatRequest,
    ChatResponse,
    ChatMessage,
    ErrorResponse
)
from backend.services.workflow import workflow_service
from backend.routers.proposals import uploaded_proposals

router = APIRouter()

# In-memory storage for chat sessions
chat_sessions: Dict[str, Dict[str, Any]] = {}


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Send a message to the chat assistant and get a response
    """
    try:
        # Get or create session
        session_id = request.session_id or f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if session_id not in chat_sessions:
            # Initialize new chat session
            if not uploaded_proposals:
                # No proposals available, provide general response
                response_content = """Hello! I'm your RFP/RFQ Chat Assistant. 

I notice you haven't uploaded any proposals yet. To get started:
1. Go to the Analysis Agent tab
2. Upload your proposal PDF files
3. Start the analysis
4. Then come back here to ask questions about your proposals!

I can help you with questions about budgets, timelines, vendor comparisons, and more once you have proposals loaded."""
            else:
                # Initialize with uploaded proposals
                proposals_list = list(uploaded_proposals.values())
                workflow_state = workflow_service.run_initial_analysis(proposals_list, session_id)
                
                chat_sessions[session_id] = {
                    "workflow_state": workflow_state,
                    "messages": []
                }
                
                response_content = f"""Hello! I'm your RFP/RFQ Chat Assistant. I can see you have {len(proposals_list)} proposal(s) loaded:

{', '.join([p['title'] for p in proposals_list[:3]])}{'...' if len(proposals_list) > 3 else ''}

I can help you with questions about:
- Budget comparisons and analysis
- Timeline and delivery schedules  
- Technical requirements and capabilities
- Vendor strengths and concerns
- Risk assessments
- Strategic recommendations

What would you like to know about your proposals?"""
        else:
            # Existing session - process the question
            workflow_state = chat_sessions[session_id]["workflow_state"]
            
            # Ask the question using the workflow
            updated_state = workflow_service.ask_question(workflow_state, request.message)
            chat_sessions[session_id]["workflow_state"] = updated_state
            
            # Get the latest response from conversation history
            if updated_state["conversation_history"]:
                latest_conversation = updated_state["conversation_history"][-1]
                response_content = latest_conversation["response"]
                relevant_proposals = latest_conversation.get("relevant_proposals", [])
            else:
                response_content = "I'm sorry, I couldn't process your question. Please try again."
                relevant_proposals = []
        
        # Create response message
        response_message = ChatMessage(
            id=len(chat_sessions.get(session_id, {}).get("messages", [])) + 1,
            type="assistant",
            content=response_content,
            timestamp=datetime.now()
        )
        
        # Store message in session
        if session_id not in chat_sessions:
            chat_sessions[session_id] = {"messages": []}
        
        # Store user message
        user_message = ChatMessage(
            id=len(chat_sessions[session_id]["messages"]) + 1,
            type="user",
            content=request.message,
            timestamp=datetime.now()
        )
        chat_sessions[session_id]["messages"].append(user_message)
        chat_sessions[session_id]["messages"].append(response_message)
        
        return ChatResponse(
            message=response_message,
            session_id=session_id,
            relevant_proposals=relevant_proposals if 'relevant_proposals' in locals() else []
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat message: {str(e)}"
        )


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    """
    Get chat history for a session
    """
    try:
        if session_id not in chat_sessions:
            raise HTTPException(
                status_code=404,
                detail="Chat session not found"
            )
        
        return {
            "session_id": session_id,
            "messages": chat_sessions[session_id]["messages"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve chat history: {str(e)}"
        )


@router.delete("/session/{session_id}")
async def clear_chat_session(session_id: str):
    """
    Clear a chat session
    """
    try:
        if session_id in chat_sessions:
            del chat_sessions[session_id]
        
        return {"message": "Chat session cleared successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear chat session: {str(e)}"
        )


@router.get("/sessions")
async def list_chat_sessions():
    """
    List all active chat sessions
    """
    try:
        sessions = []
        for session_id, session_data in chat_sessions.items():
            sessions.append({
                "session_id": session_id,
                "message_count": len(session_data.get("messages", [])),
                "has_workflow": "workflow_state" in session_data
            })
        
        return {"sessions": sessions}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list chat sessions: {str(e)}"
        )
