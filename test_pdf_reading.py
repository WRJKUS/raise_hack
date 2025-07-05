#!/usr/bin/env python3
"""
Test reading the generated PDF files to verify they work with our PDF processing
"""

from app import extract_text_from_pdf
import os

def test_pdf_reading():
    """Test reading the generated PDF files."""
    print("🧪 Testing PDF reading functionality...")
    
    pdf_files = [
        "test_proposal_1_ai_platform.pdf",
        "test_proposal_2_marketing.pdf", 
        "test_proposal_3_cloud.pdf"
    ]
    
    for pdf_file in pdf_files:
        if os.path.exists(pdf_file):
            print(f"\n📄 Testing: {pdf_file}")
            
            try:
                # Read the PDF file
                with open(pdf_file, 'rb') as f:
                    pdf_content = f.read()
                
                # Extract text using our function
                extracted_text = extract_text_from_pdf(pdf_content)
                
                # Check if extraction was successful
                if extracted_text and not extracted_text.startswith("Error"):
                    print(f"  ✅ Successfully extracted {len(extracted_text)} characters")
                    
                    # Show a preview of the extracted text
                    preview = extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text
                    print(f"  📝 Preview: {preview}")
                    
                    # Check for key information
                    if "$" in extracted_text:
                        print("  💰 Budget information detected")
                    if "month" in extracted_text.lower():
                        print("  ⏰ Timeline information detected")
                        
                else:
                    print(f"  ❌ Failed to extract text: {extracted_text}")
                    
            except Exception as e:
                print(f"  ❌ Error reading {pdf_file}: {e}")
        else:
            print(f"  ❌ File not found: {pdf_file}")
    
    print("\n🎉 PDF reading test complete!")

if __name__ == "__main__":
    test_pdf_reading()
