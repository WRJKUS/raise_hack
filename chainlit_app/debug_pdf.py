#!/usr/bin/env python3
"""
Debug script to test PDF extraction from the test proposal file
"""

import PyPDF2
import re
import io

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from PDF file."""
    try:
        with open(file_path, 'rb') as file:
            # Create PDF reader object
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extract text from all pages
            text_content = []
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text_content.append(page.extract_text())
            
            # Join all pages with newlines
            full_text = '\n'.join(text_content)
            
            return full_text
            
    except Exception as e:
        return f"Error extracting PDF content: {str(e)}"

def extract_budget_from_content(content: str) -> int:
    """Extract budget information from content."""
    # Look for budget patterns like $500,000 or Budget: $500,000
    budget_patterns = [
        r'\$[\d,]+',
        r'budget[:\s]+\$?([\d,]+)',
        r'cost[:\s]+\$?([\d,]+)',
        r'price[:\s]+\$?([\d,]+)'
    ]
    
    print("Looking for budget patterns in content...")
    for pattern in budget_patterns:
        matches = re.findall(pattern, content.lower())
        print(f"Pattern '{pattern}' found matches: {matches}")
        if matches:
            # Extract numeric value
            budget_str = matches[0].replace('$', '').replace(',', '')
            try:
                return int(budget_str)
            except ValueError:
                continue
    return 0

def extract_timeline_from_content(content: str) -> int:
    """Extract timeline information from content."""
    # Look for timeline patterns like "12 months" or "Timeline: 12 months"
    timeline_patterns = [
        r'(\d+)\s*months?',
        r'timeline[:\s]+(\d+)\s*months?',
        r'duration[:\s]+(\d+)\s*months?',
        r'(\d+)\s*month\s*timeline'
    ]
    
    print("Looking for timeline patterns in content...")
    for pattern in timeline_patterns:
        matches = re.findall(pattern, content.lower())
        print(f"Pattern '{pattern}' found matches: {matches}")
        if matches:
            try:
                return int(matches[0])
            except ValueError:
                continue
    return 0

if __name__ == "__main__":
    # Test the PDF extraction
    pdf_path = "test_proposal_1_ai_platform.pdf"
    
    print(f"Extracting text from {pdf_path}...")
    text = extract_text_from_pdf(pdf_path)
    
    print("=" * 50)
    print("EXTRACTED TEXT:")
    print("=" * 50)
    print(text)
    print("=" * 50)
    
    print(f"Text length: {len(text)} characters")
    
    # Test budget extraction
    budget = extract_budget_from_content(text)
    print(f"Extracted budget: ${budget}")
    
    # Test timeline extraction
    timeline = extract_timeline_from_content(text)
    print(f"Extracted timeline: {timeline} months")
