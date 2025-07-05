#!/usr/bin/env python3
"""
Generate test proposal PDF files for testing the Chainlit application
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
import os

def create_proposal_pdf(filename, title, company, budget, timeline, content_sections):
    """Create a professional-looking proposal PDF."""

    # Create the PDF document
    doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=1*inch)

    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1,  # Center alignment
        textColor=colors.darkblue
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.darkblue
    )

    # Build the document content
    story = []

    # Title
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 20))

    # Company info
    story.append(Paragraph(f"<b>Submitted by:</b> {company}", styles['Normal']))
    story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 20))

    # Executive Summary Table
    summary_data = [
        ['Project Budget', f'${budget:,}'],
        ['Timeline', f'{timeline} months'],
        ['Proposal Type', 'Professional Services'],
        ['Status', 'Submitted for Review']
    ]

    summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    story.append(summary_table)
    story.append(Spacer(1, 30))

    # Content sections
    for section_title, section_content in content_sections.items():
        story.append(Paragraph(section_title, heading_style))
        story.append(Paragraph(section_content, styles['Normal']))
        story.append(Spacer(1, 15))

    # Build the PDF
    doc.build(story)
    print(f"✅ Generated: {filename}")

def generate_test_proposals():
    """Generate 3 test proposal PDF files."""

    # Install reportlab if not available
    try:
        import reportlab
    except ImportError:
        print("📦 Installing reportlab for PDF generation...")
        os.system("pip install reportlab")
        import reportlab

    print("🏗️ Generating test proposal PDF files...")

    # Proposal 1: AI Customer Service Platform
    proposal1_content = {
        "Executive Summary": """
        TechSolutions Inc. proposes to develop a comprehensive AI-powered customer service platform
        that will revolutionize how your organization handles customer interactions. Our solution
        leverages cutting-edge natural language processing and machine learning technologies to
        provide 24/7 automated customer support with human-level understanding and response quality.
        """,

        "Technical Approach": """
        Our platform will be built using state-of-the-art technologies including:
        • Advanced NLP models for intent recognition and sentiment analysis
        • Multi-language support for global customer base
        • Integration APIs for existing CRM and helpdesk systems
        • Real-time analytics dashboard for performance monitoring
        • Escalation protocols for complex queries requiring human intervention
        """,

        "Project Timeline": """
        Phase 1 (Months 1-3): Requirements gathering and system design
        Phase 2 (Months 4-8): Core platform development and AI model training
        Phase 3 (Months 9-11): Integration testing and user acceptance testing
        Phase 4 (Month 12): Deployment, training, and go-live support
        """,

        "Budget Breakdown": """
        Development Team: $300,000
        AI/ML Infrastructure: $100,000
        Testing and QA: $50,000
        Training and Documentation: $30,000
        Project Management: $20,000
        Total Project Cost: $500,000
        """,

        "Risk Assessment": """
        Low Risk: Our team has extensive experience in AI/ML development
        Mitigation: Regular milestone reviews and agile development methodology
        Contingency: 10% buffer included in timeline and budget estimates
        """
    }

    create_proposal_pdf(
        "test_proposal_1_ai_platform.pdf",
        "AI-Powered Customer Service Platform",
        "TechSolutions Inc.",
        500000,
        12,
        proposal1_content
    )

    # Proposal 2: Digital Marketing Transformation
    proposal2_content = {
        "Executive Summary": """
        MarketingPro Agency presents a comprehensive digital marketing transformation strategy
        designed to modernize your marketing operations and significantly increase customer
        engagement. Our solution includes advanced automation tools, data analytics platforms,
        and integrated campaign management systems.
        """,

        "Service Offerings": """
        • Social Media Automation and Management
        • Advanced Customer Journey Mapping
        • A/B Testing and Conversion Optimization
        • Real-time Analytics and Reporting Dashboard
        • Content Management System Integration
        • ROI Tracking and Performance Metrics
        """,

        "Implementation Plan": """
        Phase 1 (Months 1-2): Current state analysis and strategy development
        Phase 2 (Months 3-5): Platform setup and automation configuration
        Phase 3 (Months 6-7): Campaign launch and optimization
        Phase 4 (Month 8): Training, handover, and ongoing support setup
        """,

        "Investment Details": """
        Platform Licensing: $150,000
        Implementation Services: $100,000
        Training and Support: $30,000
        Campaign Management (6 months): $20,000
        Total Investment: $300,000
        """,

        "Expected ROI": """
        Projected 40% increase in lead generation within 6 months
        25% improvement in conversion rates through optimization
        30% reduction in manual marketing tasks through automation
        Expected ROI: 250% within first year
        """
    }

    create_proposal_pdf(
        "test_proposal_2_marketing.pdf",
        "Digital Marketing Transformation",
        "MarketingPro Agency",
        300000,
        8,
        proposal2_content
    )

    # Proposal 3: Cloud Infrastructure Modernization
    proposal3_content = {
        "Executive Summary": """
        CloudTech Solutions proposes a comprehensive cloud infrastructure modernization project
        to migrate your current systems to a scalable, secure, and cost-effective cloud environment.
        Our solution includes migration to AWS/Azure, implementation of DevOps practices, and
        enhanced security measures.
        """,

        "Technical Solution": """
        • Complete migration to AWS/Azure cloud infrastructure
        • Containerization using Docker and Kubernetes
        • Implementation of CI/CD pipelines for automated deployments
        • Microservices architecture for improved scalability
        • Advanced monitoring and logging systems
        • Disaster recovery and backup solutions
        """,

        "Project Phases": """
        Phase 1 (Months 1-3): Assessment and migration planning
        Phase 2 (Months 4-9): Infrastructure setup and application migration
        Phase 3 (Months 10-12): DevOps implementation and automation
        Phase 4 (Months 13-15): Security hardening and compliance
        """,

        "Cost Analysis": """
        Cloud Infrastructure Setup: $400,000
        Migration Services: $200,000
        DevOps Implementation: $100,000
        Security and Compliance: $50,000
        Total Project Cost: $750,000
        """,

        "Benefits and ROI": """
        • 60% reduction in infrastructure maintenance costs
        • 99.9% uptime guarantee with cloud redundancy
        • Improved scalability for business growth
        • Enhanced security and compliance posture
        • Faster deployment cycles with DevOps practices
        """
    }

    create_proposal_pdf(
        "test_proposal_3_cloud.pdf",
        "Cloud Infrastructure Modernization",
        "CloudTech Solutions",
        750000,
        15,
        proposal3_content
    )

    print("\n🎉 Successfully generated 3 test proposal PDF files!")
    print("\n📄 Generated files:")
    print("  • test_proposal_1_ai_platform.pdf (AI Customer Service - $500K, 12 months)")
    print("  • test_proposal_2_marketing.pdf (Digital Marketing - $300K, 8 months)")
    print("  • test_proposal_3_cloud.pdf (Cloud Infrastructure - $750K, 15 months)")
    print("\n💡 You can now upload these PDF files to test the Chainlit application!")

if __name__ == "__main__":
    generate_test_proposals()
