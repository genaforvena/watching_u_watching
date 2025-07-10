"""
Compliance Agent for Ethical Compliance Verification

This agent assists in verifying that proposed AI features or model changes
align with ethical principles and regulatory requirements.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from .core import EthicalAIAgent, AgentConfig, RiskLevel


class ComplianceStatus(Enum):
    """Compliance check status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    NEEDS_REVIEW = "needs_review"
    UNKNOWN = "unknown"


@dataclass
class ComplianceCheck:
    """Structure for compliance verification results"""
    check_id: str
    item_description: str
    regulation: str
    status: ComplianceStatus
    confidence: float
    issues_found: List[str]
    recommendations: List[str]
    risk_assessment: str
    checked_at: str


@dataclass
class EthicalPrinciple:
    """Structure for ethical principle validation"""
    principle: str
    description: str
    validation_criteria: List[str]
    weight: float = 1.0


class ComplianceAgent(EthicalAIAgent):
    """
    AI agent for ethical compliance verification and risk assessment.
    
    Capabilities:
    - Verify alignment with ethical principles
    - Check regulatory compliance (NYC LL144, Brazil's AI Act, GDPR)
    - Assess potential harm risks
    - Generate compliance reports
    - Provide mitigation recommendations
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.ethical_principles = self._load_ethical_principles()
        self.regulatory_frameworks = self._load_regulatory_frameworks()
        self.compliance_history = []
    
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        return [
            "Verify ethical principle alignment",
            "Check regulatory compliance",
            "Assess harm risks",
            "Generate compliance reports",
            "Provide mitigation recommendations",
            "Monitor compliance over time"
        ]
    
    def get_description(self) -> str:
        """Return human-readable description of agent purpose"""
        return (
            "Compliance verification agent that ensures all project activities "
            "align with ethical principles and regulatory requirements, with "
            "special focus on 'NO HARM above else' principle."
        )
    
    def _load_ethical_principles(self) -> List[EthicalPrinciple]:
        """Load the ethical principles for watching_u_watching project"""
        return [
            EthicalPrinciple(
                principle="NO HARM above else",
                description="Absolute priority to prevent any form of harm",
                validation_criteria=[
                    "No risk of individual harm",
                    "No risk of group discrimination",
                    "No privacy violations",
                    "No potential for misuse",
                    "Transparent methodology"
                ],
                weight=10.0  # Highest weight
            ),
            EthicalPrinciple(
                principle="Transparency",
                description="All methods and data must be transparent and auditable",
                validation_criteria=[
                    "Open source methodology",
                    "Clear documentation",
                    "Auditable processes",
                    "Public data where appropriate"
                ],
                weight=2.0
            ),
            EthicalPrinciple(
                principle="Accountability",
                description="Clear responsibility and oversight for all actions",
                validation_criteria=[
                    "Human oversight required",
                    "Clear responsibility chains",
                    "Audit trails maintained",
                    "Regular review processes"
                ],
                weight=2.0
            ),
            EthicalPrinciple(
                principle="Fairness",
                description="Equal treatment and non-discrimination",
                validation_criteria=[
                    "No discriminatory bias",
                    "Equal access to benefits",
                    "Inclusive methodology",
                    "Representative testing"
                ],
                weight=2.0
            )
        ]
    
    def _load_regulatory_frameworks(self) -> Dict[str, Dict[str, Any]]:
        """Load regulatory framework requirements"""
        return {
            "NYC_LL144": {
                "name": "NYC Local Law 144",
                "requirements": [
                    "Independent bias audit required",
                    "Public disclosure of audit results",
                    "Specific statistical metrics required",
                    "Annual audit frequency",
                    "Candidate notification requirements"
                ],
                "scope": "Automated Employment Decision Tools in NYC"
            },
            "Brazil_AI_Act": {
                "name": "Brazil's AI Act (Bill No. 2338/2023)",
                "requirements": [
                    "Algorithmic Impact Assessments for high-risk AI",
                    "Bias mitigation measures",
                    "Transparency and explainability",
                    "Public reporting requirements",
                    "Data protection compliance"
                ],
                "scope": "High-risk AI systems including employment tools"
            },
            "GDPR": {
                "name": "General Data Protection Regulation",
                "requirements": [
                    "Data protection by design",
                    "Consent requirements",
                    "Right to explanation",
                    "Data minimization",
                    "Privacy impact assessments"
                ],
                "scope": "Personal data processing in EU"
            }
        }
    
    def verify_ethical_compliance(self, item_description: str, context: Dict[str, Any] = None) -> ComplianceCheck:
        """
        Verify that a proposed item aligns with ethical principles
        
        Args:
            item_description: Description of the item to check
            context: Additional context for the verification
            
        Returns:
            ComplianceCheck result
        """
        operation = f"Verify ethical compliance for: {item_description[:50]}..."
        
        if not self._request_operation(operation, RiskLevel.MEDIUM, context or {}):
            return ComplianceCheck(
                check_id=f"ethical_{datetime.now().timestamp()}",
                item_description=item_description,
                regulation="Ethical Principles",
                status=ComplianceStatus.UNKNOWN,
                confidence=0.0,
                issues_found=["Operation not approved by ethical guardian"],
                recommendations=["Seek human review"],
                risk_assessment="Cannot assess - operation blocked",
                checked_at=datetime.now().isoformat()
            )
        
        issues_found = []
        recommendations = []
        
        # Check against each ethical principle
        for principle in self.ethical_principles:
            violations = self._check_principle_compliance(item_description, principle, context)
            if violations:
                issues_found.extend([f"{principle.principle}: {v}" for v in violations])
                recommendations.append(f"Address {principle.principle} violations")
        
        # Determine overall status
        if not issues_found:
            status = ComplianceStatus.COMPLIANT
            confidence = 0.9
            risk_assessment = "Low risk - no ethical violations detected"
        elif any("NO HARM" in issue for issue in issues_found):
            status = ComplianceStatus.NON_COMPLIANT
            confidence = 0.95
            risk_assessment = "High risk - potential harm detected"
        else:
            status = ComplianceStatus.NEEDS_REVIEW
            confidence = 0.7
            risk_assessment = "Medium risk - minor issues require review"
        
        check = ComplianceCheck(
            check_id=f"ethical_{datetime.now().timestamp()}",
            item_description=item_description,
            regulation="Ethical Principles",
            status=status,
            confidence=confidence,
            issues_found=issues_found,
            recommendations=recommendations,
            risk_assessment=risk_assessment,
            checked_at=datetime.now().isoformat()
        )
        
        self.compliance_history.append(check)
        self.logger.info(f"Ethical compliance check completed: {status.value}")
        
        return check
    
    def _check_principle_compliance(self, item_description: str, principle: EthicalPrinciple, context: Dict[str, Any]) -> List[str]:
        """Check compliance with a specific ethical principle"""
        violations = []
        
        # Simple rule-based checking (would be more sophisticated in production)
        if principle.principle == "NO HARM above else":
            harm_indicators = [
                "personal data", "individual identification", "automated decision",
                "without consent", "discriminatory", "harmful", "bias against"
            ]
            
            for indicator in harm_indicators:
                if indicator in item_description.lower():
                    violations.append(f"Potential harm risk detected: {indicator}")
        
        elif principle.principle == "Transparency":
            transparency_issues = [
                "proprietary", "closed source", "hidden", "secret", "undisclosed"
            ]
            
            for issue in transparency_issues:
                if issue in item_description.lower():
                    violations.append(f"Transparency concern: {issue}")
        
        elif principle.principle == "Accountability":
            if "automated" in item_description.lower() and "human oversight" not in item_description.lower():
                violations.append("Automated process without clear human oversight")
        
        return violations
    
    def verify_regulatory_compliance(self, item_description: str, regulation: str, context: Dict[str, Any] = None) -> ComplianceCheck:
        """
        Verify compliance with specific regulatory framework
        
        Args:
            item_description: Description of the item to check
            regulation: Regulatory framework to check against
            context: Additional context for verification
            
        Returns:
            ComplianceCheck result
        """
        operation = f"Verify {regulation} compliance for: {item_description[:50]}..."
        
        if not self._request_operation(operation, RiskLevel.MEDIUM, context or {}):
            return ComplianceCheck(
                check_id=f"{regulation}_{datetime.now().timestamp()}",
                item_description=item_description,
                regulation=regulation,
                status=ComplianceStatus.UNKNOWN,
                confidence=0.0,
                issues_found=["Operation not approved"],
                recommendations=["Seek human review"],
                risk_assessment="Cannot assess",
                checked_at=datetime.now().isoformat()
            )
        
        if regulation not in self.regulatory_frameworks:
            return ComplianceCheck(
                check_id=f"{regulation}_{datetime.now().timestamp()}",
                item_description=item_description,
                regulation=regulation,
                status=ComplianceStatus.UNKNOWN,
                confidence=0.0,
                issues_found=[f"Unknown regulation: {regulation}"],
                recommendations=["Add regulation to framework"],
                risk_assessment="Cannot assess unknown regulation",
                checked_at=datetime.now().isoformat()
            )
        
        framework = self.regulatory_frameworks[regulation]
        issues_found = []
        recommendations = []
        
        # Check against regulatory requirements
        for requirement in framework["requirements"]:
            if not self._check_requirement_compliance(item_description, requirement, context):
                issues_found.append(f"May not meet requirement: {requirement}")
                recommendations.append(f"Ensure compliance with: {requirement}")
        
        # Determine status
        if not issues_found:
            status = ComplianceStatus.COMPLIANT
            confidence = 0.8
        elif len(issues_found) > len(framework["requirements"]) // 2:
            status = ComplianceStatus.NON_COMPLIANT
            confidence = 0.9
        else:
            status = ComplianceStatus.NEEDS_REVIEW
            confidence = 0.6
        
        check = ComplianceCheck(
            check_id=f"{regulation}_{datetime.now().timestamp()}",
            item_description=item_description,
            regulation=regulation,
            status=status,
            confidence=confidence,
            issues_found=issues_found,
            recommendations=recommendations,
            risk_assessment=f"Regulatory compliance assessment for {framework['name']}",
            checked_at=datetime.now().isoformat()
        )
        
        self.compliance_history.append(check)
        self.logger.info(f"{regulation} compliance check completed: {status.value}")
        
        return check
    
    def _check_requirement_compliance(self, item_description: str, requirement: str, context: Dict[str, Any]) -> bool:
        """Check if item meets a specific regulatory requirement"""
        # Simple rule-based checking (would be more sophisticated in production)
        requirement_lower = requirement.lower()
        description_lower = item_description.lower()
        
        # Basic keyword matching for requirements
        if "audit" in requirement_lower and "audit" not in description_lower:
            return False
        
        if "disclosure" in requirement_lower and "public" not in description_lower:
            return False
        
        if "consent" in requirement_lower and "consent" not in description_lower:
            return False
        
        return True
    
    def generate_compliance_report(self, checks: List[ComplianceCheck] = None) -> Dict[str, Any]:
        """
        Generate a compliance report based on recent checks
        
        Args:
            checks: Optional list of specific checks to include
            
        Returns:
            Comprehensive compliance report
        """
        if checks is None:
            checks = self.compliance_history[-10:]  # Last 10 checks
        
        if not checks:
            return {
                "error": "No compliance checks available",
                "generated_at": datetime.now().isoformat()
            }
        
        # Analyze compliance status
        compliant_count = len([c for c in checks if c.status == ComplianceStatus.COMPLIANT])
        non_compliant_count = len([c for c in checks if c.status == ComplianceStatus.NON_COMPLIANT])
        needs_review_count = len([c for c in checks if c.status == ComplianceStatus.NEEDS_REVIEW])
        
        # Collect all issues and recommendations
        all_issues = []
        all_recommendations = []
        
        for check in checks:
            all_issues.extend(check.issues_found)
            all_recommendations.extend(check.recommendations)
        
        return {
            "summary": {
                "total_checks": len(checks),
                "compliant": compliant_count,
                "non_compliant": non_compliant_count,
                "needs_review": needs_review_count,
                "compliance_rate": compliant_count / len(checks) if checks else 0
            },
            "top_issues": list(set(all_issues))[:5],
            "key_recommendations": list(set(all_recommendations))[:5],
            "regulations_checked": list(set(c.regulation for c in checks)),
            "recent_checks": [
                {
                    "regulation": c.regulation,
                    "status": c.status.value,
                    "confidence": c.confidence,
                    "checked_at": c.checked_at
                }
                for c in checks[-5:]
            ],
            "generated_at": datetime.now().isoformat(),
            "agent_id": self.config.agent_id
        }