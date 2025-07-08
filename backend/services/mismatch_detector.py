"""
RFP-Proposal Mismatch Detection Service
Analyzes proposals against RFP requirements to identify mismatches and alignment issues
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from backend.models.schemas import RFPMismatch, RFPAlignment


class RFPMismatchDetector:
    """Service for detecting mismatches between RFP requirements and proposals"""

    def __init__(self):
        """Initialize the mismatch detector"""
        pass

    def analyze_proposal_alignment(self, rfp_data: Dict[str, Any], proposal_data: Dict[str, Any]) -> RFPAlignment:
        """
        Analyze how well a proposal aligns with RFP requirements

        Args:
            rfp_data: RFP document data
            proposal_data: Proposal document data

        Returns:
            RFPAlignment object with detailed alignment analysis
        """
        mismatches = []

        # Analyze budget alignment
        budget_alignment, budget_mismatches = self._analyze_budget_alignment(
            rfp_data, proposal_data)
        mismatches.extend(budget_mismatches)

        # Analyze timeline alignment
        timeline_alignment, timeline_mismatches = self._analyze_timeline_alignment(
            rfp_data, proposal_data)
        mismatches.extend(timeline_mismatches)

        # Analyze technical requirements alignment
        technical_alignment, technical_mismatches = self._analyze_technical_alignment(
            rfp_data, proposal_data)
        mismatches.extend(technical_mismatches)

        # Analyze scope alignment
        scope_alignment, scope_mismatches = self._analyze_scope_alignment(
            rfp_data, proposal_data)
        mismatches.extend(scope_mismatches)

        # Calculate overall alignment score
        overall_alignment = int(
            (budget_alignment + timeline_alignment + technical_alignment + scope_alignment) / 4)

        # Generate alignment summary
        alignment_summary = self._generate_alignment_summary(
            overall_alignment, budget_alignment, timeline_alignment,
            technical_alignment, scope_alignment, mismatches
        )

        return RFPAlignment(
            overall_alignment_score=overall_alignment,
            budget_alignment=budget_alignment,
            timeline_alignment=timeline_alignment,
            technical_alignment=technical_alignment,
            scope_alignment=scope_alignment,
            mismatches=mismatches,
            alignment_summary=alignment_summary
        )

    def _analyze_budget_alignment(self, rfp_data: Dict[str, Any], proposal_data: Dict[str, Any]) -> Tuple[int, List[RFPMismatch]]:
        """Analyze budget alignment between RFP and proposal"""
        mismatches = []
        rfp_budget = rfp_data.get('budget', 0)
        proposal_budget = proposal_data.get('budget', 0)

        print(
            f"🔍 BUDGET DEBUG: RFP budget: {rfp_budget}, Proposal budget: {proposal_budget}")

        if rfp_budget == 0 or proposal_budget == 0:
            print(f"⚠️ BUDGET DEBUG: Missing budget data, returning neutral score")
            return 50, mismatches  # Neutral score if budget info is missing

        # Extract budget range from RFP content if available
        rfp_content = rfp_data.get('content', '').lower()
        budget_range = self._extract_budget_range(rfp_content)

        alignment_score = 100

        # Check if proposal budget exceeds RFP budget significantly
        budget_ratio = proposal_budget / rfp_budget

        if budget_ratio > 1.2:  # More than 20% over budget
            severity = "high" if budget_ratio > 1.5 else "medium"
            mismatches.append(RFPMismatch(
                type="budget",
                severity=severity,
                message=f"Proposal budget (${proposal_budget:,}) exceeds RFP budget (${rfp_budget:,}) by {((budget_ratio - 1) * 100):.1f}%",
                rfp_requirement=f"Budget: ${rfp_budget:,}",
                proposal_value=f"Budget: ${proposal_budget:,}",
                impact="May require budget reallocation or scope reduction"
            ))
            alignment_score = max(20, 100 - int((budget_ratio - 1) * 100))

        elif budget_ratio < 0.5:  # Less than 50% of budget (suspiciously low)
            mismatches.append(RFPMismatch(
                type="budget",
                severity="medium",
                message=f"Proposal budget (${proposal_budget:,}) is significantly lower than RFP budget (${rfp_budget:,})",
                rfp_requirement=f"Budget: ${rfp_budget:,}",
                proposal_value=f"Budget: ${proposal_budget:,}",
                impact="May indicate missing scope or unrealistic pricing"
            ))
            alignment_score = max(60, 100 - int((1 - budget_ratio) * 50))

        return alignment_score, mismatches

    def _analyze_timeline_alignment(self, rfp_data: Dict[str, Any], proposal_data: Dict[str, Any]) -> Tuple[int, List[RFPMismatch]]:
        """Analyze timeline alignment between RFP and proposal"""
        mismatches = []
        rfp_timeline = rfp_data.get('timeline_months', 0)
        proposal_timeline = proposal_data.get('timeline_months', 0)

        print(
            f"🔍 TIMELINE DEBUG: RFP timeline: {rfp_timeline}, Proposal timeline: {proposal_timeline}")

        if rfp_timeline == 0 or proposal_timeline == 0:
            print(f"⚠️ TIMELINE DEBUG: Missing timeline data, returning neutral score")
            return 50, mismatches  # Neutral score if timeline info is missing

        alignment_score = 100
        timeline_ratio = proposal_timeline / rfp_timeline

        if timeline_ratio > 1.3:  # More than 30% longer than expected
            severity = "high" if timeline_ratio > 1.8 else "medium"
            mismatches.append(RFPMismatch(
                type="timeline",
                severity=severity,
                message=f"Proposal timeline ({proposal_timeline} months) exceeds RFP timeline ({rfp_timeline} months) by {((timeline_ratio - 1) * 100):.1f}%",
                rfp_requirement=f"Timeline: {rfp_timeline} months",
                proposal_value=f"Timeline: {proposal_timeline} months",
                impact="May delay project delivery and impact business objectives"
            ))
            alignment_score = max(30, 100 - int((timeline_ratio - 1) * 80))

        # Less than 60% of expected timeline (potentially unrealistic)
        elif timeline_ratio < 0.6:
            mismatches.append(RFPMismatch(
                type="timeline",
                severity="medium",
                message=f"Proposal timeline ({proposal_timeline} months) is significantly shorter than RFP timeline ({rfp_timeline} months)",
                rfp_requirement=f"Timeline: {rfp_timeline} months",
                proposal_value=f"Timeline: {proposal_timeline} months",
                impact="May indicate unrealistic timeline or missing project phases"
            ))
            alignment_score = max(70, 100 - int((1 - timeline_ratio) * 40))

        return alignment_score, mismatches

    def _analyze_technical_alignment(self, rfp_data: Dict[str, Any], proposal_data: Dict[str, Any]) -> Tuple[int, List[RFPMismatch]]:
        """Analyze technical requirements alignment"""
        mismatches = []
        rfp_content = rfp_data.get('content', '').lower()
        proposal_content = proposal_data.get('content', '').lower()

        # Define key technical requirements to check
        technical_keywords = {
            'ai': ['ai', 'artificial intelligence', 'machine learning', 'ml', 'neural network'],
            'cloud': ['cloud', 'aws', 'azure', 'gcp', 'kubernetes', 'docker'],
            'api': ['api', 'rest', 'graphql', 'microservices', 'integration'],
            'database': ['database', 'sql', 'nosql', 'mongodb', 'postgresql', 'mysql'],
            'security': ['security', 'encryption', 'authentication', 'authorization', 'ssl', 'tls'],
            'mobile': ['mobile', 'ios', 'android', 'react native', 'flutter'],
            'web': ['web', 'frontend', 'backend', 'react', 'angular', 'vue']
        }

        missing_requirements = []
        alignment_score = 100

        for category, keywords in technical_keywords.items():
            rfp_mentions = any(keyword in rfp_content for keyword in keywords)
            proposal_mentions = any(
                keyword in proposal_content for keyword in keywords)

            if rfp_mentions and not proposal_mentions:
                missing_requirements.append(category)
                mismatches.append(RFPMismatch(
                    type="technical",
                    severity="high",
                    message=f"RFP requires {category.upper()} capabilities but proposal doesn't address this requirement",
                    rfp_requirement=f"Technical requirement: {category.upper()}",
                    proposal_value="Not mentioned in proposal",
                    impact=f"Missing {category} implementation may affect project success"
                ))

        if missing_requirements:
            alignment_score = max(20, 100 - (len(missing_requirements) * 20))

        return alignment_score, mismatches

    def _analyze_scope_alignment(self, rfp_data: Dict[str, Any], proposal_data: Dict[str, Any]) -> Tuple[int, List[RFPMismatch]]:
        """Analyze scope alignment between RFP and proposal"""
        mismatches = []
        rfp_content = rfp_data.get('content', '').lower()
        proposal_content = proposal_data.get('content', '').lower()

        # Define scope-related keywords
        scope_keywords = {
            'deliverables': ['deliverable', 'delivery', 'output', 'result'],
            'phases': ['phase', 'milestone', 'stage', 'iteration'],
            'support': ['support', 'maintenance', 'warranty', 'training'],
            'documentation': ['documentation', 'manual', 'guide', 'specification'],
            'testing': ['testing', 'qa', 'quality assurance', 'validation']
        }

        alignment_score = 100
        missing_scope = []

        for category, keywords in scope_keywords.items():
            rfp_mentions = any(keyword in rfp_content for keyword in keywords)
            proposal_mentions = any(
                keyword in proposal_content for keyword in keywords)

            if rfp_mentions and not proposal_mentions:
                missing_scope.append(category)
                mismatches.append(RFPMismatch(
                    type="scope",
                    severity="medium",
                    message=f"RFP mentions {category} but proposal doesn't clearly address this scope element",
                    rfp_requirement=f"Scope requirement: {category}",
                    proposal_value="Not clearly addressed in proposal",
                    impact=f"Unclear {category} scope may lead to project disputes"
                ))

        if missing_scope:
            alignment_score = max(40, 100 - (len(missing_scope) * 15))

        return alignment_score, mismatches

    def _extract_budget_range(self, rfp_content: str) -> Optional[Tuple[int, int]]:
        """Extract budget range from RFP content"""
        # Look for budget range patterns like "$100,000 - $200,000" or "$100K-$200K"
        budget_patterns = [
            r'\$(\d{1,3}(?:,\d{3})*)\s*-\s*\$(\d{1,3}(?:,\d{3})*)',
            r'\$(\d+)k\s*-\s*\$(\d+)k',
            r'budget.*?(\d{1,3}(?:,\d{3})*)\s*-\s*(\d{1,3}(?:,\d{3})*)'
        ]

        for pattern in budget_patterns:
            match = re.search(pattern, rfp_content, re.IGNORECASE)
            if match:
                try:
                    min_budget = int(match.group(1).replace(',', ''))
                    max_budget = int(match.group(2).replace(',', ''))
                    return (min_budget, max_budget)
                except ValueError:
                    continue

        return None

    def _generate_alignment_summary(self, overall: int, budget: int, timeline: int,
                                    technical: int, scope: int, mismatches: List[RFPMismatch]) -> str:
        """Generate a human-readable alignment summary"""
        if overall >= 90:
            summary = "Excellent alignment with RFP requirements."
        elif overall >= 75:
            summary = "Good alignment with RFP requirements."
        elif overall >= 60:
            summary = "Moderate alignment with some concerns."
        elif overall >= 40:
            summary = "Poor alignment with significant issues."
        else:
            summary = "Very poor alignment with major mismatches."

        critical_mismatches = [
            m for m in mismatches if m.severity == "critical"]
        high_mismatches = [m for m in mismatches if m.severity == "high"]

        if critical_mismatches:
            summary += f" {len(critical_mismatches)} critical issue(s) identified."
        elif high_mismatches:
            summary += f" {len(high_mismatches)} high-priority issue(s) identified."

        return summary


# Global instance
mismatch_detector = RFPMismatchDetector()
