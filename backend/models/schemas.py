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


class RFPMismatch(BaseModel):
    """Model for RFP-Proposal mismatch detection"""
    type: str = Field(...,
                      description="Type of mismatch: budget, timeline, technical, scope")
    severity: str = Field(...,
                          description="Severity: low, medium, high, critical")
    message: str = Field(...,
                         description="Human-readable mismatch description")
    rfp_requirement: str = Field(..., description="What the RFP specified")
    proposal_value: str = Field(..., description="What the proposal offers")
    impact: str = Field(..., description="Potential impact of this mismatch")


class RFPAlignment(BaseModel):
    """Model for RFP-Proposal alignment analysis"""
    overall_alignment_score: int = Field(..., ge=0, le=100,
                                         description="Overall alignment score (0-100)")
    budget_alignment: int = Field(..., ge=0, le=100,
                                  description="Budget alignment score")
    timeline_alignment: int = Field(..., ge=0, le=100,
                                    description="Timeline alignment score")
    technical_alignment: int = Field(..., ge=0, le=100,
                                     description="Technical requirements alignment score")
    scope_alignment: int = Field(..., ge=0, le=100,
                                 description="Scope alignment score")
    mismatches: List[RFPMismatch] = Field(
        default=[], description="List of detected mismatches")
    alignment_summary: str = Field(...,
                                   description="Summary of alignment analysis")


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
    rfp_alignment: Optional[RFPAlignment] = Field(
        None, description="RFP alignment analysis when RFP is provided")


class ChatMessage(BaseModel):
    """Model for chat messages"""
    id: int = Field(..., description="Message ID")
    type: str = Field(..., description="Message type: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    """Model for chat requests"""
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(
        None, description="Session ID for conversation continuity")


class ChatResponse(BaseModel):
    """Model for chat responses"""
    message: ChatMessage = Field(..., description="Assistant response message")
    session_id: str = Field(..., description="Session ID")
    relevant_proposals: List[str] = Field(
        default=[], description="List of relevant proposal titles")


class AnalysisRequest(BaseModel):
    """Model for analysis requests"""
    session_id: Optional[str] = Field(None, description="Session ID")
    rfp_document_id: Optional[str] = Field(
        None, description="RFP document ID for context-aware analysis")


class AnalysisResponse(BaseModel):
    """Model for analysis responses"""
    session_id: str = Field(..., description="Session ID")
    analysis: str = Field(..., description="Analysis content")
    proposals_count: int = Field(...,
                                 description="Number of proposals analyzed")


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


# RFP Optimization Models

class RFPDimensionAnalysis(BaseModel):
    """Model for individual dimension analysis in RFP optimization"""
    score: int = Field(..., ge=1, le=10,
                       description="Score from 1-10 for this dimension")
    max_score: int = Field(default=10, description="Maximum possible score")
    findings: List[str] = Field(...,
                                description="Key findings for this dimension")
    recommendations: List[str] = Field(
        ..., description="Specific recommendations for improvement")


class RFPTimelineAnalysis(RFPDimensionAnalysis):
    """Model for timeline feasibility analysis"""
    timeline_assessment_score: int = Field(..., ge=1,
                                           le=10, description="Timeline assessment score")
    recommended_timeline_adjustments: List[str] = Field(
        default=[], description="Specific timeline changes with rationale")
    risk_factors: List[str] = Field(
        default=[], description="Identified timeline risks and mitigation strategies")
    historical_comparison: List[str] = Field(
        default=[], description="Similar project examples and their timelines")


class RFPRequirementsAnalysis(RFPDimensionAnalysis):
    """Model for requirements clarity analysis"""
    clarity_score: int = Field(..., ge=1, le=10,
                               description="Requirements clarity score")
    requirement_gaps: List[str] = Field(
        default=[], description="Specific missing or unclear elements")
    suggested_clarifications: List[str] = Field(
        default=[], description="Recommended additions or modifications")
    deliverable_alignment: str = Field(
        ..., description="Assessment of requirement-to-output coherence")


class RFPCostStructureAnalysis(RFPDimensionAnalysis):
    """Model for cost structure and change management analysis"""
    cost_structure_assessment: str = Field(
        ..., description="Flexibility rating and recommendations")
    change_management_readiness: str = Field(
        ..., description="Evaluation of change handling processes")
    missing_cost_categories: List[str] = Field(
        default=[], description="Identified gaps in cost planning")
    recommended_contingencies: List[str] = Field(
        default=[], description="Suggested buffer percentages and categories")


class RFPTCOAnalysis(RFPDimensionAnalysis):
    """Model for Total Cost of Ownership analysis"""
    tco_completeness_score: int = Field(..., ge=1,
                                        le=10, description="TCO completeness score")
    missing_cost_elements: List[str] = Field(
        default=[], description="Specific overlooked expenses")
    lifecycle_cost_projections: List[str] = Field(
        default=[], description="Estimated ongoing costs and recommendations")
    budget_realism_check: str = Field(
        ..., description="Assessment of whether budget aligns with true project costs")


class RFPOptimizationAnalysis(BaseModel):
    """Model for complete RFP optimization analysis"""
    analysis_id: str = Field(..., description="Unique analysis identifier")
    rfp_document_id: str = Field(..., description="RFP document identifier")
    analysis_timestamp: datetime = Field(
        default_factory=datetime.now, description="Analysis timestamp")
    overall_score: int = Field(..., ge=0, le=40,
                               description="Overall RFP health score")
    max_score: int = Field(default=40, description="Maximum possible score")

    # Four critical dimensions
    timeline_feasibility: RFPTimelineAnalysis = Field(
        ..., description="Timeline feasibility analysis")
    requirements_clarity: RFPRequirementsAnalysis = Field(
        ..., description="Requirements clarity analysis")
    cost_flexibility: RFPCostStructureAnalysis = Field(
        ..., description="Cost structure and flexibility analysis")
    tco_analysis: RFPTCOAnalysis = Field(...,
                                         description="Total Cost of Ownership analysis")

    # Priority actions and implementation timeline
    priority_actions: List[str] = Field(..., max_items=3,
                                        description="Top 3 priority actions")
    implementation_timeline: Dict[str, List[str]] = Field(
        ..., description="Implementation timeline with immediate, short-term, and long-term actions")

    # Executive summary
    executive_summary: str = Field(
        ..., description="2-3 sentence overview of key findings and priority recommendations")


class RFPOptimizationRequest(BaseModel):
    """Model for RFP optimization analysis requests"""
    rfp_document_id: str = Field(..., description="RFP document ID to analyze")
    session_id: Optional[str] = Field(
        None, description="Session ID for tracking")
    include_historical_data: bool = Field(
        default=True, description="Whether to include historical project comparisons")


class RFPOptimizationResponse(BaseModel):
    """Model for RFP optimization analysis responses"""
    analysis: RFPOptimizationAnalysis = Field(
        ..., description="Complete RFP optimization analysis")
    session_id: str = Field(..., description="Session ID")
    processing_time_seconds: float = Field(...,
                                           description="Time taken to complete analysis")


class RFPActionItem(BaseModel):
    """Model for RFP optimization action items"""
    id: str = Field(..., description="Action item ID")
    title: str = Field(..., description="Action item title")
    description: str = Field(..., description="Detailed description")
    priority: str = Field(...,
                          description="Priority level: immediate, short-term, or long-term")
    dimension: str = Field(
        ..., description="Related dimension: timeline, requirements, cost, or tco")
    completed: bool = Field(
        default=False, description="Whether the action item is completed")
    created_at: datetime = Field(
        default_factory=datetime.now, description="Creation timestamp")
    completed_at: Optional[datetime] = Field(
        None, description="Completion timestamp")


class RFPActionItemUpdate(BaseModel):
    """Model for updating RFP action items"""
    completed: bool = Field(...,
                            description="Whether the action item is completed")
    notes: Optional[str] = Field(
        None, description="Additional notes about the action item")
