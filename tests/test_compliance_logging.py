"""
Tests for compliance_logging module.

Tests the enterprise-style compliance logging functionality for oversight integrity,
including event logging, actor tracking, and compliance reporting features.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from datetime import datetime

# Import the module being tested
import sys
sys.path.insert(0, '/home/runner/work/watching_u_watching/watching_u_watching/src')
from compliance_logging import ComplianceLogger, ComplianceEvent


class TestComplianceEvent:
    """Test the ComplianceEvent dataclass."""
    
    def test_compliance_event_creation(self):
        """Test basic compliance event creation."""
        event = ComplianceEvent(
            timestamp="2024-01-01T00:00:00Z",
            event_id="TEST_001",
            actor="test_user",
            actor_type="human",
            event_type="oversight_check",
            details={"test": "data"},
            severity="info"
        )
        
        assert event.timestamp == "2024-01-01T00:00:00Z"
        assert event.event_id == "TEST_001"
        assert event.actor == "test_user"
        assert event.actor_type == "human"
        assert event.event_type == "oversight_check"
        assert event.details == {"test": "data"}
        assert event.severity == "info"
        assert event.metadata is None
    
    def test_compliance_event_to_dict(self):
        """Test event serialization to dictionary."""
        event = ComplianceEvent(
            timestamp="2024-01-01T00:00:00Z",
            event_id="TEST_001",
            actor="test_user",
            actor_type="human",
            event_type="oversight_check",
            details={"test": "data"},
            severity="info",
            metadata={"extra": "info"}
        )
        
        event_dict = event.to_dict()
        assert isinstance(event_dict, dict)
        assert event_dict["timestamp"] == "2024-01-01T00:00:00Z"
        assert event_dict["event_id"] == "TEST_001"
        assert event_dict["metadata"] == {"extra": "info"}


class TestComplianceLogger:
    """Test the ComplianceLogger class."""
    
    def test_logger_initialization(self):
        """Test logger initialization."""
        logger = ComplianceLogger()
        assert logger.events == []
        assert logger.max_events == 10000
        assert logger.log_file is None
        assert logger._event_counter == 0
    
    def test_logger_with_file(self):
        """Test logger initialization with file."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            logger = ComplianceLogger(log_file=tmp.name)
            assert logger.log_file == Path(tmp.name)
    
    def test_event_id_generation(self):
        """Test unique event ID generation."""
        logger = ComplianceLogger()
        
        id1 = logger._generate_event_id()
        id2 = logger._generate_event_id()
        
        assert id1 != id2
        assert id1.startswith("COMP_")
        assert id2.startswith("COMP_")
        assert logger._event_counter == 2
    
    def test_log_event_basic(self):
        """Test basic event logging."""
        logger = ComplianceLogger()
        
        event_id = logger.log_event(
            actor="test_human",
            actor_type="human",
            event_type="oversight_check",
            details={"system": "test_system"},
            severity="info"
        )
        
        assert len(logger.events) == 1
        assert event_id.startswith("COMP_")
        
        event = logger.events[0]
        assert event.actor == "test_human"
        assert event.actor_type == "human"
        assert event.event_type == "oversight_check"
        assert event.details == {"system": "test_system"}
        assert event.severity == "info"
    
    def test_log_event_with_metadata(self):
        """Test event logging with metadata."""
        logger = ComplianceLogger()
        
        event_id = logger.log_event(
            actor="mad_robot_1",
            actor_type="mad_robot",
            event_type="bias_detection",
            details={"anomalies": 5},
            severity="warning",
            metadata={"model_version": "v2.1"}
        )
        
        event = logger.events[0]
        assert event.metadata == {"model_version": "v2.1"}
    
    def test_max_events_limit(self):
        """Test that logger respects max events limit."""
        logger = ComplianceLogger(max_events=3)
        
        # Add 5 events
        for i in range(5):
            logger.log_event(
                actor=f"actor_{i}",
                actor_type="human",
                event_type="test",
                details={"index": i}
            )
        
        # Should only keep the last 3
        assert len(logger.events) == 3
        assert logger.events[0].details["index"] == 2
        assert logger.events[1].details["index"] == 3
        assert logger.events[2].details["index"] == 4
    
    def test_get_recent_events_basic(self):
        """Test retrieving recent events."""
        logger = ComplianceLogger()
        
        # Add multiple events
        for i in range(5):
            logger.log_event(
                actor=f"actor_{i}",
                actor_type="human",
                event_type="test",
                details={"index": i}
            )
        
        recent = logger.get_recent_events(count=3)
        assert len(recent) == 3
        assert recent[0].details["index"] == 2
        assert recent[1].details["index"] == 3
        assert recent[2].details["index"] == 4
    
    def test_get_recent_events_filtered(self):
        """Test retrieving recent events with filters."""
        logger = ComplianceLogger()
        
        # Add events with different types and actors
        logger.log_event("human1", "human", "oversight_check", {"test": 1})
        logger.log_event("robot1", "mad_robot", "bias_detection", {"test": 2})
        logger.log_event("human2", "human", "compliance_review", {"test": 3})
        logger.log_event("robot2", "mad_robot", "bias_detection", {"test": 4}, severity="critical")
        
        # Filter by actor type
        human_events = logger.get_recent_events(count=10, actor_type="human")
        assert len(human_events) == 2
        assert all(e.actor_type == "human" for e in human_events)
        
        # Filter by event type
        bias_events = logger.get_recent_events(count=10, event_type="bias_detection")
        assert len(bias_events) == 2
        assert all(e.event_type == "bias_detection" for e in bias_events)
        
        # Filter by severity
        critical_events = logger.get_recent_events(count=10, severity="critical")
        assert len(critical_events) == 1
        assert critical_events[0].severity == "critical"
    
    def test_get_actor_summary(self):
        """Test actor summary generation."""
        logger = ComplianceLogger()
        
        # Add events for specific actor
        logger.log_event("alice", "human", "oversight_check", {"test": 1})
        logger.log_event("alice", "human", "compliance_review", {"test": 2})
        logger.log_event("alice", "human", "oversight_check", {"test": 3}, severity="warning")
        logger.log_event("bob", "human", "oversight_check", {"test": 4})
        
        summary = logger.get_actor_summary("alice")
        assert summary["actor"] == "alice"
        assert summary["actor_type"] == "human"
        assert summary["total_events"] == 3
        assert summary["event_types"]["oversight_check"] == 2
        assert summary["event_types"]["compliance_review"] == 1
        assert summary["severities"]["info"] == 2
        assert summary["severities"]["warning"] == 1
        assert "first_seen" in summary
        assert "last_seen" in summary
    
    def test_get_actor_summary_nonexistent(self):
        """Test actor summary for non-existent actor."""
        logger = ComplianceLogger()
        
        summary = logger.get_actor_summary("nonexistent")
        assert summary["actor"] == "nonexistent"
        assert summary["total_events"] == 0
    
    def test_get_compliance_report(self):
        """Test compliance report generation."""
        logger = ComplianceLogger()
        
        # Add variety of events
        logger.log_event("alice", "human", "oversight_check", {"test": 1})
        logger.log_event("robot1", "mad_robot", "bias_detection", {"test": 2}, severity="warning")
        logger.log_event("probe1", "audit_probe", "compliance_review", {"test": 3}, severity="critical")
        
        report = logger.get_compliance_report()
        assert report["total_events"] == 3
        assert "report_timestamp" in report
        assert "time_range" in report
        assert report["time_range"]["earliest"] == logger.events[0].timestamp
        assert report["time_range"]["latest"] == logger.events[-1].timestamp
        
        # Check actor statistics
        assert "alice" in report["actors"]
        assert report["actors"]["alice"]["type"] == "human"
        assert report["actors"]["alice"]["count"] == 1
        
        # Check event type statistics
        assert report["event_types"]["oversight_check"] == 1
        assert report["event_types"]["bias_detection"] == 1
        assert report["event_types"]["compliance_review"] == 1
        
        # Check severity statistics
        assert report["severities"]["info"] == 1
        assert report["severities"]["warning"] == 1
        assert report["severities"]["critical"] == 1
        
        # Check recent critical events count
        assert report["recent_critical_events"] == 1
    
    def test_get_compliance_report_empty(self):
        """Test compliance report for empty logger."""
        logger = ComplianceLogger()
        
        report = logger.get_compliance_report()
        assert report["total_events"] == 0
        assert "report_timestamp" in report
    
    def test_file_logging(self):
        """Test logging to file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp_path = tmp.name
        
        logger = ComplianceLogger(log_file=tmp_path)
        
        # Log an event
        logger.log_event(
            actor="test_actor",
            actor_type="human",
            event_type="test_event",
            details={"key": "value"},
            metadata={"extra": "data"}
        )
        
        # Read back the file
        with open(tmp_path, 'r') as f:
            line = f.readline().strip()
            event_data = json.loads(line)
        
        assert event_data["actor"] == "test_actor"
        assert event_data["actor_type"] == "human"
        assert event_data["event_type"] == "test_event"
        assert event_data["details"] == {"key": "value"}
        assert event_data["metadata"] == {"extra": "data"}
        
        # Clean up
        Path(tmp_path).unlink()
    
    def test_mad_robot_event_logging(self):
        """Test logging events from mad robot actors."""
        logger = ComplianceLogger()
        
        # Log mad robot event
        event_id = logger.log_event(
            actor="compliance_bot_7",
            actor_type="mad_robot",
            event_type="bias_detection",
            details={
                "scan_type": "cryptohauntological_probe",
                "entities_scanned": 1247,
                "anomalies_found": 3,
                "memory_patterns_detected": ["ghost_completions", "training_echoes"]
            },
            severity="warning",
            metadata={"automated": True, "model_version": "spectre_v2.1"}
        )
        
        assert len(logger.events) == 1
        event = logger.events[0]
        assert event.actor == "compliance_bot_7"
        assert event.actor_type == "mad_robot"
        assert event.details["scan_type"] == "cryptohauntological_probe"
        assert event.metadata["automated"] is True
    
    def test_audit_probe_event_logging(self):
        """Test logging events from audit probes."""
        logger = ComplianceLogger()
        
        # Log audit probe event
        event_id = logger.log_event(
            actor="alignment_probe_delta",
            actor_type="audit_probe",
            event_type="compliance_review",
            details={
                "violation_type": "potential_data_leakage",
                "confidence_score": 0.89,
                "affected_records": 12,
                "mitigation_status": "quarantined"
            },
            severity="critical",
            metadata={"hauntological_signature": True}
        )
        
        assert len(logger.events) == 1
        event = logger.events[0]
        assert event.actor == "alignment_probe_delta"
        assert event.actor_type == "audit_probe"
        assert event.severity == "critical"
        assert event.metadata["hauntological_signature"] is True


class TestDemo:
    """Test the demo function."""
    
    @patch('builtins.print')
    def test_demo_compliance_logging(self, mock_print):
        """Test that demo runs without errors."""
        from compliance_logging import demo_compliance_logging
        
        # Should not raise any exceptions
        logger = demo_compliance_logging()
        
        # Verify logger was created with events
        assert len(logger.events) >= 3
        
        # Verify different actor types were used
        actor_types = {event.actor_type for event in logger.events}
        assert "human" in actor_types
        assert "mad_robot" in actor_types
        assert "audit_probe" in actor_types
        
        # Verify print was called (demo produced output)
        assert mock_print.called


if __name__ == "__main__":
    pytest.main([__file__])