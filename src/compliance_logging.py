"""
Enhanced Compliance Logging Module for Oversight Integrity

This module provides enterprise-grade compliance logging functionality for
oversight integrity in AI auditing systems, addressing security, performance,
and integration concerns.

Key improvements:
- Pluggable storage backends (SQLite, PostgreSQL, etc.)
- Encryption at rest and integrity guarantees
- Pydantic models for schema validation
- Async API support
- Integration hooks for existing audit modules
- Enhanced security and performance

Example Usage:
    >>> from compliance_logging_v2 import ComplianceLogger, EventPayloads
    >>> logger = ComplianceLogger(backend="sqlite", encryption_key="your-key")
    >>> await logger.log_event("audit_started", EventPayloads.AuditStarted(
    ...     audit_type="bias_detection",
    ...     target_system="employment_ai"
    ... ))
"""

import json
import logging
import sqlite3
import datetime
import asyncio
import hmac
import hashlib
import secrets
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, Protocol
from pathlib import Path
import os
from dataclasses import dataclass
from cryptography.fernet import Fernet
import base64

# Use pydantic for schema validation
try:
    from pydantic import BaseModel, Field, validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    # Fallback for environments without pydantic
    PYDANTIC_AVAILABLE = False
    BaseModel = dict


class StorageBackend(ABC):
    """Abstract base class for compliance logging storage backends."""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the storage backend."""
        pass
    
    @abstractmethod
    async def store_event(self, event_data: Dict[str, Any]) -> str:
        """Store a compliance event and return its ID."""
        pass
    
    @abstractmethod
    async def search_events(self, **criteria) -> List[Dict[str, Any]]:
        """Search for events based on criteria."""
        pass
    
    @abstractmethod
    async def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific event by ID."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close the storage backend connection."""
        pass


class SecurityManager:
    """Handles encryption and integrity verification for compliance data."""
    
    def __init__(self, encryption_key: Optional[str] = None):
        if encryption_key:
            # Handle different key formats
            if isinstance(encryption_key, str):
                if len(encryption_key) == 44 and encryption_key.endswith('='):
                    # Looks like a base64-encoded key
                    self.fernet = Fernet(encryption_key.encode())
                elif len(encryption_key) >= 32:
                    # Use first 32 characters and base64 encode
                    key_bytes = encryption_key[:32].encode('utf-8')
                    import base64
                    b64_key = base64.urlsafe_b64encode(key_bytes)
                    self.fernet = Fernet(b64_key)
                else:
                    # Pad and encode
                    padded_key = (encryption_key + '0' * 32)[:32]
                    import base64
                    b64_key = base64.urlsafe_b64encode(padded_key.encode('utf-8'))
                    self.fernet = Fernet(b64_key)
            else:
                self.fernet = Fernet(encryption_key)
        else:
            # Generate a new key (for development only)
            key = Fernet.generate_key()
            self.fernet = Fernet(key)
            logging.warning("Generated new encryption key - not suitable for production")
        
        self.hmac_secret = secrets.token_bytes(32)
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive compliance data."""
        return self.fernet.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt compliance data."""
        return self.fernet.decrypt(encrypted_data.encode()).decode()
    
    def generate_integrity_hash(self, data: str) -> str:
        """Generate HMAC for data integrity verification."""
        return hmac.new(self.hmac_secret, data.encode(), hashlib.sha256).hexdigest()
    
    def verify_integrity(self, data: str, integrity_hash: str) -> bool:
        """Verify data integrity using HMAC."""
        expected_hash = self.generate_integrity_hash(data)
        return hmac.compare_digest(expected_hash, integrity_hash)


class SQLiteBackend(StorageBackend):
    """SQLite implementation of the storage backend."""
    
    def __init__(self, db_path: str = ":memory:", security_manager: Optional[SecurityManager] = None):
        self.db_path = db_path
        self.security_manager = security_manager
        self.conn = None
    
    async def initialize(self) -> None:
        """Initialize SQLite database with proper schema."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS compliance_events (
                event_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                encrypted_payload TEXT NOT NULL,
                integrity_hash TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                user_id TEXT,
                session_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                retention_until TIMESTAMP,
                legal_hold BOOLEAN DEFAULT FALSE
            )
        """)
        
        # Create indices for performance
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_event_type ON compliance_events(event_type)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON compliance_events(timestamp)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_session ON compliance_events(session_id)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_user ON compliance_events(user_id)")
        self.conn.commit()
    
    async def store_event(self, event_data: Dict[str, Any]) -> str:
        """Store an encrypted compliance event."""
        event_id = event_data["event_id"]
        payload_json = json.dumps(event_data["details"])
        
        if self.security_manager:
            encrypted_payload = self.security_manager.encrypt_data(payload_json)
            integrity_hash = self.security_manager.generate_integrity_hash(payload_json)
        else:
            encrypted_payload = payload_json
            integrity_hash = ""
        
        self.conn.execute("""
            INSERT INTO compliance_events 
            (event_id, event_type, encrypted_payload, integrity_hash, timestamp, user_id, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            event_data["event_type"],
            encrypted_payload,
            integrity_hash,
            event_data["timestamp"],
            event_data.get("user_id"),
            event_data.get("session_id")
        ))
        self.conn.commit()
        return event_id
    
    async def search_events(self, **criteria) -> List[Dict[str, Any]]:
        """Search events with filtering and pagination."""
        query = "SELECT * FROM compliance_events WHERE 1=1"
        params = []
        
        # Build dynamic query based on criteria
        for key, value in criteria.items():
            if key == "event_type" and value:
                query += " AND event_type = ?"
                params.append(value)
            elif key == "user_id" and value:
                query += " AND user_id = ?"
                params.append(value)
            elif key == "session_id" and value:
                query += " AND session_id = ?"
                params.append(value)
            elif key == "start_time" and value:
                query += " AND timestamp >= ?"
                params.append(value.isoformat() if hasattr(value, 'isoformat') else value)
            elif key == "end_time" and value:
                query += " AND timestamp <= ?"
                params.append(value.isoformat() if hasattr(value, 'isoformat') else value)
        
        # Add ordering and limit
        query += " ORDER BY timestamp DESC"
        if "limit" in criteria:
            query += " LIMIT ?"
            params.append(criteria["limit"])
        if "offset" in criteria:
            query += " OFFSET ?"
            params.append(criteria["offset"])
        
        cursor = self.conn.execute(query, params)
        events = []
        
        for row in cursor.fetchall():
            event_data = {
                "event_id": row[0],
                "event_type": row[1],
                "encrypted_payload": row[2],
                "integrity_hash": row[3],
                "timestamp": row[4],
                "user_id": row[5],
                "session_id": row[6],
                "created_at": row[7]
            }
            
            # Decrypt payload if security manager is available
            if self.security_manager and row[2]:
                try:
                    decrypted_payload = self.security_manager.decrypt_data(row[2])
                    if self.security_manager.verify_integrity(decrypted_payload, row[3]):
                        event_data["details"] = json.loads(decrypted_payload)
                    else:
                        logging.warning(f"Integrity check failed for event {row[0]}")
                        event_data["details"] = {"error": "integrity_check_failed"}
                except Exception as e:
                    logging.error(f"Failed to decrypt event {row[0]}: {e}")
                    event_data["details"] = {"error": "decryption_failed"}
            else:
                event_data["details"] = json.loads(row[2]) if row[2] else {}
            
            events.append(event_data)
        
        return events
    
    async def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific event by ID."""
        results = await self.search_events(event_id=event_id, limit=1)
        return results[0] if results else None
    
    async def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()


# Pydantic models for event payloads
if PYDANTIC_AVAILABLE:
    class BaseEventPayload(BaseModel):
        """Base class for all event payloads."""
        pass
    
    class AuditStartedPayload(BaseEventPayload):
        """Payload for audit started events."""
        audit_type: str = Field(..., description="Type of audit being performed")
        target_system: str = Field(..., description="System being audited")
        auditor: Optional[str] = Field(None, description="ID of the auditor")
        methodology: Optional[str] = Field(None, description="Audit methodology used")
    
    class BiasDetectedPayload(BaseEventPayload):
        """Payload for bias detected events."""
        bias_type: str = Field(..., description="Type of bias detected")
        severity: str = Field(..., description="Severity level (low, medium, high, critical)")
        confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
        affected_groups: List[str] = Field(default_factory=list, description="Affected demographic groups")
        mitigation_recommended: Optional[str] = Field(None, description="Recommended mitigation")
    
    class ModelEvaluationPayload(BaseEventPayload):
        """Payload for model evaluation events."""
        model_name: str = Field(..., description="Name of the model evaluated")
        test_cases: int = Field(..., ge=0, description="Number of test cases")
        accuracy: float = Field(..., ge=0.0, le=1.0, description="Model accuracy")
        bias_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Bias score")
        
    class EventPayloads:
        """Container for all event payload types."""
        AuditStarted = AuditStartedPayload
        BiasDetected = BiasDetectedPayload
        ModelEvaluation = ModelEvaluationPayload
else:
    # Fallback classes when pydantic is not available
    class EventPayloads:
        """Fallback event payloads when pydantic is not available."""
        AuditStarted = dict
        BiasDetected = dict
        ModelEvaluation = dict


class ComplianceEvent:
    """Enhanced compliance event with security and validation."""
    
    def __init__(self, event_type: str, details: Union[Dict[str, Any], BaseModel], 
                 timestamp: Optional[datetime.datetime] = None,
                 user_id: Optional[str] = None, session_id: Optional[str] = None):
        self.event_type = event_type
        
        # Convert pydantic models to dict
        if PYDANTIC_AVAILABLE and isinstance(details, BaseModel):
            self.details = details.model_dump()
        else:
            self.details = details
            
        self.timestamp = timestamp or datetime.datetime.now(datetime.timezone.utc)
        self.user_id = user_id or "system"
        self.session_id = session_id
        self.event_id = self._generate_event_id()
    
    def _generate_event_id(self) -> str:
        """Generate a cryptographically secure event ID."""
        # Use timestamp + random component for uniqueness
        timestamp_part = self.timestamp.strftime('%Y%m%d_%H%M%S_%f')
        random_part = secrets.token_hex(8)
        return f"{timestamp_part}_{random_part}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "session_id": self.session_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComplianceEvent":
        """Create event from dictionary (backwards compatibility)."""
        event = cls(
            event_type=data["event_type"],
            details=data["details"],
            timestamp=datetime.datetime.fromisoformat(data["timestamp"]),
            user_id=data.get("user_id"),
            session_id=data.get("session_id")
        )
        event.event_id = data["event_id"]
        return event


class EnhancedComplianceLogger:
    """
    Enterprise-grade compliance logger with security and performance improvements.
    
    Features:
    - Pluggable storage backends
    - Encryption at rest
    - Integrity verification
    - Async API support
    - Schema validation
    - Integration hooks
    """
    
    def __init__(self, backend: str = "sqlite", 
                 backend_config: Optional[Dict[str, Any]] = None,
                 encryption_key: Optional[str] = None,
                 log_level: str = "INFO"):
        """
        Initialize enhanced compliance logger.
        
        Args:
            backend: Storage backend type ("sqlite", "postgresql", etc.)
            backend_config: Configuration for the storage backend
            encryption_key: Encryption key for data at rest
            log_level: Logging level
        """
        self.backend_type = backend
        self.backend_config = backend_config or {}
        
        # Initialize security manager
        self.security_manager = SecurityManager(encryption_key) if encryption_key else None
        
        # Initialize storage backend
        self.backend = self._create_backend()
        
        # Initialize Python logging
        self._init_logging(log_level)
        
        # Track initialization
        self._initialized = False
    
    def _create_backend(self) -> StorageBackend:
        """Factory method to create storage backend."""
        if self.backend_type == "sqlite":
            db_path = self.backend_config.get("db_path", ":memory:")
            return SQLiteBackend(db_path, self.security_manager)
        else:
            raise ValueError(f"Unsupported backend type: {self.backend_type}")
    
    def _init_logging(self, log_level: str):
        """Initialize Python logging."""
        self.logger = logging.getLogger("enhanced_compliance_logger")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    async def initialize(self):
        """Initialize the logger (async)."""
        if not self._initialized:
            await self.backend.initialize()
            self._initialized = True
    
    async def log_event(self, event_type: str, details: Union[Dict[str, Any], BaseModel], 
                       user_id: Optional[str] = None, session_id: Optional[str] = None) -> str:
        """
        Log a compliance event asynchronously.
        
        Args:
            event_type: Type of compliance event
            details: Event details (dict or pydantic model)
            user_id: Optional user identifier
            session_id: Optional session identifier
            
        Returns:
            str: The unique event ID
        """
        if not self._initialized:
            await self.initialize()
        
        event = ComplianceEvent(event_type, details, user_id=user_id, session_id=session_id)
        event_id = await self.backend.store_event(event.to_dict())
        
        # Log to Python logging system
        self.logger.info(f"Compliance event logged: {event_type} - {event_id}")
        
        return event_id
    
    # Synchronous wrapper for backwards compatibility
    def log_event_sync(self, event_type: str, details: Union[Dict[str, Any], BaseModel], 
                      user_id: Optional[str] = None, session_id: Optional[str] = None) -> str:
        """Synchronous wrapper for log_event."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.log_event(event_type, details, user_id, session_id))
        finally:
            loop.close()
    
    async def search_events(self, **criteria) -> List[Dict[str, Any]]:
        """Search for compliance events asynchronously."""
        if not self._initialized:
            await self.initialize()
        return await self.backend.search_events(**criteria)
    
    async def close(self):
        """Close the logger and backend connections."""
        if hasattr(self.backend, 'close'):
            await self.backend.close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Event types constants
class EventTypes:
    """Standard compliance event types for AI auditing systems."""
    
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


# For backwards compatibility, create a synchronous wrapper
class ComplianceLogger(EnhancedComplianceLogger):
    """Backwards-compatible synchronous wrapper for EnhancedComplianceLogger."""
    
    def __init__(self, db_path: Optional[str] = None, log_level: str = "INFO", **kwargs):
        # Handle old-style db_path parameter
        if db_path is not None:
            backend_config = kwargs.get("backend_config", {})
            backend_config["db_path"] = db_path
            kwargs["backend_config"] = backend_config
        
        super().__init__(**kwargs)
        # Initialize synchronously for backwards compatibility
        asyncio.run(self.initialize())
        
        # Store db_path for backwards compatibility
        self.db_path = kwargs.get("backend_config", {}).get("db_path", ":memory:")
    
    def log_event(self, event_type: str, details: Union[Dict[str, Any], BaseModel], 
                  user_id: Optional[str] = None, session_id: Optional[str] = None) -> str:
        """Log event synchronously."""
        return asyncio.run(super().log_event(event_type, details, user_id, session_id))
    
    def search_events(self, **criteria) -> List[ComplianceEvent]:
        """Search events synchronously and return ComplianceEvent objects."""
        raw_events = asyncio.run(super().search_events(**criteria))
        # Convert dict results back to ComplianceEvent objects for backwards compatibility
        events = []
        for event_data in raw_events:
            event = ComplianceEvent(
                event_type=event_data["event_type"],
                details=event_data["details"],
                timestamp=datetime.datetime.fromisoformat(event_data["timestamp"]),
                user_id=event_data.get("user_id"),
                session_id=event_data.get("session_id")
            )
            event.event_id = event_data["event_id"]
            events.append(event)
        return events
    
    def get_event(self, event_id: str) -> Optional[ComplianceEvent]:
        """Get a specific event by ID (backwards compatibility)."""
        events = self.search_events(limit=1000)  # Search all events
        for event in events:
            if event.event_id == event_id:
                return event
        return None
    
    def generate_compliance_report(self, start_time: Optional[datetime.datetime] = None,
                                 end_time: Optional[datetime.datetime] = None) -> Dict[str, Any]:
        """Generate a compliance report (backwards compatibility)."""
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
        """Export compliance events to a file (backwards compatibility)."""
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
        """Close synchronously."""
        asyncio.run(super().close())
    
    def __enter__(self):
        """Synchronous context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Synchronous context manager exit."""
        self.close()


# Integration hooks for existing audit modules
class AuditIntegrationMixin:
    """Mixin to add compliance logging to existing audit classes."""
    
    def __init__(self, *args, compliance_logger: Optional[ComplianceLogger] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.compliance_logger = compliance_logger or ComplianceLogger()
    
    def log_audit_event(self, event_type: str, details: Dict[str, Any], 
                       session_id: Optional[str] = None):
        """Helper method to log audit events."""
        if self.compliance_logger:
            return self.compliance_logger.log_event(
                event_type, details, 
                user_id=getattr(self, 'auditor_id', None),
                session_id=session_id or getattr(self, 'session_id', None)
            )
        return None