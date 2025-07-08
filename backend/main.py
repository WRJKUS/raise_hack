"""
FastAPI backend for Leonardo's RFQ Alchemy Platform
Integrates LangGraph AI agents with proposal comparison workflow
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

from backend.routers import proposals, chat, analysis, rfp_optimization
from backend.core.config import settings

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Leonardo's RFQ Alchemy API",
    description="AI-powered proposal comparison and analysis platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080",
                   "http://localhost:3000", "*"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    proposals.router, prefix="/api/proposals", tags=["proposals"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(rfp_optimization.router,
                   prefix="/api/rfp-optimization", tags=["rfp-optimization"])

# Health check endpoint


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Leonardo's RFQ Alchemy API is running",
        "version": "1.0.0"
    }

# Root endpoint


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Leonardo's RFQ Alchemy API",
        "docs": "/api/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
