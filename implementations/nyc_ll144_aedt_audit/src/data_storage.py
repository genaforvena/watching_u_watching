#!/usr/bin/env python3
"""
Data Storage for NYC Local Law 144 Audits.

This module handles the storage of audit data for NYC Local Law 144 compliance.
"""

import json
import logging
import os
import shutil
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

# Configure logging
logger = logging.getLogger(__name__)


class DataStorage:
    """Handles the storage of audit data."""
    
    def __init__(
        self,
        db_path: str,
        backup_enabled: bool = True,
        backup_interval: int = 24,
        retention_days: int = 90
    ):
        """Initialize the data storage.
        
        Args:
            db_path: Path to the SQLite database
            backup_enabled: Whether to enable automatic backups
            backup_interval: Interval between backups in hours
            retention_days: Number of days to retain data
        """
        self.db_path = db_path
        self.backup_enabled = backup_enabled
        self.backup_interval = backup_interval
        self.retention_days = retention_days
        
        # Create database directory if it doesn't exist
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        # Initialize database
        self._init_db()
        
        # Schedule cleanup
        self._schedule_cleanup()
        
        logger.info(f"Initialized DataStorage with database at {db_path}")
    
    def _init_db(self):
        """Initialize the database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS probes (
            id TEXT PRIMARY KEY,
            job_type TEXT,
            template_type TEXT,
            variation TEXT,
            content TEXT,
            pair_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id TEXT PRIMARY KEY,
            probe_id TEXT,
            status TEXT,
            timestamp TIMESTAMP,
            metadata TEXT,
            FOREIGN KEY (probe_id) REFERENCES probes (id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id TEXT PRIMARY KEY,
            submission_id TEXT,
            response_type TEXT,
            selected INTEGER,
            timestamp TIMESTAMP,
            content TEXT,
            metadata TEXT,
            FOREIGN KEY (submission_id) REFERENCES submissions (id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            id TEXT PRIMARY KEY,
            timestamp TIMESTAMP,
            metrics TEXT,
            report TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def _schedule_cleanup(self):
        """Schedule data cleanup based on retention policy."""
        # This is a placeholder for a more sophisticated scheduling system
        # In a real implementation, this would use a proper scheduler
        
        # For now, just run cleanup once
        self._cleanup_old_data()
    
    def _cleanup_old_data(self):
        """Clean up data older than the retention period."""
        if self.retention_days <= 0:
            logger.info("Data retention disabled, skipping cleanup")
            return
            
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d %H:%M:%S")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete old data
        cursor.execute(f"DELETE FROM responses WHERE timestamp < '{cutoff_str}'")
        cursor.execute(f"DELETE FROM submissions WHERE timestamp < '{cutoff_str}'")
        cursor.execute(f"DELETE FROM probes WHERE created_at < '{cutoff_str}'")
        cursor.execute(f"DELETE FROM analysis_results WHERE timestamp < '{cutoff_str}'")
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        logger.info(f"Cleaned up {deleted_count} records older than {cutoff_str}")
    
    def _backup_db(self):
        """Create a backup of the database."""
        if not self.backup_enabled:
            return
            
        backup_dir = os.path.join(os.path.dirname(self.db_path), "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"aedt_audit_{timestamp}.db")
        
        shutil.copy2(self.db_path, backup_path)
        logger.info(f"Created database backup at {backup_path}")
        
        # Clean up old backups
        self._cleanup_old_backups(backup_dir)
    
    def _cleanup_old_backups(self, backup_dir: str):
        """Clean up old database backups.
        
        Args:
            backup_dir: Directory containing backups
        """
        if not os.path.exists(backup_dir):
            return
            
        # Keep only the 5 most recent backups
        backups = sorted(
            [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) if f.endswith(".db")],
            key=os.path.getmtime,
            reverse=True
        )
        
        for backup in backups[5:]:
            os.remove(backup)
            logger.info(f"Removed old backup: {backup}")
    
    def store_probe(self, probe: Dict) -> bool:
        """Store a probe in the database.
        
        Args:
            probe: Probe dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO probes (id, job_type, template_type, variation, content, pair_id) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    probe["id"],
                    probe["job_type"],
                    probe["template_type"],
                    probe["variation"],
                    json.dumps(probe["content"]),
                    probe["pair_id"]
                )
            )
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            logger.error(f"Error storing probe: {e}")
            return False
    
    def store_submission(self, probe: Dict, submission_result: Dict) -> bool:
        """Store a submission in the database.
        
        Args:
            probe: Probe dictionary
            submission_result: Submission result dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # First store the probe
            self.store_probe(probe)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO submissions (id, probe_id, status, timestamp, metadata) VALUES (?, ?, ?, ?, ?)",
                (
                    submission_result["id"],
                    probe["id"],
                    submission_result["status"],
                    submission_result["timestamp"],
                    json.dumps(submission_result.get("metadata", {}))
                )
            )
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            logger.error(f"Error storing submission: {e}")
            return False
    
    def store_response(self, response: Dict) -> bool:
        """Store a response in the database.
        
        Args:
            response: Response dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO responses (id, submission_id, response_type, selected, timestamp, content, metadata) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    response["id"],
                    response["submission_id"],
                    response["response_type"],
                    1 if response.get("selected", False) else 0,
                    response["timestamp"],
                    response.get("content", ""),
                    json.dumps(response.get("metadata", {}))
                )
            )
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            logger.error(f"Error storing response: {e}")
            return False
    
    def store_analysis_results(self, analysis_results: Dict) -> bool:
        """Store analysis results in the database.
        
        Args:
            analysis_results: Analysis results dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO analysis_results (id, timestamp, metrics, report) VALUES (?, ?, ?, ?)",
                (
                    analysis_results.get("id", str(time.time())),
                    analysis_results.get("timestamp", datetime.now().isoformat()),
                    json.dumps(analysis_results.get("metrics", {})),
                    json.dumps(analysis_results.get("report", {}))
                )
            )
            
            conn.commit()
            conn.close()
            
            # Create a backup after storing analysis results
            self._backup_db()
            
            return True
        except Exception as e:
            logger.error(f"Error storing analysis results: {e}")
            return False
    
    def get_probes(self, filters: Dict = None) -> List[Dict]:
        """Get probes from the database.
        
        Args:
            filters: Filters to apply
            
        Returns:
            List of probe dictionaries
        """
        filters = filters or {}
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM probes"
            params = []
            
            # Apply filters
            if filters:
                conditions = []
                for key, value in filters.items():
                    conditions.append(f"{key} = ?")
                    params.append(value)
                
                query += " WHERE " + " AND ".join(conditions)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            probes = []
            for row in rows:
                probe = dict(row)
                probe["content"] = json.loads(probe["content"])
                probes.append(probe)
            
            conn.close()
            
            return probes
        except Exception as e:
            logger.error(f"Error getting probes: {e}")
            return []
    
    def get_responses(self, filters: Dict = None) -> List[Dict]:
        """Get responses from the database.
        
        Args:
            filters: Filters to apply
            
        Returns:
            List of response dictionaries
        """
        filters = filters or {}
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = """
            SELECT r.*, s.probe_id, p.variation, p.content
            FROM responses r
            JOIN submissions s ON r.submission_id = s.id
            JOIN probes p ON s.probe_id = p.id
            """
            
            params = []
            
            # Apply filters
            if filters:
                conditions = []
                for key, value in filters.items():
                    if key.startswith("r."):
                        conditions.append(f"{key} = ?")
                    elif key.startswith("s."):
                        conditions.append(f"{key} = ?")
                    elif key.startswith("p."):
                        conditions.append(f"{key} = ?")
                    else:
                        conditions.append(f"r.{key} = ?")
                    params.append(value)
                
                query += " WHERE " + " AND ".join(conditions)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            responses = []
            for row in rows:
                response = dict(row)
                response["selected"] = bool(response["selected"])
                response["metadata"] = json.loads(response["metadata"])
                response["probe"] = {
                    "id": response["probe_id"],
                    "variation": response["variation"],
                    "content": json.loads(response["content"])
                }
                responses.append(response)
            
            conn.close()
            
            return responses
        except Exception as e:
            logger.error(f"Error getting responses: {e}")
            return []
    
    def get_analysis_results(self, limit: int = 1) -> List[Dict]:
        """Get analysis results from the database.
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of analysis results dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM analysis_results ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                result = dict(row)
                result["metrics"] = json.loads(result["metrics"])
                result["report"] = json.loads(result["report"])
                results.append(result)
            
            conn.close()
            
            return results
        except Exception as e:
            logger.error(f"Error getting analysis results: {e}")
            return []


if __name__ == "__main__":
    # Simple demonstration
    logging.basicConfig(level=logging.INFO)
    
    storage = DataStorage(
        db_path="data/aedt_audit_demo.db",
        backup_enabled=True,
        backup_interval=24,
        retention_days=90
    )
    
    # Example probe
    probe = {
        "id": "probe-123",
        "job_type": "software_engineer",
        "template_type": "application",
        "variation": "race_white",
        "content": {
            "personal_info": {
                "first_name": "John",
                "last_name": "Smith",
                "race_ethnicity": "white"
            }
        },
        "pair_id": "pair-456"
    }
    
    # Example submission
    submission = {
        "id": "submission-789",
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "metadata": {"url": "https://example.com/apply"}
    }
    
    # Example response
    response = {
        "id": "response-101112",
        "submission_id": "submission-789",
        "response_type": "interview",
        "selected": True,
        "timestamp": datetime.now().isoformat(),
        "content": "We would like to invite you for an interview.",
        "metadata": {"response_time_seconds": 3600}
    }
    
    # Store data
    storage.store_submission(probe, submission)
    storage.store_response(response)
    
    # Retrieve data
    probes = storage.get_probes()
    responses = storage.get_responses()
    
    print(f"Stored {len(probes)} probes and {len(responses)} responses")