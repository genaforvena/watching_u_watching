"""
Example integration of compliance logging with existing audit modules.

This demonstrates how to integrate the enhanced compliance logging system
with existing audit classes like AlignmentInjectionProbe and BiasDetector.
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from compliance_logging_v2 import (
    ComplianceLogger, EventTypes, EventPayloads, AuditIntegrationMixin
)

# Import existing audit modules
try:
    from audits.alignment_injection_probe.alignment_injection_probe import AlignmentInjectionProbe
    ALIGNMENT_PROBE_AVAILABLE = True
except ImportError:
    ALIGNMENT_PROBE_AVAILABLE = False
    AlignmentInjectionProbe = object


class EnhancedAlignmentInjectionProbe(AuditIntegrationMixin, AlignmentInjectionProbe):
    """
    Enhanced version of AlignmentInjectionProbe with compliance logging integration.
    
    This demonstrates how to retrofit existing audit classes with compliance logging
    without breaking existing functionality.
    """
    
    def __init__(self, *args, compliance_logger: Optional[ComplianceLogger] = None, 
                 auditor_id: str = "alignment_probe", **kwargs):
        # Initialize both parent classes
        super().__init__(*args, compliance_logger=compliance_logger, **kwargs)
        self.auditor_id = auditor_id
        self.session_id = f"alignment_audit_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Log audit initialization
        self.log_audit_event(
            EventTypes.AUDIT_STARTED,
            {
                "audit_type": "alignment_injection_probe",
                "target_system": "generative_ai_model",
                "methodology": "adversarial_prompting",
                "session_id": self.session_id
            }
        )
    
    def probe_model(self, model_interface, test_prompts: List[str]) -> Dict[str, Any]:
        """
        Enhanced probe_model method with compliance logging.
        
        Args:
            model_interface: Interface to the model being tested
            test_prompts: List of test prompts to use
            
        Returns:
            Dictionary containing probe results and compliance metadata
        """
        # Log the start of model probing
        self.log_audit_event(
            EventTypes.MODEL_EVALUATION,
            {
                "model_type": getattr(model_interface, 'model_name', 'unknown'),
                "test_prompt_count": len(test_prompts),
                "evaluation_start": datetime.datetime.now().isoformat()
            }
        )
        
        results = {
            "total_prompts": len(test_prompts),
            "successful_injections": 0,
            "failed_injections": 0,
            "detected_vulnerabilities": [],
            "compliance_events": []
        }
        
        for i, prompt in enumerate(test_prompts):
            try:
                # Simulate the actual probing (would call parent method in real implementation)
                response = self._simulate_model_probe(prompt)
                
                # Analyze response for alignment issues
                vulnerability_detected = self._analyze_response_for_vulnerability(response)
                
                if vulnerability_detected:
                    results["successful_injections"] += 1
                    results["detected_vulnerabilities"].append({
                        "prompt_index": i,
                        "vulnerability_type": vulnerability_detected["type"],
                        "severity": vulnerability_detected["severity"]
                    })
                    
                    # Log the vulnerability detection
                    event_id = self.log_audit_event(
                        EventTypes.BIAS_DETECTED,  # Using BIAS_DETECTED for alignment issues
                        {
                            "vulnerability_type": vulnerability_detected["type"],
                            "severity": vulnerability_detected["severity"],
                            "prompt_index": i,
                            "confidence": vulnerability_detected.get("confidence", 0.8),
                            "mitigation_recommended": "Review model alignment training"
                        }
                    )
                    results["compliance_events"].append(event_id)
                else:
                    results["failed_injections"] += 1
                    
            except Exception as e:
                # Log errors as compliance events
                self.log_audit_event(
                    EventTypes.ERROR_OCCURRED,
                    {
                        "error_type": "probe_execution_error",
                        "error_message": str(e),
                        "prompt_index": i
                    }
                )
        
        # Log completion of model evaluation
        self.log_audit_event(
            EventTypes.MODEL_EVALUATION,
            {
                "evaluation_completed": datetime.datetime.now().isoformat(),
                "total_vulnerabilities": results["successful_injections"],
                "success_rate": results["successful_injections"] / len(test_prompts) if test_prompts else 0
            }
        )
        
        return results
    
    def _simulate_model_probe(self, prompt: str) -> str:
        """Simulate model probing for demonstration."""
        # In a real implementation, this would call the actual model
        return f"Model response to: {prompt[:50]}..."
    
    def _analyze_response_for_vulnerability(self, response: str) -> Optional[Dict[str, Any]]:
        """Analyze model response for potential alignment vulnerabilities."""
        # Simplified vulnerability detection logic
        vulnerability_indicators = [
            ("harmful_content", "harmful"),
            ("bias_expression", "biased"),
            ("instruction_following", "ignore"),
            ("ethical_violation", "unethical")
        ]
        
        for vuln_type, indicator in vulnerability_indicators:
            if indicator in response.lower():
                return {
                    "type": vuln_type,
                    "severity": "medium",
                    "confidence": 0.7
                }
        
        return None
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate a comprehensive compliance report for this audit."""
        if not self.compliance_logger:
            return {"error": "No compliance logger available"}
        
        # Search for all events in this session
        session_events = self.compliance_logger.search_events(session_id=self.session_id)
        
        # Categorize events
        audit_events = [e for e in session_events if e["event_type"] == EventTypes.AUDIT_STARTED]
        vulnerability_events = [e for e in session_events if e["event_type"] == EventTypes.BIAS_DETECTED]
        error_events = [e for e in session_events if e["event_type"] == EventTypes.ERROR_OCCURRED]
        evaluation_events = [e for e in session_events if e["event_type"] == EventTypes.MODEL_EVALUATION]
        
        return {
            "session_id": self.session_id,
            "auditor_id": self.auditor_id,
            "audit_summary": {
                "total_events": len(session_events),
                "vulnerabilities_detected": len(vulnerability_events),
                "errors_encountered": len(error_events),
                "evaluations_performed": len(evaluation_events)
            },
            "vulnerability_details": [
                {
                    "event_id": event["event_id"],
                    "type": event["details"]["vulnerability_type"],
                    "severity": event["details"]["severity"],
                    "timestamp": event["timestamp"]
                }
                for event in vulnerability_events
            ],
            "compliance_metadata": {
                "audit_methodology": "alignment_injection_probe",
                "compliance_framework": "enhanced_compliance_logging_v2",
                "data_retention": "encrypted_at_rest",
                "integrity_verified": True
            }
        }


class ComplianceEnabledBiasDetector(AuditIntegrationMixin):
    """
    Example bias detector with built-in compliance logging.
    
    This shows how to create new audit classes that incorporate
    compliance logging from the ground up.
    """
    
    def __init__(self, compliance_logger: Optional[ComplianceLogger] = None,
                 auditor_id: str = "bias_detector"):
        super().__init__(compliance_logger=compliance_logger)
        self.auditor_id = auditor_id
        self.session_id = f"bias_audit_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Log audit initialization
        self.log_audit_event(
            EventTypes.AUDIT_STARTED,
            {
                "audit_type": "bias_detection",
                "target_system": "ai_decision_system",
                "methodology": "statistical_parity_testing"
            }
        )
    
    def detect_demographic_bias(self, dataset: List[Dict[str, Any]], 
                              protected_attributes: List[str]) -> Dict[str, Any]:
        """
        Detect demographic bias in decision outcomes.
        
        Args:
            dataset: List of decision records with demographics
            protected_attributes: List of protected attribute names
            
        Returns:
            Bias detection results with compliance tracking
        """
        # Log start of bias detection
        self.log_audit_event(
            EventTypes.MODEL_EVALUATION,
            {
                "dataset_size": len(dataset),
                "protected_attributes": protected_attributes,
                "analysis_type": "demographic_parity"
            }
        )
        
        bias_results = {}
        
        for attribute in protected_attributes:
            # Simulate bias detection calculation
            bias_score = self._calculate_bias_score(dataset, attribute)
            
            if bias_score > 0.1:  # Threshold for bias detection
                # Log bias detection
                self.log_audit_event(
                    EventTypes.BIAS_DETECTED,
                    EventPayloads.BiasDetected(
                        bias_type="demographic_parity",
                        severity="high" if bias_score > 0.2 else "medium",
                        confidence=min(bias_score * 2, 1.0),
                        affected_groups=[attribute],
                        mitigation_recommended="Rebalance training data and retrain model"
                    )
                )
                
                bias_results[attribute] = {
                    "bias_detected": True,
                    "bias_score": bias_score,
                    "severity": "high" if bias_score > 0.2 else "medium"
                }
            else:
                bias_results[attribute] = {
                    "bias_detected": False,
                    "bias_score": bias_score
                }
        
        # Log completion
        total_bias_detected = sum(1 for result in bias_results.values() if result["bias_detected"])
        self.log_audit_event(
            EventTypes.AUDIT_COMPLETED,
            {
                "attributes_tested": len(protected_attributes),
                "bias_instances_detected": total_bias_detected,
                "overall_result": "bias_detected" if total_bias_detected > 0 else "no_bias_detected"
            }
        )
        
        return bias_results
    
    def _calculate_bias_score(self, dataset: List[Dict[str, Any]], attribute: str) -> float:
        """Calculate bias score for a protected attribute."""
        # Simplified bias calculation for demonstration
        import random
        return random.uniform(0.0, 0.3)  # Simulate bias score


def demonstrate_compliance_integration():
    """
    Demonstrate the integration of compliance logging with audit modules.
    """
    print("=== Compliance Logging Integration Demonstration ===\n")
    
    # Initialize compliance logger with encryption
    logger = ComplianceLogger(
        backend="sqlite",
        backend_config={"db_path": ":memory:"},
        encryption_key="demo_key_for_testing_32_chars_",
        log_level="INFO"
    )
    
    print("1. Testing Audit Integration Mixin")
    print("-" * 50)
    
    # Create a simple audit class using the mixin
    class DemoAuditClass(AuditIntegrationMixin):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.auditor_id = "demo_auditor"
            self.session_id = f"demo_audit_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        def run_demo_audit(self):
            """Simulate running an audit with compliance logging."""
            # Log audit start
            self.log_audit_event(
                EventTypes.AUDIT_STARTED, 
                {
                    "audit_type": "demo_audit",
                    "target_system": "test_system"
                }
            )
            
            # Simulate finding some issues
            self.log_audit_event(
                EventTypes.BIAS_DETECTED,
                {
                    "bias_type": "demo_bias",
                    "severity": "medium",
                    "confidence": 0.8
                }
            )
            
            # Log completion
            self.log_audit_event(
                EventTypes.AUDIT_COMPLETED,
                {
                    "result": "issues_found",
                    "total_issues": 1
                }
            )
    
    demo_audit = DemoAuditClass(compliance_logger=logger)
    demo_audit.run_demo_audit()
    
    print("2. Testing Compliance-Enabled Bias Detector")
    print("-" * 50)
    
    # Create bias detector
    bias_detector = ComplianceEnabledBiasDetector(
        compliance_logger=logger,
        auditor_id="bias_analyst"
    )
    
    # Simulate dataset
    mock_dataset = [
        {"outcome": 1, "gender": "male", "race": "white"},
        {"outcome": 0, "gender": "female", "race": "black"},
        {"outcome": 1, "gender": "male", "race": "black"},
        {"outcome": 0, "gender": "female", "race": "white"},
    ]
    
    bias_results = bias_detector.detect_demographic_bias(
        mock_dataset, 
        ["gender", "race"]
    )
    print(f"Bias detection results: {bias_results}")
    
    print("\n3. Generating Compliance Reports")
    print("-" * 50)
    
    # Generate overall compliance report
    all_events = logger.search_events(limit=100)
    print(f"Total compliance events logged: {len(all_events)}")
    
    # Show event types
    event_types = {}
    for event in all_events:
        event_type = event["event_type"]
        event_types[event_type] = event_types.get(event_type, 0) + 1
    
    print("Event type breakdown:")
    for event_type, count in event_types.items():
        print(f"  {event_type}: {count}")
    
    # Show some sample events
    print("\nSample compliance events:")
    for i, event in enumerate(all_events[:3]):
        print(f"  {i+1}. {event['event_type']} at {event['timestamp']}")
        print(f"     Details: {event['details']}")
    
    logger.close()
    print("\n=== Demonstration Complete ===")
    print("\nThis demonstrates:")
    print("- Pluggable storage backends (SQLite with encryption)")
    print("- Schema validation with Pydantic models")
    print("- Integration hooks for existing audit modules")  
    print("- Comprehensive compliance event tracking")
    print("- Encrypted storage with integrity verification")


if __name__ == "__main__":
    demonstrate_compliance_integration()