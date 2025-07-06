"""
API router for proposal management and file uploads
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import os
import uuid
from datetime import datetime

from backend.models.schemas import (
    ProposalResponse, 
    FileUploadResponse, 
    ErrorResponse,
    AnalysisResult
)
from backend.services.pdf_processor import pdf_processor
from backend.services.workflow import workflow_service
from backend.core.config import settings

router = APIRouter()

# In-memory storage for demo purposes (in production, use a proper database)
uploaded_proposals: Dict[str, Dict[str, Any]] = {}
analysis_results: Dict[str, List[AnalysisResult]] = {}


@router.post("/upload", response_model=FileUploadResponse)
async def upload_proposal(file: UploadFile = File(...)):
    """
    Upload a proposal PDF file for analysis
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed"
            )
        
        # Validate file size
        file_content = await file.read()
        if len(file_content) > settings.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {settings.max_file_size} bytes"
            )
        
        # Process the PDF
        result = pdf_processor.process_proposal_pdf(file_content, file.filename)
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to process PDF: {result['error']}"
            )
        
        # Store the proposal
        proposal = result["proposal"]
        uploaded_proposals[proposal["id"]] = proposal
        
        # Save file to disk for reference
        file_path = os.path.join(settings.upload_directory, f"{proposal['id']}_{file.filename}")
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return FileUploadResponse(
            filename=file.filename,
            file_id=proposal["id"],
            size=len(file_content),
            message="File uploaded and processed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/list", response_model=List[ProposalResponse])
async def list_proposals():
    """
    Get list of all uploaded proposals
    """
    try:
        proposals = []
        for proposal_data in uploaded_proposals.values():
            proposals.append(ProposalResponse(
                id=proposal_data["id"],
                title=proposal_data["title"],
                content=proposal_data["content"][:500] + "..." if len(proposal_data["content"]) > 500 else proposal_data["content"],
                budget=proposal_data["budget"],
                timeline_months=proposal_data["timeline_months"],
                category=proposal_data["category"],
                created_at=datetime.fromisoformat(proposal_data["processed_at"])
            ))
        
        return proposals
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve proposals: {str(e)}"
        )


@router.get("/{proposal_id}", response_model=ProposalResponse)
async def get_proposal(proposal_id: str):
    """
    Get a specific proposal by ID
    """
    try:
        if proposal_id not in uploaded_proposals:
            raise HTTPException(
                status_code=404,
                detail="Proposal not found"
            )
        
        proposal_data = uploaded_proposals[proposal_id]
        return ProposalResponse(
            id=proposal_data["id"],
            title=proposal_data["title"],
            content=proposal_data["content"],
            budget=proposal_data["budget"],
            timeline_months=proposal_data["timeline_months"],
            category=proposal_data["category"],
            created_at=datetime.fromisoformat(proposal_data["processed_at"])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve proposal: {str(e)}"
        )


@router.delete("/{proposal_id}")
async def delete_proposal(proposal_id: str):
    """
    Delete a proposal
    """
    try:
        if proposal_id not in uploaded_proposals:
            raise HTTPException(
                status_code=404,
                detail="Proposal not found"
            )
        
        # Remove from storage
        proposal_data = uploaded_proposals.pop(proposal_id)
        
        # Remove file from disk
        file_path = os.path.join(settings.upload_directory, f"{proposal_id}_{proposal_data['filename']}")
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return {"message": "Proposal deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete proposal: {str(e)}"
        )


@router.get("/analysis/results", response_model=List[AnalysisResult])
async def get_analysis_results(session_id: str = None):
    """
    Get analysis results for proposals
    This endpoint provides mock data that matches the frontend expectations
    """
    try:
        # If no proposals uploaded, return empty list
        if not uploaded_proposals:
            return []
        
        # Generate mock analysis results based on uploaded proposals
        results = []
        for i, (proposal_id, proposal_data) in enumerate(uploaded_proposals.items()):
            # Generate mock scores (in production, these would come from actual AI analysis)
            base_score = 85 + (i * 3) % 15  # Vary scores between 85-100
            
            result = AnalysisResult(
                id=proposal_id,
                vendor=proposal_data["title"].replace("Proposal: ", ""),
                fileName=proposal_data["filename"],
                overallScore=base_score,
                budgetScore=max(70, base_score - 5),
                technicalScore=min(100, base_score + 5),
                timelineScore=base_score,
                proposedBudget=f"${proposal_data['budget']:,.0f}" if proposal_data['budget'] > 0 else "$TBD",
                timeline=f"{proposal_data['timeline_months']} months",
                contact="contact@vendor.com",  # Mock contact
                phone="+1 (555) 123-4567",  # Mock phone
                strengths=[
                    "Strong technical approach",
                    "Competitive pricing",
                    "Proven track record"
                ],
                concerns=[
                    "Timeline may be aggressive",
                    "Limited local presence"
                ]
            )
            results.append(result)
        
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve analysis results: {str(e)}"
        )
