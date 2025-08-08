"""
Compliance Logging Module for Oversight Integrity

This module provides enterprise-style compliance logging functionality for
oversight integrity in AI auditing systems. It simulates compliance logging,
review, and search features commonly found in enterprise environments.

Features:
- Structured logging of compliance events
- Review and audit trail functionality
- Search and filtering capabilities
- Integration with existing auditing frameworks

Example Usage:
    >>> from compliance_logging import ComplianceLogger
    >>> logger = ComplianceLogger()
    >>> logger.log_event("audit_started", {"audit_type": "bias_detection"})
    >>> events = logger.search_events(event_type="audit_started")
"""

import json
import logging
import sqlite3
import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import os


class ComplianceEvent:
    """Represents a single compliance event with metadata."""
    
    def __init__(self, event_type: str, details: Dict[str, Any], 
                 timestamp: Optional[datetime.datetime] = None,
                 user_id: Optional[str] = None, session_id: Optional[str] = None):
        self.event_type = event_type
        self.details = details
        self.timestamp = timestamp or datetime.datetime.now(datetime.timezone.utc)
        self.user_id = user_id or "system"
        self.session_id = session_id
        self.event_id = self._generate_event_id()
    
    def _generate_event_id(self) -> str:
        """Generate a unique event ID."""
        return f"{self.timestamp.strftime('%Y%m%d_%H%M%S')}_{hash(str(self.details)) % 10000:04d}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "session_id": self.session_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComplianceEvent':
        """Create event from dictionary."""
        event = cls(
            event_type=data["event_type"],
            details=data["details"],
            timestamp=datetime.datetime.fromisoformat(data["timestamp"]),
            user_id=data.get("user_id"),
            session_id=data.get("session_id")
        )
        event.event_id = data["event_id"]
        return event


class ComplianceLogger:
    """
    Enterprise-style compliance logger for oversight integrity.
    
    Provides logging, review, and search capabilities for compliance events
    in AI auditing systems.
    """
    
    def __init__(self, db_path: Optional[str] = None, log_level: str = "INFO"):
        """
        Initialize the compliance logger.
        
        Args:
            db_path: Path to SQLite database file. If None, uses in-memory database.
            log_level: Logging level for standard Python logging
        """
        self.db_path = db_path or ":memory:"
        self._init_database()
        self._init_logging(log_level)
        
    def _init_database(self):
        """Initialize SQLite database for event storage."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS compliance_events (
                event_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                details TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                user_id TEXT,
                session_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_event_type ON compliance_events(event_type)
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON compliance_events(timestamp)
        """)
        self.conn.commit()
    
    def _init_logging(self, log_level: str):
        """Initialize Python logging for the compliance logger."""
        self.logger = logging.getLogger("compliance_logger")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Only add handler if none exists to avoid duplicates
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_event(self, event_type: str, details: Dict[str, Any], 
                  user_id: Optional[str] = None, session_id: Optional[str] = None) -> str:
        """
        Log a compliance event.
        
        Args:
            event_type: Type of compliance event (e.g., "audit_started", "bias_detected")
            details: Dictionary containing event details
            user_id: Optional user identifier
            session_id: Optional session identifier
            
        Returns:
            str: The unique event ID
        """
        event = ComplianceEvent(event_type, details, user_id=user_id, session_id=session_id)
        
        # Store in database
        self.conn.execute("""
            INSERT INTO compliance_events 
            (event_id, event_type, details, timestamp, user_id, session_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            event.event_id,
            event.event_type,
            json.dumps(event.details),
            event.timestamp.isoformat(),
            event.user_id,
            event.session_id
        ))
        self.conn.commit()
        
        # Also log to Python logging system
        self.logger.info(f"Compliance event logged: {event_type} - {event.event_id}")
        
        return event.event_id
    
    def search_events(self, event_type: Optional[str] = None,
                     user_id: Optional[str] = None,
                     session_id: Optional[str] = None,
                     start_time: Optional[datetime.datetime] = None,
                     end_time: Optional[datetime.datetime] = None,
                     limit: int = 100) -> List[ComplianceEvent]:
        """
        Search for compliance events based on criteria.
        
        Args:
            event_type: Filter by event type
            user_id: Filter by user ID
            session_id: Filter by session ID
            start_time: Filter events after this time
            end_time: Filter events before this time
            limit: Maximum number of events to return
            
        Returns:
            List of ComplianceEvent objects matching the criteria
        """
        query = "SELECT * FROM compliance_events WHERE 1=1"
        params = []
        
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
            
        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)
            
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())
            
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor = self.conn.execute(query, params)
        events = []
        
        for row in cursor.fetchall():
            event_data = {
                "event_id": row[0],
                "event_type": row[1],
                "details": json.loads(row[2]),
                "timestamp": row[3],
                "user_id": row[4],
                "session_id": row[5]
            }
            events.append(ComplianceEvent.from_dict(event_data))
        
        return events
    
    def get_event(self, event_id: str) -> Optional[ComplianceEvent]:
        """
        Retrieve a specific event by ID.
        
        Args:
            event_id: Unique event identifier
            
        Returns:
            ComplianceEvent if found, None otherwise
        """
        cursor = self.conn.execute(
            "SELECT * FROM compliance_events WHERE event_id = ?", 
            (event_id,)
        )
        row = cursor.fetchone()
        
        if row:
            event_data = {
                "event_id": row[0],
                "event_type": row[1],
                "details": json.loads(row[2]),
                "timestamp": row[3],
                "user_id": row[4],
                "session_id": row[5]
            }
            return ComplianceEvent.from_dict(event_data)
        
        return None
    
    def generate_compliance_report(self, start_time: Optional[datetime.datetime] = None,
                                 end_time: Optional[datetime.datetime] = None) -> Dict[str, Any]:
        """
        Generate a compliance report for the specified time period.
        
        Args:
            start_time: Report start time (defaults to 24 hours ago)
            end_time: Report end time (defaults to now)
            
        Returns:
            Dictionary containing compliance report data
        """
        if not end_time:
            end_time = datetime.datetime.now(datetime.timezone.utc)
        if not start_time:
            start_time = end_time - datetime.timedelta(days=1)
        
        events = self.search_events(start_time=start_time, end_time=end_time, limit=10000)
        
        # Count events by type
        event_counts = {}
        for event in events:
            event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1
        
        # Count events by user
        user_counts = {}
        for event in events:
            user_counts[event.user_id] = user_counts.get(event.user_id, 0) + 1
        
        return {
            "report_period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "total_events": len(events),
            "event_types": event_counts,
            "user_activity": user_counts,
            "events": [event.to_dict() for event in events]
        }
    
    def export_events(self, file_path: str, format: str = "json",
                     start_time: Optional[datetime.datetime] = None,
                     end_time: Optional[datetime.datetime] = None):
        """
        Export compliance events to a file.
        
        Args:
            file_path: Path to output file
            format: Export format ("json" or "csv")
            start_time: Export events after this time
            end_time: Export events before this time
        """
        events = self.search_events(start_time=start_time, end_time=end_time, limit=10000)
        
        if format.lower() == "json":
            with open(file_path, 'w') as f:
                json.dump([event.to_dict() for event in events], f, indent=2)
        elif format.lower() == "csv":
            import csv
            with open(file_path, 'w', newline='') as f:
                if events:
                    writer = csv.DictWriter(f, fieldnames=events[0].to_dict().keys())
                    writer.writeheader()
                    for event in events:
                        writer.writerow(event.to_dict())
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def close(self):
        """Close the database connection."""
        if hasattr(self, 'conn'):
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Predefined event types for common compliance scenarios
class EventTypes:
    """Common compliance event types for AI auditing systems."""
    
    AUDIT_STARTED = "audit_started"
    AUDIT_COMPLETED = "audit_completed"
    BIAS_DETECTED = "bias_detected"
    COMPLIANCE_VIOLATION = "compliance_violation"
    MODEL_EVALUATION = "model_evaluation"
    DATA_ACCESS = "data_access"
    CONFIGURATION_CHANGE = "configuration_change"
    ERROR_OCCURRED = "error_occurred"
    REVIEW_CONDUCTED = "review_conducted"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_DENIED = "approval_denied"


def demo_compliance_logging():
    """
    Demonstration of compliance logging functionality.
    
    This function shows how to use the ComplianceLogger for typical
    oversight scenarios in AI auditing systems.
    """
    print("=== Compliance Logging Demo ===\n")
    
    # Initialize logger
    with ComplianceLogger() as logger:
        # Log various compliance events
        session_id = "demo_session_001"
        
        # 1. Audit started
        audit_id = logger.log_event(
            EventTypes.AUDIT_STARTED,
            {
                "audit_type": "bias_detection",
                "target_system": "employment_decision_tool",
                "auditor": "ai_ethics_team"
            },
            user_id="auditor_001",
            session_id=session_id
        )
        print(f"Logged audit start: {audit_id}")
        
        # 2. Model evaluation
        eval_id = logger.log_event(
            EventTypes.MODEL_EVALUATION,
            {
                "model_name": "gemini-1.5-flash",
                "test_cases": 100,
                "accuracy": 0.92,
                "bias_score": 0.15
            },
            user_id="auditor_001",
            session_id=session_id
        )
        print(f"Logged model evaluation: {eval_id}")
        
        # 3. Bias detected
        bias_id = logger.log_event(
            EventTypes.BIAS_DETECTED,
            {
                "bias_type": "demographic_parity",
                "affected_groups": ["gender", "ethnicity"],
                "severity": "high",
                "confidence": 0.87
            },
            user_id="auditor_001",
            session_id=session_id
        )
        print(f"Logged bias detection: {bias_id}")
        
        # 4. Review conducted
        review_id = logger.log_event(
            EventTypes.REVIEW_CONDUCTED,
            {
                "reviewer": "senior_auditor_002",
                "findings_confirmed": True,
                "recommendations": [
                    "Retrain model with balanced dataset",
                    "Implement fairness constraints"
                ]
            },
            user_id="senior_auditor_002",
            session_id=session_id
        )
        print(f"Logged review: {review_id}")
        
        # 5. Audit completed
        complete_id = logger.log_event(
            EventTypes.AUDIT_COMPLETED,
            {
                "status": "completed",
                "findings": "bias_detected",
                "action_required": True,
                "report_generated": True
            },
            user_id="auditor_001",
            session_id=session_id
        )
        print(f"Logged audit completion: {complete_id}")
        
        print("\n=== Search and Review Examples ===\n")
        
        # Search for bias detection events
        bias_events = logger.search_events(event_type=EventTypes.BIAS_DETECTED)
        print(f"Found {len(bias_events)} bias detection events")
        
        # Search for events by user
        user_events = logger.search_events(user_id="auditor_001")
        print(f"Found {len(user_events)} events by auditor_001")
        
        # Search for events in session
        session_events = logger.search_events(session_id=session_id)
        print(f"Found {len(session_events)} events in session {session_id}")
        
        # Generate compliance report
        report = logger.generate_compliance_report()
        print(f"\nCompliance Report Summary:")
        print(f"Total events: {report['total_events']}")
        print(f"Event types: {list(report['event_types'].keys())}")
        print(f"Users active: {list(report['user_activity'].keys())}")
        
        # Retrieve specific event
        specific_event = logger.get_event(bias_id)
        if specific_event:
            print(f"\nDetailed bias event:")
            print(f"Type: {specific_event.event_type}")
            print(f"Timestamp: {specific_event.timestamp}")
            print(f"Details: {specific_event.details}")
        
        print("\n=== Demo completed successfully ===")


if __name__ == "__main__":
    demo_compliance_logging()