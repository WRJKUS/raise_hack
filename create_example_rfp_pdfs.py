#!/usr/bin/env python3
"""
Script to convert example RFP text files to PDF format
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

def create_pdf_from_text(text_file_path, pdf_file_path):
    """Convert a text file to a formatted PDF"""
    
    # Read the text file
    with open(text_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        pdf_file_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor='#2c3e50'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=12,
        spaceBefore=12,
        textColor='#34495e'
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=10,
        spaceAfter=8,
        spaceBefore=8,
        textColor='#34495e'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        textColor='#2c3e50'
    )
    
    # Build the story (content)
    story = []
    
    # Split content into lines
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        if not line:
            # Empty line - add small spacer
            story.append(Spacer(1, 6))
            continue
        
        # Determine style based on content
        if line.startswith('REQUEST FOR PROPOSAL'):
            # Main title
            story.append(Paragraph(line, title_style))
        elif line.isupper() and len(line) > 3 and not line.startswith('   '):
            # Section headings (all caps)
            story.append(Paragraph(line, heading_style))
        elif line.startswith(('1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ', '8. ', '9. ')):
            # Numbered items
            story.append(Paragraph(line, subheading_style))
        elif line.startswith('   - ') or line.startswith('- '):
            # Bullet points
            story.append(Paragraph(line, body_style))
        elif ':' in line and len(line) < 100:
            # Key-value pairs or short descriptive lines
            story.append(Paragraph(f"<b>{line}</b>", body_style))
        else:
            # Regular body text
            story.append(Paragraph(line, body_style))
    
    # Build PDF
    doc.build(story)
    print(f"✅ Created PDF: {pdf_file_path}")

def main():
    """Main function to create all example RFP PDFs"""
    print("📄 Creating Example RFP PDF Documents")
    print("=" * 50)
    
    # Define the text files and their corresponding PDF names
    rfp_files = [
        {
            'text': 'example_rfp_1_ai_platform.txt',
            'pdf': 'example_rfp_1_ai_platform.pdf',
            'title': 'AI-Powered Customer Service Platform'
        },
        {
            'text': 'example_rfp_2_mobile_app.txt',
            'pdf': 'example_rfp_2_mobile_app.pdf',
            'title': 'Mobile Fitness Tracking Application'
        },
        {
            'text': 'example_rfp_3_ecommerce.txt',
            'pdf': 'example_rfp_3_ecommerce.pdf',
            'title': 'E-Commerce Platform Modernization'
        }
    ]
    
    # Create uploads directory if it doesn't exist
    uploads_dir = 'uploads'
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
        print(f"📁 Created directory: {uploads_dir}")
    
    # Convert each text file to PDF
    for rfp in rfp_files:
        text_path = rfp['text']
        pdf_path = os.path.join(uploads_dir, rfp['pdf'])
        
        if os.path.exists(text_path):
            try:
                create_pdf_from_text(text_path, pdf_path)
                print(f"   📋 {rfp['title']}")
                print(f"   📁 Saved to: {pdf_path}")
                print()
            except Exception as e:
                print(f"❌ Error creating {rfp['pdf']}: {str(e)}")
        else:
            print(f"❌ Text file not found: {text_path}")
    
    print("🎉 PDF creation completed!")
    print("\n📋 Summary of created RFP documents:")
    print("1. AI Platform Development RFP ($750K-$1.2M, 12 months)")
    print("   - Complex AI/ML project with multiple integrations")
    print("   - High budget, long timeline, detailed requirements")
    print()
    print("2. Mobile App Development RFP ($150K-$250K, 20 weeks)")
    print("   - Medium complexity fitness tracking app")
    print("   - Moderate budget, shorter timeline, clear scope")
    print()
    print("3. E-Commerce Platform RFP ($200K-$350K, 20 weeks)")
    print("   - Legacy system modernization project")
    print("   - Medium-high budget, data migration challenges")
    print()
    print("💡 These RFPs demonstrate different:")
    print("   - Project complexities and scopes")
    print("   - Budget ranges and timelines")
    print("   - Technical requirements and challenges")
    print("   - Risk factors and optimization opportunities")
    print()
    print("🧪 Use these files to test the RFP Optimization AI Agent:")
    print("   1. Upload each PDF through the web interface")
    print("   2. Run optimization analysis")
    print("   3. Compare scores across the four dimensions")
    print("   4. Review action items and recommendations")

if __name__ == "__main__":
    # Check if reportlab is available
    try:
        import reportlab
        main()
    except ImportError:
        print("❌ ReportLab library not found.")
        print("📦 Install it with: pip install reportlab")
        print("🔄 Then run this script again to create the PDF files.")
