"""
PDF processing service for extracting text from uploaded proposal documents
"""

import io
import uuid
from typing import Dict, Any, Optional
import PyPDF2
import pdfplumber
from datetime import datetime

from backend.core.config import settings


class PDFProcessorService:
    """Service for processing PDF files and extracting proposal information"""
    
    def __init__(self):
        """Initialize the PDF processor service"""
        pass
    
    def extract_text_from_pdf(self, pdf_content: bytes, filename: str = None) -> str:
        """
        Extract text from PDF content using multiple methods for better reliability
        
        Args:
            pdf_content: PDF file content as bytes
            filename: Original filename for logging
            
        Returns:
            Extracted text content
        """
        try:
            # Try pdfplumber first (better for complex layouts)
            text = self._extract_with_pdfplumber(pdf_content)
            if text and len(text.strip()) > 50:  # Reasonable amount of text
                print(f"✅ Successfully extracted text using pdfplumber: {len(text)} characters")
                return text
            
            # Fallback to PyPDF2
            text = self._extract_with_pypdf2(pdf_content)
            if text and len(text.strip()) > 50:
                print(f"✅ Successfully extracted text using PyPDF2: {len(text)} characters")
                return text
            
            # If both methods fail or return minimal text
            return "Error: Could not extract sufficient text from PDF. The file may be image-based or corrupted."
            
        except Exception as e:
            error_msg = f"Error extracting text from PDF {filename or 'unknown'}: {str(e)}"
            print(f"❌ {error_msg}")
            return f"Error: {error_msg}"
    
    def _extract_with_pdfplumber(self, pdf_content: bytes) -> str:
        """Extract text using pdfplumber (better for tables and complex layouts)"""
        text_parts = []
        
        with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(f"--- Page {page_num} ---\n{page_text}\n")
                except Exception as e:
                    print(f"⚠️ Error extracting page {page_num} with pdfplumber: {e}")
                    continue
        
        return "\n".join(text_parts)
    
    def _extract_with_pypdf2(self, pdf_content: bytes) -> str:
        """Extract text using PyPDF2 (fallback method)"""
        text_parts = []
        
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        
        for page_num, page in enumerate(pdf_reader.pages, 1):
            try:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"--- Page {page_num} ---\n{page_text}\n")
            except Exception as e:
                print(f"⚠️ Error extracting page {page_num} with PyPDF2: {e}")
                continue
        
        return "\n".join(text_parts)
    
    def process_proposal_pdf(self, pdf_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Process a proposal PDF and extract structured information
        
        Args:
            pdf_content: PDF file content as bytes
            filename: Original filename
            
        Returns:
            Dictionary with extracted proposal information
        """
        try:
            # Extract text content
            text_content = self.extract_text_from_pdf(pdf_content, filename)
            
            if text_content.startswith("Error:"):
                return {
                    "success": False,
                    "error": text_content,
                    "filename": filename
                }
            
            # Generate unique ID for the proposal
            proposal_id = str(uuid.uuid4())
            
            # Extract basic information (this could be enhanced with NLP)
            proposal_info = self._extract_proposal_info(text_content, filename)
            
            # Create proposal dictionary
            proposal = {
                "id": proposal_id,
                "title": proposal_info.get("title", self._generate_title_from_filename(filename)),
                "content": text_content,
                "budget": proposal_info.get("budget", 0.0),
                "timeline_months": proposal_info.get("timeline_months", 12),
                "category": proposal_info.get("category", "General"),
                "filename": filename,
                "processed_at": datetime.now().isoformat(),
                "text_length": len(text_content)
            }
            
            return {
                "success": True,
                "proposal": proposal,
                "filename": filename
            }
            
        except Exception as e:
            error_msg = f"Error processing proposal PDF {filename}: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "filename": filename
            }
    
    def _extract_proposal_info(self, text_content: str, filename: str) -> Dict[str, Any]:
        """
        Extract structured information from proposal text
        This is a basic implementation that could be enhanced with NLP
        """
        info = {}
        text_lower = text_content.lower()
        
        # Try to extract budget information
        import re
        
        # Look for budget patterns like $100,000 or $100K or 100000
        budget_patterns = [
            r'\$[\d,]+(?:\.\d{2})?',  # $100,000.00
            r'\$\d+k',  # $100K
            r'budget[:\s]+\$?[\d,]+',  # budget: $100,000
            r'cost[:\s]+\$?[\d,]+',  # cost: $100,000
        ]
        
        for pattern in budget_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                # Take the first substantial budget found
                for match in matches:
                    budget_str = re.sub(r'[^\d.]', '', match)
                    try:
                        budget = float(budget_str)
                        if budget > 1000:  # Reasonable minimum budget
                            info["budget"] = budget
                            break
                    except ValueError:
                        continue
                if "budget" in info:
                    break
        
        # Try to extract timeline information
        timeline_patterns = [
            r'(\d+)\s*months?',
            r'(\d+)\s*weeks?',
            r'timeline[:\s]+(\d+)',
        ]
        
        for pattern in timeline_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                try:
                    timeline = int(matches[0])
                    if 'week' in pattern:
                        timeline = max(1, timeline // 4)  # Convert weeks to months
                    info["timeline_months"] = min(timeline, 60)  # Cap at 5 years
                    break
                except ValueError:
                    continue
        
        # Try to determine category based on keywords
        categories = {
            "Technology": ["software", "ai", "machine learning", "cloud", "api", "platform", "system"],
            "Marketing": ["marketing", "advertising", "campaign", "brand", "social media"],
            "Infrastructure": ["infrastructure", "hardware", "network", "server", "datacenter"],
            "Consulting": ["consulting", "advisory", "strategy", "analysis", "assessment"],
            "Training": ["training", "education", "workshop", "certification", "learning"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                info["category"] = category
                break
        
        return info
    
    def _generate_title_from_filename(self, filename: str) -> str:
        """Generate a title from filename if no title is found in the document"""
        # Remove file extension and clean up
        title = filename.rsplit('.', 1)[0]
        title = title.replace('_', ' ').replace('-', ' ')
        title = ' '.join(word.capitalize() for word in title.split())
        return f"Proposal: {title}"


# Global PDF processor service instance
pdf_processor = PDFProcessorService()
