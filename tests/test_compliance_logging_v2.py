"""
Comprehensive tests for the enhanced compliance logging module.

This test suite validates security, performance, and integration features
of the improved compliance logging system.
"""

import pytest
import tempfile
import os
import datetime
import json
import asyncio
import threading
import time
from unittest import mock
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from compliance_logging_v2 import (
    EnhancedComplianceLogger, ComplianceLogger, ComplianceEvent, 
    EventTypes, EventPayloads, SecurityManager, SQLiteBackend,
    AuditIntegrationMixin
)


class TestSecurityManager:
    """Test cases for the SecurityManager class."""
    
    def test_encryption_decryption(self):
        """Test data encryption and decryption."""
        security_manager = SecurityManager()
        test_data = "sensitive compliance data"
        
        encrypted = security_manager.encrypt_data(test_data)
        decrypted = security_manager.decrypt_data(encrypted)
        
        assert decrypted == test_data
        assert encrypted != test_data
    
    def test_integrity_verification(self):
        """Test HMAC integrity verification."""
        security_manager = SecurityManager()
        test_data = "important audit data"
        
        integrity_hash = security_manager.generate_integrity_hash(test_data)
        
        # Valid verification
        assert security_manager.verify_integrity(test_data, integrity_hash)
        
        # Invalid verification (tampered data)
        tampered_data = "tampered audit data"
        assert not security_manager.verify_integrity(tampered_data, integrity_hash)
    
    def test_custom_encryption_key(self):
        """Test using a custom encryption key."""
        from cryptography.fernet import Fernet
        custom_key = Fernet.generate_key()
        
        security_manager = SecurityManager(custom_key)
        test_data = "test data with custom key"
        
        encrypted = security_manager.encrypt_data(test_data)
        decrypted = security_manager.decrypt_data(encrypted)
        
        assert decrypted == test_data


class TestSQLiteBackend:
    """Test cases for the SQLite storage backend."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        os.unlink(path)
    
    @pytest.mark.asyncio
    async def test_backend_initialization(self, temp_db):
        """Test backend initialization."""
        backend = SQLiteBackend(temp_db)
        await backend.initialize()
        
        # Check that tables were created
        cursor = backend.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='compliance_events'"
        )
        tables = cursor.fetchall()
        assert len(tables) == 1
        
        await backend.close()
    
    @pytest.mark.asyncio
    async def test_store_and_retrieve_event(self, temp_db):
        """Test storing and retrieving events."""
        security_manager = SecurityManager()
        backend = SQLiteBackend(temp_db, security_manager)
        await backend.initialize()
        
        event_data = {
            "event_id": "test_event_001",
            "event_type": "test_event",
            "details": {"key": "value", "number": 42},
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "user_id": "test_user",
            "session_id": "test_session"
        }
        
        # Store event
        stored_id = await backend.store_event(event_data)
        assert stored_id == "test_event_001"
        
        # Search for event
        results = await backend.search_events(event_type="test_event")
        assert len(results) == 1
        
        retrieved_event = results[0]
        assert retrieved_event["event_id"] == "test_event_001"
        assert retrieved_event["details"]["key"] == "value"
        assert retrieved_event["details"]["number"] == 42
        
        await backend.close()
    
    @pytest.mark.asyncio
    async def test_search_filtering(self, temp_db):
        """Test event search with various filters."""
        backend = SQLiteBackend(temp_db)
        await backend.initialize()
        
        # Store multiple events
        base_time = datetime.datetime.now(datetime.timezone.utc)
        events = [
            {
                "event_id": f"event_{i}",
                "event_type": "audit_started" if i % 2 == 0 else "bias_detected",
                "details": {"test": i},
                "timestamp": (base_time + datetime.timedelta(minutes=i)).isoformat(),
                "user_id": f"user_{i % 3}",
                "session_id": f"session_{i % 2}"
            }
            for i in range(10)
        ]
        
        for event in events:
            await backend.store_event(event)
        
        # Test filtering by event type
        audit_events = await backend.search_events(event_type="audit_started")
        assert len(audit_events) == 5
        
        # Test filtering by user
        user_events = await backend.search_events(user_id="user_0")
        assert len(user_events) == 4  # users 0, 3, 6, 9
        
        # Test time range filtering
        mid_time = base_time + datetime.timedelta(minutes=5)
        recent_events = await backend.search_events(start_time=mid_time)
        assert len(recent_events) == 5  # events 5-9
        
        # Test limit
        limited_events = await backend.search_events(limit=3)
        assert len(limited_events) == 3
        
        await backend.close()


class TestEnhancedComplianceEvent:
    """Test cases for the enhanced ComplianceEvent class."""
    
    def test_event_creation_with_dict(self):
        """Test event creation with dictionary payload."""
        details = {"audit_type": "bias_detection", "target": "model_v1"}
        event = ComplianceEvent("audit_started", details, user_id="auditor_1")
        
        assert event.event_type == "audit_started"
        assert event.details == details
        assert event.user_id == "auditor_1"
        assert event.event_id is not None
        assert len(event.event_id) > 20  # Should be cryptographically secure
    
    def test_event_creation_with_pydantic(self):
        """Test event creation with pydantic model."""
        payload = EventPayloads.AuditStarted(
            audit_type="bias_detection",
            target_system="employment_model",
            auditor="ethics_team"
        )
        
        event = ComplianceEvent("audit_started", payload)
        
        assert event.event_type == "audit_started"
        assert event.details["audit_type"] == "bias_detection"
        assert event.details["target_system"] == "employment_model"
    
    def test_event_id_uniqueness(self):
        """Test that event IDs are unique."""
        details = {"test": "data"}
        events = [ComplianceEvent("test", details) for _ in range(100)]
        event_ids = [event.event_id for event in events]
        
        # All IDs should be unique
        assert len(set(event_ids)) == len(event_ids)


class TestEnhancedComplianceLogger:
    """Test cases for the EnhancedComplianceLogger class."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        os.unlink(path)
    
    @pytest.mark.asyncio
    async def test_async_logging(self, temp_db):
        """Test asynchronous event logging."""
        config = {"db_path": temp_db}
        encryption_key = "test_key_32_chars_long_12345678"
        
        async with EnhancedComplianceLogger(
            backend="sqlite", 
            backend_config=config,
            encryption_key=encryption_key
        ) as logger:
            
            # Log an event with pydantic model
            audit_payload = EventPayloads.AuditStarted(
                audit_type="bias_detection",
                target_system="hiring_algorithm"
            )
            
            event_id = await logger.log_event("audit_started", audit_payload, 
                                            user_id="auditor_1", session_id="session_1")
            
            assert event_id is not None
            
            # Search for the event
            events = await logger.search_events(event_type="audit_started")
            assert len(events) == 1
            assert events[0]["details"]["audit_type"] == "bias_detection"
    
    def test_sync_wrapper_compatibility(self, temp_db):
        """Test backwards compatibility with synchronous interface."""
        config = {"db_path": temp_db}
        
        with ComplianceLogger(backend="sqlite", backend_config=config) as logger:
            # Log event using synchronous interface
            event_id = logger.log_event(
                EventTypes.BIAS_DETECTED,
                {"bias_type": "demographic_parity", "severity": "high", "confidence": 0.87}
            )
            
            assert event_id is not None
            
            # Search using synchronous interface
            events = logger.search_events(event_type=EventTypes.BIAS_DETECTED)
            assert len(events) == 1
            assert events[0]["details"]["bias_type"] == "demographic_parity"
    
    @pytest.mark.asyncio
    async def test_multiple_backends(self):
        """Test using different storage backends."""
        # Test in-memory SQLite
        async with EnhancedComplianceLogger(backend="sqlite") as logger:
            event_id = await logger.log_event("test", {"data": "memory"})
            assert event_id is not None
            
            events = await logger.search_events()
            assert len(events) == 1


class TestConcurrency:
    """Test cases for concurrent access and thread safety."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        os.unlink(path)
    
    def test_concurrent_logging(self, temp_db):
        """Test concurrent logging from multiple threads."""
        config = {"db_path": temp_db}
        
        def log_events(thread_id: int, num_events: int):
            """Log events from a specific thread."""
            with ComplianceLogger(backend="sqlite", backend_config=config) as logger:
                for i in range(num_events):
                    logger.log_event(
                        "concurrent_test",
                        {"thread_id": thread_id, "event_num": i},
                        session_id=f"thread_{thread_id}"
                    )
        
        # Start multiple threads
        threads = []
        num_threads = 5
        events_per_thread = 10
        
        for thread_id in range(num_threads):
            thread = threading.Thread(
                target=log_events, 
                args=(thread_id, events_per_thread)
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all events were logged
        with ComplianceLogger(backend="sqlite", backend_config=config) as logger:
            events = logger.search_events(event_type="concurrent_test", limit=1000)
            
            assert len(events) == num_threads * events_per_thread
            
            # Check that events from all threads are present
            thread_ids = {event["details"]["thread_id"] for event in events}
            assert thread_ids == set(range(num_threads))


class TestAuditIntegration:
    """Test cases for integration with existing audit modules."""
    
    def test_integration_mixin(self):
        """Test the audit integration mixin."""
        class MockAuditClass(AuditIntegrationMixin):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.auditor_id = "test_auditor"
                self.session_id = "test_session"
            
            def run_audit(self):
                """Simulate running an audit with compliance logging."""
                self.log_audit_event("audit_started", {"test": "audit"})
                self.log_audit_event("audit_completed", {"result": "passed"})
        
        # Test with custom logger
        logger = ComplianceLogger()
        audit = MockAuditClass(compliance_logger=logger)
        audit.run_audit()
        
        # Verify events were logged
        events = logger.search_events()
        assert len(events) == 2
        assert events[0]["event_type"] in ["audit_started", "audit_completed"]


class TestEdgeCases:
    """Test cases for edge cases and error handling."""
    
    def test_timezone_handling(self):
        """Test handling of different timezones."""
        # Create events with different timezones
        utc_time = datetime.datetime.now(datetime.timezone.utc)
        est_tz = datetime.timezone(datetime.timedelta(hours=-5))
        est_time = datetime.datetime.now(est_tz)
        
        event1 = ComplianceEvent("test", {"tz": "utc"}, timestamp=utc_time)
        event2 = ComplianceEvent("test", {"tz": "est"}, timestamp=est_time)
        
        # Both should have timestamps
        assert event1.timestamp is not None
        assert event2.timestamp is not None
        
        # Serialization should preserve timezone info
        dict1 = event1.to_dict()
        dict2 = event2.to_dict()
        
        assert "Z" in dict1["timestamp"] or "+00:00" in dict1["timestamp"]
        assert "-05:00" in dict2["timestamp"]
    
    def test_large_payload_handling(self):
        """Test handling of large event payloads."""
        # Create a large payload
        large_payload = {
            f"key_{i}": f"value_{i}" * 100 
            for i in range(1000)
        }
        
        logger = ComplianceLogger()
        event_id = logger.log_event("large_payload_test", large_payload)
        
        assert event_id is not None
        
        # Verify the large payload can be retrieved
        events = logger.search_events(event_type="large_payload_test")
        assert len(events) == 1
        assert len(events[0]["details"]) == 1000
    
    def test_invalid_backend_type(self):
        """Test error handling for invalid backend types."""
        with pytest.raises(ValueError, match="Unsupported backend type"):
            ComplianceLogger(backend="invalid_backend")
    
    def test_encryption_without_key(self):
        """Test behavior when encryption is enabled without providing a key."""
        with mock.patch('compliance_logging_v2.logging') as mock_logging:
            logger = ComplianceLogger(encryption_key="auto-generate")
            
            # Should work but log a warning
            event_id = logger.log_event("test", {"data": "encrypted"})
            assert event_id is not None


class TestPydanticValidation:
    """Test cases for Pydantic schema validation."""
    
    def test_valid_audit_started_payload(self):
        """Test valid audit started payload validation."""
        payload = EventPayloads.AuditStarted(
            audit_type="bias_detection",
            target_system="employment_ai",
            auditor="ethics_team",
            methodology="correspondence_testing"
        )
        
        assert payload.audit_type == "bias_detection"
        assert payload.target_system == "employment_ai"
    
    def test_bias_detected_validation(self):
        """Test bias detected payload validation."""
        payload = EventPayloads.BiasDetected(
            bias_type="demographic_parity",
            severity="high",
            confidence=0.87,
            affected_groups=["gender", "race"],
            mitigation_recommended="Retrain with balanced dataset"
        )
        
        assert payload.confidence == 0.87
        assert "gender" in payload.affected_groups
    
    def test_invalid_confidence_score(self):
        """Test validation of invalid confidence scores."""
        with pytest.raises(ValueError):
            EventPayloads.BiasDetected(
                bias_type="test",
                severity="low",
                confidence=1.5  # Invalid: > 1.0
            )
    
    def test_model_evaluation_validation(self):
        """Test model evaluation payload validation."""
        payload = EventPayloads.ModelEvaluation(
            model_name="gemini-1.5-flash",
            test_cases=1000,
            accuracy=0.94,
            bias_score=0.12
        )
        
        assert payload.test_cases == 1000
        assert payload.accuracy == 0.94


class TestPerformance:
    """Test cases for performance characteristics."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        os.unlink(path)
    
    def test_bulk_logging_performance(self, temp_db):
        """Test performance of bulk event logging."""
        config = {"db_path": temp_db}
        
        with ComplianceLogger(backend="sqlite", backend_config=config) as logger:
            start_time = time.time()
            
            # Log 1000 events
            for i in range(1000):
                logger.log_event(
                    "performance_test",
                    {"event_number": i, "timestamp": time.time()}
                )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Should complete within reasonable time (adjust based on system)
            assert duration < 10.0  # 10 seconds for 1000 events
            
            # Verify all events were logged
            events = logger.search_events(event_type="performance_test", limit=2000)
            assert len(events) == 1000
    
    def test_search_performance_with_indices(self, temp_db):
        """Test search performance with database indices."""
        config = {"db_path": temp_db}
        
        with ComplianceLogger(backend="sqlite", backend_config=config) as logger:
            # Insert many events
            for i in range(5000):
                logger.log_event(
                    f"event_type_{i % 10}",
                    {"data": f"event_{i}"},
                    user_id=f"user_{i % 100}",
                    session_id=f"session_{i % 50}"
                )
            
            # Test search performance
            start_time = time.time()
            events = logger.search_events(event_type="event_type_5", limit=100)
            search_duration = time.time() - start_time
            
            # Should be fast due to indices
            assert search_duration < 1.0  # 1 second
            assert len(events) == 100  # Should respect limit