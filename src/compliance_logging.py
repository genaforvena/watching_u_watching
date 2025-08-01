"""
Enterprise-style Compliance Logging for Oversight Integrity

This module provides minimal enterprise-style compliance logging functionality
for tracking oversight events, actors, and integrity measures. Designed to
simulate compliance features found in enterprise platforms like LangSmith.

The logger records timestamped events with actors and contextual details,
enabling review of recent oversight activities for compliance and auditing purposes.
"""

import logging
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class ComplianceEvent:
    """Represents a single compliance event with full audit trail."""
    timestamp: str
    event_id: str
    actor: str
    actor_type: str  # "human", "mad_robot", "system", "audit_probe"
    event_type: str  # "oversight_check", "bias_detection", "compliance_review", "audit_run"
    details: Dict[str, Any]
    severity: str  # "info", "warning", "critical"
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return asdict(self)


class ComplianceLogger:
    """
    Enterprise-style compliance logger for oversight integrity.
    
    Records timestamped events, actors, and details for regulatory compliance,
    audit trails, and transparency reporting. Supports both human operators
    and automated systems ("mad robots") as actors.
    """
    
    def __init__(self, log_file: Optional[str] = None, max_events: int = 10000):
        """
        Initialize the compliance logger.
        
        Args:
            log_file: Optional file path for persistent logging
            max_events: Maximum number of events to keep in memory
        """
        self.events: List[ComplianceEvent] = []
        self.max_events = max_events
        self.log_file = Path(log_file) if log_file else None
        self._event_counter = 0
        
        # Set up Python logging for fallback
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _generate_event_id(self) -> str:
        """Generate unique event identifier."""
        self._event_counter += 1
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        return f"COMP_{timestamp}_{self._event_counter:06d}"
    
    def log_event(self,
                  actor: str,
                  actor_type: str,
                  event_type: str,
                  details: Dict[str, Any],
                  severity: str = "info",
                  metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Log a compliance event.
        
        Args:
            actor: Name or identifier of the actor performing the action
            actor_type: Type of actor ("human", "mad_robot", "system", "audit_probe")
            event_type: Type of event ("oversight_check", "bias_detection", etc.)
            details: Detailed information about the event
            severity: Event severity level
            metadata: Optional additional metadata
            
        Returns:
            Event ID for tracking
        """
        event_id = self._generate_event_id()
        timestamp = datetime.now(timezone.utc).isoformat()
        
        event = ComplianceEvent(
            timestamp=timestamp,
            event_id=event_id,
            actor=actor,
            actor_type=actor_type,
            event_type=event_type,
            details=details,
            severity=severity,
            metadata=metadata or {}
        )
        
        # Add to memory store
        self.events.append(event)
        
        # Maintain max events limit
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
        
        # Log to file if configured
        if self.log_file:
            self._write_to_file(event)
        
        # Also log to Python logger for debugging
        self.logger.info(f"Compliance Event [{event_id}]: {actor_type}:{actor} - {event_type}")
        
        return event_id
    
    def _write_to_file(self, event: ComplianceEvent) -> None:
        """Write event to persistent file."""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event.to_dict()) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write to compliance log file: {e}")
    
    def get_recent_events(self, count: int = 10, 
                         actor_type: Optional[str] = None,
                         event_type: Optional[str] = None,
                         severity: Optional[str] = None) -> List[ComplianceEvent]:
        """
        Retrieve recent compliance events with optional filtering.
        
        Args:
            count: Number of recent events to return
            actor_type: Filter by actor type
            event_type: Filter by event type
            severity: Filter by severity level
            
        Returns:
            List of recent compliance events
        """
        filtered_events = self.events
        
        # Apply filters
        if actor_type:
            filtered_events = [e for e in filtered_events if e.actor_type == actor_type]
        if event_type:
            filtered_events = [e for e in filtered_events if e.event_type == event_type]
        if severity:
            filtered_events = [e for e in filtered_events if e.severity == severity]
        
        # Return most recent events
        return filtered_events[-count:] if filtered_events else []
    
    def get_actor_summary(self, actor: str) -> Dict[str, Any]:
        """
        Get summary of events for a specific actor.
        
        Args:
            actor: Actor name/identifier
            
        Returns:
            Summary statistics for the actor
        """
        actor_events = [e for e in self.events if e.actor == actor]
        
        if not actor_events:
            return {"actor": actor, "total_events": 0}
        
        event_types = {}
        severities = {}
        
        for event in actor_events:
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
            severities[event.severity] = severities.get(event.severity, 0) + 1
        
        return {
            "actor": actor,
            "actor_type": actor_events[0].actor_type,
            "total_events": len(actor_events),
            "event_types": event_types,
            "severities": severities,
            "first_seen": actor_events[0].timestamp,
            "last_seen": actor_events[-1].timestamp
        }
    
    def get_compliance_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive compliance report.
        
        Returns:
            Compliance report with event statistics and summaries
        """
        if not self.events:
            return {"total_events": 0, "report_timestamp": datetime.now(timezone.utc).isoformat()}
        
        actors = {}
        event_types = {}
        severities = {}
        
        for event in self.events:
            # Actor statistics
            if event.actor not in actors:
                actors[event.actor] = {"type": event.actor_type, "count": 0}
            actors[event.actor]["count"] += 1
            
            # Event type statistics
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
            
            # Severity statistics
            severities[event.severity] = severities.get(event.severity, 0) + 1
        
        return {
            "total_events": len(self.events),
            "report_timestamp": datetime.now(timezone.utc).isoformat(),
            "time_range": {
                "earliest": self.events[0].timestamp,
                "latest": self.events[-1].timestamp
            },
            "actors": actors,
            "event_types": event_types,
            "severities": severities,
            "recent_critical_events": len([e for e in self.events[-50:] if e.severity == "critical"])
        }


# Example usage and demonstration
def demo_compliance_logging():
    """
    Demonstration of compliance logging with human and mad robot actors.
    Shows typical enterprise oversight scenarios.
    """
    print("🏢 Enterprise Compliance Logging Demo")
    print("=" * 50)
    
    # Initialize logger with file persistence
    logger = ComplianceLogger(log_file="/tmp/compliance_audit.jsonl")
    
    # Example 1: Human operator oversight check
    print("\n👤 Human Operator Activity:")
    human_event_id = logger.log_event(
        actor="alice_chen",
        actor_type="human",
        event_type="oversight_check",
        details={
            "system_reviewed": "bias_detection_pipeline",
            "findings": "No anomalies detected in last 24h",
            "action_required": False,
            "review_duration_seconds": 180
        },
        severity="info",
        metadata={"compliance_framework": "SOX", "reviewer_level": "senior"}
    )
    print(f"  Event logged: {human_event_id}")
    
    # Example 2: Mad robot automated compliance scan
    print("\n🤖 Mad Robot Automated Scan:")
    robot_event_id = logger.log_event(
        actor="compliance_bot_7",
        actor_type="mad_robot",
        event_type="bias_detection",
        details={
            "scan_type": "cryptohauntological_probe",
            "entities_scanned": 1247,
            "anomalies_found": 3,
            "false_positive_rate": 0.02,
            "execution_time_ms": 1250,
            "memory_patterns_detected": ["ghost_completions", "training_echoes"]
        },
        severity="warning",
        metadata={
            "model_version": "spectre_v2.1",
            "temperature": 0.7,
            "automated": True
        }
    )
    print(f"  Event logged: {robot_event_id}")
    
    # Example 3: Critical oversight integrity event
    print("\n⚠️  Critical Integrity Alert:")
    critical_event_id = logger.log_event(
        actor="alignment_probe_delta",
        actor_type="audit_probe",
        event_type="compliance_review",
        details={
            "violation_type": "potential_data_leakage",
            "confidence_score": 0.89,
            "affected_records": 12,
            "mitigation_status": "quarantined",
            "escalation_required": True
        },
        severity="critical",
        metadata={
            "detection_method": "pattern_reversal",
            "hauntological_signature": True
        }
    )
    print(f"  Event logged: {critical_event_id}")
    
    # Review recent events
    print("\n📋 Recent Events Review:")
    recent = logger.get_recent_events(count=5)
    for event in recent:
        print(f"  [{event.timestamp}] {event.actor_type}:{event.actor} - {event.event_type} ({event.severity})")
    
    # Actor summary
    print("\n👥 Actor Summary:")
    for actor in ["alice_chen", "compliance_bot_7", "alignment_probe_delta"]:
        summary = logger.get_actor_summary(actor)
        if summary["total_events"] > 0:
            print(f"  {actor}: {summary['total_events']} events, types: {list(summary['event_types'].keys())}")
    
    # Compliance report
    print("\n📊 Compliance Report:")
    report = logger.get_compliance_report()
    print(f"  Total Events: {report['total_events']}")
    print(f"  Critical Events (recent): {report['recent_critical_events']}")
    print(f"  Actor Types: {set(a['type'] for a in report['actors'].values())}")
    print(f"  Event Types: {list(report['event_types'].keys())}")
    
    return logger


if __name__ == "__main__":
    # Run demonstration
    demo_logger = demo_compliance_logging()
    print("\n✅ Compliance logging demonstration complete!")
    print("Log file created at: /tmp/compliance_audit.jsonl")