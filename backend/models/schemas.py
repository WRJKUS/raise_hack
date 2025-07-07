"""
Pydantic models for API request/response schemas
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ProposalBase(BaseModel):
    """Base proposal model"""
    title: str = Field(..., description="Proposal title")
    content: str = Field(..., description="Proposal content/description")
    budget: float = Field(..., description="Proposed budget")
    timeline_months: int = Field(..., description="Timeline in months")
    category: str = Field(..., description="Proposal category")


class ProposalCreate(ProposalBase):
    """Model for creating a new proposal"""
    pass


class ProposalResponse(ProposalBase):
    """Model for proposal response"""
    id: str = Field(..., description="Proposal ID")
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        from_attributes = True


class AnalysisResult(BaseModel):
    """Model for analysis results"""
    id: str = Field(..., description="Analysis ID")
    vendor: str = Field(..., description="Vendor name")
    fileName: str = Field(..., description="Original file name")
    overallScore: int = Field(..., description="Overall score (0-100)")
    budgetScore: int = Field(..., description="Budget score (0-100)")
    technicalScore: int = Field(..., description="Technical score (0-100)")
    timelineScore: int = Field(..., description="Timeline score (0-100)")
    proposedBudget: str = Field(..., description="Proposed budget as string")
    timeline: str = Field(..., description="Timeline as string")
    contact: str = Field(..., description="Contact email")
    phone: str = Field(..., description="Phone number")
    strengths: List[str] = Field(..., description="List of strengths")
    concerns: List[str] = Field(..., description="List of concerns")


class ChatMessage(BaseModel):
    """Model for chat messages"""
    id: int = Field(..., description="Message ID")
    type: str = Field(..., description="Message type: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    """Model for chat requests"""
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")


class ChatResponse(BaseModel):
    """Model for chat responses"""
    message: ChatMessage = Field(..., description="Assistant response message")
    session_id: str = Field(..., description="Session ID")
    relevant_proposals: List[str] = Field(default=[], description="List of relevant proposal titles")


class AnalysisRequest(BaseModel):
    """Model for analysis requests"""
    session_id: Optional[str] = Field(None, description="Session ID")
    
    
class AnalysisResponse(BaseModel):
    """Model for analysis responses"""
    session_id: str = Field(..., description="Session ID")
    analysis: str = Field(..., description="Analysis content")
    proposals_count: int = Field(..., description="Number of proposals analyzed")


class FileUploadResponse(BaseModel):
    """Model for file upload responses"""
    filename: str = Field(..., description="Uploaded filename")
    file_id: str = Field(..., description="File ID")
    size: int = Field(..., description="File size in bytes")
    message: str = Field(..., description="Upload status message")


class ErrorResponse(BaseModel):
    """Model for error responses"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")
    code: Optional[int] = Field(None, description="Error code")
