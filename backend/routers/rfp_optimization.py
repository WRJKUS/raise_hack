"""
API router for RFP Optimization functionality
"""

import time
import uuid
from datetime import datetime
from typing import Dict, Any, List

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse

from backend.models.schemas import (
    RFPOptimizationRequest,
    RFPOptimizationResponse,
    RFPOptimizationAnalysis,
    RFPActionItem,
    RFPActionItemUpdate,
    ErrorResponse
)
from backend.services.rfp_optimization_agent import rfp_optimization_agent
from backend.services.pdf_processor import PDFProcessorService
from backend.routers.proposals import uploaded_proposals

router = APIRouter()

# In-memory storage for RFP optimization sessions and action items
rfp_optimization_sessions: Dict[str, Dict[str, Any]] = {}
rfp_action_items: Dict[str, List[RFPActionItem]] = {}

# Initialize PDF processor
pdf_processor = PDFProcessorService()


@router.post("/analyze", response_model=RFPOptimizationResponse)
async def analyze_rfp_document(request: RFPOptimizationRequest):
    """
    Analyze an RFP document for optimization recommendations
    """
    try:
        start_time = time.time()

        # Check if the RFP document exists
        if request.rfp_document_id not in uploaded_proposals:
            raise HTTPException(
                status_code=404,
                detail=f"RFP document with ID {request.rfp_document_id} not found"
            )

        # Get the RFP document data
        rfp_data = uploaded_proposals[request.rfp_document_id]

        # Generate session ID if not provided
        session_id = request.session_id or f"rfp_opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Perform RFP optimization analysis
        analysis = rfp_optimization_agent.analyze_rfp_document(
            rfp_data, session_id)

        # Calculate processing time
        processing_time = time.time() - start_time

        # Store the analysis session
        rfp_optimization_sessions[session_id] = {
            "analysis": analysis,
            "rfp_document_id": request.rfp_document_id,
            "created_at": datetime.now().isoformat(),
            "processing_time": processing_time
        }

        # Generate action items
        action_items = rfp_optimization_agent.generate_action_items(analysis)
        rfp_action_items[session_id] = action_items

        print(
            f"✅ RFP optimization analysis completed for session {session_id}")

        return RFPOptimizationResponse(
            analysis=analysis,
            session_id=session_id,
            processing_time_seconds=processing_time
        )

    except Exception as e:
        print(f"❌ Error in RFP optimization analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"RFP optimization analysis failed: {str(e)}"
        )


@router.get("/analysis/{session_id}", response_model=RFPOptimizationResponse)
async def get_rfp_analysis(session_id: str):
    """
    Get RFP optimization analysis results for a session
    """
    try:
        if session_id not in rfp_optimization_sessions:
            raise HTTPException(
                status_code=404,
                detail="RFP optimization session not found"
            )

        session_data = rfp_optimization_sessions[session_id]

        return RFPOptimizationResponse(
            analysis=session_data["analysis"],
            session_id=session_id,
            processing_time_seconds=session_data["processing_time"]
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error retrieving RFP analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve RFP analysis: {str(e)}"
        )


@router.get("/sessions")
async def list_rfp_optimization_sessions():
    """
    List all RFP optimization sessions
    """
    try:
        sessions_summary = []
        for session_id, session_data in rfp_optimization_sessions.items():
            analysis = session_data["analysis"]
            sessions_summary.append({
                "session_id": session_id,
                "rfp_document_id": session_data["rfp_document_id"],
                "created_at": session_data["created_at"],
                "overall_score": analysis.overall_score,
                "max_score": analysis.max_score,
                "executive_summary": analysis.executive_summary[:100] + "..." if len(analysis.executive_summary) > 100 else analysis.executive_summary
            })

        return {"sessions": sessions_summary, "total_count": len(sessions_summary)}

    except Exception as e:
        print(f"❌ Error listing RFP optimization sessions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list sessions: {str(e)}"
        )


@router.get("/action-items/{session_id}")
async def get_action_items(session_id: str):
    """
    Get action items for an RFP optimization session
    """
    try:
        if session_id not in rfp_action_items:
            raise HTTPException(
                status_code=404,
                detail="Action items not found for this session"
            )

        action_items = rfp_action_items[session_id]

        # Group action items by priority
        grouped_items = {
            "immediate": [item for item in action_items if item.priority == "immediate"],
            "short_term": [item for item in action_items if item.priority == "short_term"],
            "long_term": [item for item in action_items if item.priority == "long_term"]
        }

        return {
            "session_id": session_id,
            "action_items": grouped_items,
            "total_count": len(action_items),
            "completed_count": len([item for item in action_items if item.completed])
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error retrieving action items: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve action items: {str(e)}"
        )


@router.put("/action-items/{session_id}/{item_id}")
async def update_action_item(session_id: str, item_id: str, update: RFPActionItemUpdate):
    """
    Update an action item (mark as completed/incomplete)
    """
    try:
        if session_id not in rfp_action_items:
            raise HTTPException(
                status_code=404,
                detail="Action items not found for this session"
            )

        action_items = rfp_action_items[session_id]

        # Find the action item to update
        item_to_update = None
        for item in action_items:
            if item.id == item_id:
                item_to_update = item
                break

        if not item_to_update:
            raise HTTPException(
                status_code=404,
                detail="Action item not found"
            )

        # Update the action item
        item_to_update.completed = update.completed
        if update.completed:
            item_to_update.completed_at = datetime.now()
        else:
            item_to_update.completed_at = None

        return {
            "message": "Action item updated successfully",
            "item_id": item_id,
            "completed": update.completed
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error updating action item: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update action item: {str(e)}"
        )


@router.post("/upload-rfp")
async def upload_rfp_document(file: UploadFile = File(...)):
    """
    Upload an RFP document for optimization analysis
    """
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported"
            )

        # Read file content
        file_content = await file.read()

        # Process the PDF
        processed_data = pdf_processor.process_proposal_pdf(
            file_content, file.filename)

        if not processed_data.get("success", True):
            raise HTTPException(
                status_code=400,
                detail=f"Failed to process PDF: {processed_data.get('error', 'Unknown error')}"
            )

        # Generate unique ID for the RFP document
        rfp_id = str(uuid.uuid4())

        # Store the processed RFP data
        rfp_data = {
            "id": rfp_id,
            "filename": file.filename,
            "title": processed_data.get("title", file.filename),
            "content": processed_data.get("content", ""),
            "budget": processed_data.get("budget", 0),
            "timeline_months": processed_data.get("timeline_months", 0),
            "category": processed_data.get("category", "RFP"),
            "created_at": datetime.now(),
            "file_size": len(file_content)
        }

        # Store in uploaded proposals (reusing existing storage)
        uploaded_proposals[rfp_id] = rfp_data

        return {
            "rfp_document_id": rfp_id,
            "filename": file.filename,
            "title": rfp_data["title"],
            "file_size": len(file_content),
            "message": "RFP document uploaded successfully and ready for optimization analysis"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error uploading RFP document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload RFP document: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint for RFP optimization service
    """
    try:
        # Check if the RFP optimization agent is properly initialized
        agent_status = "healthy" if rfp_optimization_agent.llm is not None else "not_initialized"

        return {
            "status": "healthy",
            "agent_status": agent_status,
            "active_sessions": len(rfp_optimization_sessions),
            "total_action_items": sum(len(items) for items in rfp_action_items.values()),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )
