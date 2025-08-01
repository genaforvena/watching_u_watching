"""
Tests for the compliance_logging module.

This test suite validates the functionality of the enterprise-style
compliance logging system for oversight integrity.
"""

import pytest
import tempfile
import os
import datetime
import json
from unittest import mock

# Import the compliance logging module
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from compliance_logging import ComplianceLogger, ComplianceEvent, EventTypes


class TestComplianceEvent:
    """Test cases for the ComplianceEvent class."""
    
    def test_event_creation(self):
        """Test basic event creation."""
        event = ComplianceEvent(
            event_type="test_event",
            details={"key": "value"},
            user_id="test_user",
            session_id="test_session"
        )
        
        assert event.event_type == "test_event"
        assert event.details == {"key": "value"}
        assert event.user_id == "test_user"
        assert event.session_id == "test_session"
        assert isinstance(event.timestamp, datetime.datetime)
        assert event.event_id is not None
    
    def test_event_serialization(self):
        """Test event to_dict and from_dict methods."""
        original_event = ComplianceEvent(
            event_type="test_event",
            details={"key": "value"},
            user_id="test_user"
        )
        
        # Convert to dict and back
        event_dict = original_event.to_dict()
        reconstructed_event = ComplianceEvent.from_dict(event_dict)
        
        assert reconstructed_event.event_type == original_event.event_type
        assert reconstructed_event.details == original_event.details
        assert reconstructed_event.user_id == original_event.user_id
        assert reconstructed_event.event_id == original_event.event_id
        assert reconstructed_event.timestamp == original_event.timestamp


class TestComplianceLogger:
    """Test cases for the ComplianceLogger class."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database file for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name
        yield db_path
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def logger(self):
        """Create an in-memory compliance logger for testing."""
        return ComplianceLogger()
    
    def test_logger_initialization(self, temp_db):
        """Test logger initialization with different configurations."""
        # Test in-memory database
        logger1 = ComplianceLogger()
        assert logger1.db_path == ":memory:"
        logger1.close()
        
        # Test file database
        logger2 = ComplianceLogger(db_path=temp_db)
        assert logger2.db_path == temp_db
        logger2.close()
    
    def test_log_event(self, logger):
        """Test basic event logging functionality."""
        event_id = logger.log_event(
            event_type=EventTypes.AUDIT_STARTED,
            details={"audit_type": "bias_detection"},
            user_id="test_user",
            session_id="test_session"
        )
        
        assert event_id is not None
        assert isinstance(event_id, str)
        
        # Verify event was stored
        event = logger.get_event(event_id)
        assert event is not None
        assert event.event_type == EventTypes.AUDIT_STARTED
        assert event.details == {"audit_type": "bias_detection"}
        assert event.user_id == "test_user"
        assert event.session_id == "test_session"
    
    def test_search_events_by_type(self, logger):
        """Test searching events by event type."""
        # Log multiple events of different types
        logger.log_event(EventTypes.AUDIT_STARTED, {"data": "test1"})
        logger.log_event(EventTypes.BIAS_DETECTED, {"data": "test2"})
        logger.log_event(EventTypes.AUDIT_STARTED, {"data": "test3"})
        
        # Search for audit_started events
        audit_events = logger.search_events(event_type=EventTypes.AUDIT_STARTED)
        assert len(audit_events) == 2
        
        # Search for bias_detected events
        bias_events = logger.search_events(event_type=EventTypes.BIAS_DETECTED)
        assert len(bias_events) == 1
    
    def test_search_events_by_user(self, logger):
        """Test searching events by user ID."""
        logger.log_event(EventTypes.AUDIT_STARTED, {"data": "test1"}, user_id="user1")
        logger.log_event(EventTypes.AUDIT_STARTED, {"data": "test2"}, user_id="user2")
        logger.log_event(EventTypes.BIAS_DETECTED, {"data": "test3"}, user_id="user1")
        
        user1_events = logger.search_events(user_id="user1")
        assert len(user1_events) == 2
        
        user2_events = logger.search_events(user_id="user2")
        assert len(user2_events) == 1
    
    def test_search_events_by_session(self, logger):
        """Test searching events by session ID."""
        logger.log_event(EventTypes.AUDIT_STARTED, {"data": "test1"}, session_id="session1")
        logger.log_event(EventTypes.AUDIT_STARTED, {"data": "test2"}, session_id="session2")
        logger.log_event(EventTypes.BIAS_DETECTED, {"data": "test3"}, session_id="session1")
        
        session1_events = logger.search_events(session_id="session1")
        assert len(session1_events) == 2
        
        session2_events = logger.search_events(session_id="session2")
        assert len(session2_events) == 1
    
    def test_search_events_by_time_range(self, logger):
        """Test searching events by time range."""
        # Create events with specific timestamps
        base_time = datetime.datetime.now(datetime.timezone.utc)
        
        # Mock datetime.now to control timestamps
        with mock.patch('compliance_logging.datetime') as mock_datetime:
            mock_datetime.datetime.now.return_value = base_time
            mock_datetime.timezone = datetime.timezone
            event1_id = logger.log_event(EventTypes.AUDIT_STARTED, {"data": "test1"})
            
            mock_datetime.datetime.now.return_value = base_time + datetime.timedelta(hours=1)
            event2_id = logger.log_event(EventTypes.BIAS_DETECTED, {"data": "test2"})
            
            mock_datetime.datetime.now.return_value = base_time + datetime.timedelta(hours=2)
            event3_id = logger.log_event(EventTypes.AUDIT_COMPLETED, {"data": "test3"})
        
        # Search for events in the middle hour
        start_time = base_time + datetime.timedelta(minutes=30)
        end_time = base_time + datetime.timedelta(minutes=90)
        
        events = logger.search_events(start_time=start_time, end_time=end_time)
        assert len(events) == 1
        assert events[0].event_id == event2_id
    
    def test_generate_compliance_report(self, logger):
        """Test compliance report generation."""
        # Log several events
        logger.log_event(EventTypes.AUDIT_STARTED, {"data": "test1"}, user_id="user1")
        logger.log_event(EventTypes.BIAS_DETECTED, {"data": "test2"}, user_id="user1")
        logger.log_event(EventTypes.AUDIT_COMPLETED, {"data": "test3"}, user_id="user2")
        
        report = logger.generate_compliance_report()
        
        assert "report_period" in report
        assert "total_events" in report
        assert "event_types" in report
        assert "user_activity" in report
        assert "events" in report
        
        assert report["total_events"] == 3
        assert EventTypes.AUDIT_STARTED in report["event_types"]
        assert EventTypes.BIAS_DETECTED in report["event_types"]
        assert EventTypes.AUDIT_COMPLETED in report["event_types"]
        assert "user1" in report["user_activity"]
        assert "user2" in report["user_activity"]
    
    def test_export_events_json(self, logger, temp_db):
        """Test exporting events to JSON format."""
        # Log some events
        logger.log_event(EventTypes.AUDIT_STARTED, {"data": "test1"})
        logger.log_event(EventTypes.BIAS_DETECTED, {"data": "test2"})
        
        # Export to JSON
        export_path = temp_db + ".json"
        logger.export_events(export_path, format="json")
        
        # Verify the exported file
        assert os.path.exists(export_path)
        
        with open(export_path, 'r') as f:
            exported_data = json.load(f)
        
        assert len(exported_data) == 2
        assert exported_data[0]["event_type"] in [EventTypes.AUDIT_STARTED, EventTypes.BIAS_DETECTED]
        
        # Cleanup
        os.unlink(export_path)
    
    def test_context_manager(self, temp_db):
        """Test using the logger as a context manager."""
        with ComplianceLogger(db_path=temp_db) as logger:
            event_id = logger.log_event(EventTypes.AUDIT_STARTED, {"data": "test"})
            event = logger.get_event(event_id)
            assert event is not None
        
        # Logger should be closed after context manager exits
        # We can't directly test this without accessing private attributes
        # but the context manager should handle cleanup properly
    
    def test_search_limit(self, logger):
        """Test search result limiting."""
        # Log many events
        for i in range(20):
            logger.log_event(EventTypes.AUDIT_STARTED, {"iteration": i})
        
        # Search with limit
        events = logger.search_events(event_type=EventTypes.AUDIT_STARTED, limit=5)
        assert len(events) == 5
        
        # Events should be returned in reverse chronological order (most recent first)
        for i in range(4):
            assert events[i].timestamp >= events[i+1].timestamp


class TestEventTypes:
    """Test the EventTypes constant class."""
    
    def test_event_types_constants(self):
        """Test that all expected event type constants are defined."""
        expected_types = [
            "AUDIT_STARTED", "AUDIT_COMPLETED", "BIAS_DETECTED",
            "COMPLIANCE_VIOLATION", "MODEL_EVALUATION", "DATA_ACCESS",
            "CONFIGURATION_CHANGE", "ERROR_OCCURRED", "REVIEW_CONDUCTED",
            "APPROVAL_GRANTED", "APPROVAL_DENIED"
        ]
        
        for event_type in expected_types:
            assert hasattr(EventTypes, event_type)
            assert isinstance(getattr(EventTypes, event_type), str)


class TestIntegration:
    """Integration tests for the complete compliance logging system."""
    
    def test_audit_workflow(self):
        """Test a complete audit workflow using compliance logging."""
        with ComplianceLogger() as logger:
            session_id = "integration_test_session"
            user_id = "test_auditor"
            
            # Start audit
            audit_start_id = logger.log_event(
                EventTypes.AUDIT_STARTED,
                {
                    "audit_type": "bias_detection",
                    "target_system": "test_system",
                    "configuration": {"test_cases": 100}
                },
                user_id=user_id,
                session_id=session_id
            )
            
            # Log some findings
            bias_id = logger.log_event(
                EventTypes.BIAS_DETECTED,
                {
                    "bias_type": "demographic_parity",
                    "severity": "medium",
                    "confidence": 0.75
                },
                user_id=user_id,
                session_id=session_id
            )
            
            # Complete audit
            audit_complete_id = logger.log_event(
                EventTypes.AUDIT_COMPLETED,
                {
                    "status": "completed",
                    "findings_count": 1,
                    "recommendations": ["Retrain model"]
                },
                user_id=user_id,
                session_id=session_id
            )
            
            # Verify the complete workflow
            session_events = logger.search_events(session_id=session_id)
            assert len(session_events) == 3
            
            # Events should be in reverse chronological order
            event_types = [event.event_type for event in session_events]
            assert EventTypes.AUDIT_COMPLETED in event_types
            assert EventTypes.BIAS_DETECTED in event_types
            assert EventTypes.AUDIT_STARTED in event_types
            
            # Generate report for this session
            report = logger.generate_compliance_report()
            assert report["total_events"] == 3
            assert user_id in report["user_activity"]
            assert report["user_activity"][user_id] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])