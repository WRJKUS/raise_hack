"""
API router for proposal analysis functionality
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from datetime import datetime

from backend.models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    ErrorResponse
)
from backend.services.workflow import workflow_service
from backend.routers.proposals import uploaded_proposals

router = APIRouter()

# In-memory storage for analysis sessions
analysis_sessions: Dict[str, Dict[str, Any]] = {}


@router.post("/start", response_model=AnalysisResponse)
async def start_analysis(request: AnalysisRequest = None):
    """
    Start proposal analysis workflow
    """
    try:
        # Check if we have proposals to analyze
        if not uploaded_proposals:
            raise HTTPException(
                status_code=400,
                detail="No proposals available for analysis. Please upload proposals first."
            )

        # Get session ID or create new one
        session_id = request.session_id if request else None
        if not session_id:
            session_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Get RFP document ID if provided
        rfp_document_id = request.rfp_document_id if request else None
        rfp_data = None

        # Get RFP document data if ID is provided
        if rfp_document_id:
            if rfp_document_id not in uploaded_proposals:
                raise HTTPException(
                    status_code=404,
                    detail=f"RFP document with ID {rfp_document_id} not found"
                )
            rfp_data = uploaded_proposals[rfp_document_id]

        # Convert uploaded proposals to the format expected by workflow
        proposals_list = list(uploaded_proposals.values())

        # Run initial analysis with RFP context if available
        workflow_state = workflow_service.run_initial_analysis(
            proposals_list, session_id, rfp_data)

        if workflow_state["error_message"]:
            raise HTTPException(
                status_code=500,
                detail=f"Analysis failed: {workflow_state['error_message']}"
            )

        # Store the analysis session
        analysis_sessions[session_id] = {
            "workflow_state": workflow_state,
            "started_at": datetime.now().isoformat(),
            "proposals_count": len(proposals_list)
        }

        return AnalysisResponse(
            session_id=session_id,
            analysis=workflow_state["current_analysis"],
            proposals_count=len(proposals_list)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start analysis: {str(e)}"
        )


@router.get("/status/{session_id}")
async def get_analysis_status(session_id: str):
    """
    Get the status of an analysis session
    """
    try:
        if session_id not in analysis_sessions:
            raise HTTPException(
                status_code=404,
                detail="Analysis session not found"
            )

        session_data = analysis_sessions[session_id]
        workflow_state = session_data["workflow_state"]

        return {
            "session_id": session_id,
            "started_at": session_data["started_at"],
            "proposals_count": session_data["proposals_count"],
            "analysis_completed": bool(workflow_state["current_analysis"]),
            "questions_asked": len(workflow_state["conversation_history"]),
            "has_errors": bool(workflow_state["error_message"]),
            "error_message": workflow_state["error_message"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analysis status: {str(e)}"
        )


@router.get("/result/{session_id}", response_model=AnalysisResponse)
async def get_analysis_result(session_id: str):
    """
    Get the analysis result for a session
    """
    try:
        if session_id not in analysis_sessions:
            raise HTTPException(
                status_code=404,
                detail="Analysis session not found"
            )

        session_data = analysis_sessions[session_id]
        workflow_state = session_data["workflow_state"]

        if not workflow_state["current_analysis"]:
            raise HTTPException(
                status_code=400,
                detail="Analysis not completed yet"
            )

        return AnalysisResponse(
            session_id=session_id,
            analysis=workflow_state["current_analysis"],
            proposals_count=session_data["proposals_count"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analysis result: {str(e)}"
        )


@router.get("/sessions")
async def list_analysis_sessions():
    """
    List all analysis sessions
    """
    try:
        sessions = []
        for session_id, session_data in analysis_sessions.items():
            workflow_state = session_data["workflow_state"]
            sessions.append({
                "session_id": session_id,
                "started_at": session_data["started_at"],
                "proposals_count": session_data["proposals_count"],
                "analysis_completed": bool(workflow_state["current_analysis"]),
                "questions_asked": len(workflow_state["conversation_history"]),
                "has_errors": bool(workflow_state["error_message"])
            })

        return {"sessions": sessions}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list analysis sessions: {str(e)}"
        )


@router.delete("/session/{session_id}")
async def delete_analysis_session(session_id: str):
    """
    Delete an analysis session
    """
    try:
        if session_id in analysis_sessions:
            del analysis_sessions[session_id]

        return {"message": "Analysis session deleted successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete analysis session: {str(e)}"
        )


@router.post("/question/{session_id}")
async def ask_analysis_question(session_id: str, question: str):
    """
    Ask a question about the analysis
    """
    try:
        if session_id not in analysis_sessions:
            raise HTTPException(
                status_code=404,
                detail="Analysis session not found"
            )

        session_data = analysis_sessions[session_id]
        workflow_state = session_data["workflow_state"]

        # Ask the question using the workflow
        updated_state = workflow_service.ask_question(workflow_state, question)
        analysis_sessions[session_id]["workflow_state"] = updated_state

        # Get the latest response
        if updated_state["conversation_history"]:
            latest_conversation = updated_state["conversation_history"][-1]
            return {
                "question": question,
                "response": latest_conversation["response"],
                "relevant_proposals": latest_conversation.get("relevant_proposals", []),
                "timestamp": latest_conversation["timestamp"]
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to process question"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process question: {str(e)}"
        )
