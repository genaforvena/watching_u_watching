"""
Data Storage System for Berlin Housing Bias Testing

This module handles storage of property data, applications, submissions,
and responses for analysis while maintaining strict PII protection.
"""

import json
import os
import sqlite3
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import hashlib
from pathlib import Path

from .pii_redactor import PIIRedactor


class DataStorage:
    """
    Handles data storage for the housing bias testing system.
    """
    
    def __init__(self, config: Dict, pii_redactor: PIIRedactor):
        """
        Initialize the data storage system.
        
        Args:
            config: Configuration dictionary
            pii_redactor: PII redaction system instance
        """
        self.config = config
        self.storage_config = config.get('data_storage', {})
        self.pii_redactor = pii_redactor
        
        self.output_dir = Path(self.storage_config.get('output_directory', 'data'))
        self.output_dir.mkdir(exist_ok=True)
        
        self.backup_enabled = self.storage_config.get('backup_enabled', True)
        self.retention_days = self.storage_config.get('retention_days', 90)
        
        # Initialize database
        self.db_path = self.output_dir / 'housing_bias_test.db'
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Properties table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS properties (
                    id TEXT PRIMARY KEY,
                    url TEXT UNIQUE,
                    title TEXT,
                    description TEXT,
                    price TEXT,
                    location TEXT,
                    rooms TEXT,
                    area TEXT,
                    discovered_at TEXT,
                    source TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Applications table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS applications (
                    id TEXT PRIMARY KEY,
                    property_id TEXT,
                    persona TEXT,
                    applicant_name TEXT,
                    applicant_email TEXT,
                    subject TEXT,
                    body TEXT,
                    generated_at TEXT,
                    template_used TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (property_id) REFERENCES properties (id)
                )
            ''')
            
            # Submissions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS submissions (
                    id TEXT PRIMARY KEY,
                    application_id TEXT,
                    property_id TEXT,
                    persona TEXT,
                    success BOOLEAN,
                    error_message TEXT,
                    submitted_at TEXT,
                    dry_run BOOLEAN,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (application_id) REFERENCES applications (id),
                    FOREIGN KEY (property_id) REFERENCES properties (id)
                )
            ''')
            
            # Responses table (all PII redacted)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS responses (
                    id TEXT PRIMARY KEY,
                    submission_id TEXT,
                    application_id TEXT,
                    property_id TEXT,
                    persona TEXT,
                    redacted_subject TEXT,
                    redacted_sender_name TEXT,
                    redacted_sender_email TEXT,
                    redacted_body TEXT,
                    original_timestamp TEXT,
                    response_received_at TEXT,
                    response_type TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (submission_id) REFERENCES submissions (id),
                    FOREIGN KEY (application_id) REFERENCES applications (id),
                    FOREIGN KEY (property_id) REFERENCES properties (id)
                )
            ''')
            
            # Analysis results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id TEXT PRIMARY KEY,
                    analysis_type TEXT,
                    property_id TEXT,
                    mohammed_response_count INTEGER DEFAULT 0,
                    franz_response_count INTEGER DEFAULT 0,
                    response_time_difference_hours REAL,
                    response_sentiment_difference REAL,
                    bias_indicator_score REAL,
                    analysis_notes TEXT,
                    analyzed_at TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            logging.info("Database initialized successfully")
    
    def store_property(self, property_data: Dict) -> bool:
        """
        Store property data.
        
        Args:
            property_data: Property information dictionary
            
        Returns:
            True if stored successfully
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO properties 
                    (id, url, title, description, price, location, rooms, area, discovered_at, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    property_data.get('id'),
                    property_data.get('url'),
                    property_data.get('title'),
                    property_data.get('description'),
                    property_data.get('price'),
                    property_data.get('location'),
                    property_data.get('rooms'),
                    property_data.get('area'),
                    property_data.get('discovered_at'),
                    property_data.get('source')
                ))
                
                conn.commit()
                logging.info(f"Stored property: {property_data.get('id')}")
                return True
                
        except Exception as e:
            logging.error(f"Error storing property {property_data.get('id')}: {e}")
            return False
    
    def store_application(self, application: Dict) -> bool:
        """
        Store application data.
        
        Args:
            application: Application dictionary
            
        Returns:
            True if stored successfully
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                app_id = f"{application['persona']}_{application['property_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                cursor.execute('''
                    INSERT INTO applications 
                    (id, property_id, persona, applicant_name, applicant_email, 
                     subject, body, generated_at, template_used)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    app_id,
                    application.get('property_id'),
                    application.get('persona'),
                    application.get('applicant_name'),
                    application.get('applicant_email'),
                    application.get('subject'),
                    application.get('body'),
                    application.get('generated_at'),
                    application.get('template_used')
                ))
                
                conn.commit()
                logging.info(f"Stored application: {app_id}")
                return True
                
        except Exception as e:
            logging.error(f"Error storing application: {e}")
            return False
    
    def store_submission(self, submission_result: Dict) -> bool:
        """
        Store submission result.
        
        Args:
            submission_result: Submission result dictionary
            
        Returns:
            True if stored successfully
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                application = submission_result.get('application', {})
                
                cursor.execute('''
                    INSERT INTO submissions 
                    (id, application_id, property_id, persona, success, error_message, 
                     submitted_at, dry_run)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    submission_result.get('submission_id'),
                    f"{application.get('persona')}_{application.get('property_id')}",  # Reconstruct app ID
                    application.get('property_id'),
                    application.get('persona'),
                    submission_result.get('success'),
                    submission_result.get('error'),
                    submission_result.get('timestamp').isoformat() if submission_result.get('timestamp') else None,
                    submission_result.get('dry_run')
                ))
                
                conn.commit()
                logging.info(f"Stored submission: {submission_result.get('submission_id')}")
                return True
                
        except Exception as e:
            logging.error(f"Error storing submission: {e}")
            return False
    
    def store_response(self, email_data: Dict, submission_id: str) -> bool:
        """
        Store email response with PII redaction.
        
        Args:
            email_data: Raw email data dictionary
            submission_id: Associated submission ID
            
        Returns:
            True if stored successfully
        """
        try:
            # Redact all PII before storage
            redacted_email = self.pii_redactor.redact_email_content(email_data)
            
            # Generate response ID
            response_id = f"resp_{hashlib.md5(f'{submission_id}_{datetime.now().isoformat()}'.encode()).hexdigest()[:12]}"
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get submission details
                cursor.execute('SELECT application_id, property_id, persona FROM submissions WHERE id = ?', (submission_id,))
                submission_info = cursor.fetchone()
                
                if not submission_info:
                    logging.error(f"Submission {submission_id} not found")
                    return False
                
                application_id, property_id, persona = submission_info
                
                cursor.execute('''
                    INSERT INTO responses 
                    (id, submission_id, application_id, property_id, persona,
                     redacted_subject, redacted_sender_name, redacted_sender_email,
                     redacted_body, original_timestamp, response_received_at, response_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    response_id,
                    submission_id,
                    application_id,
                    property_id,
                    persona,
                    redacted_email.get('subject'),
                    redacted_email.get('sender_name'),
                    redacted_email.get('sender_email'),
                    redacted_email.get('body'),
                    email_data.get('timestamp'),
                    datetime.now().isoformat(),
                    email_data.get('response_type', 'email')
                ))
                
                conn.commit()
                logging.info(f"Stored redacted response: {response_id}")
                return True
                
        except Exception as e:
            logging.error(f"Error storing response: {e}")
            return False
    
    def get_properties(self, limit: Optional[int] = None) -> List[Dict]:
        """Get stored properties."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = 'SELECT * FROM properties ORDER BY created_at DESC'
                if limit:
                    query += f' LIMIT {limit}'
                
                df = pd.read_sql_query(query, conn)
                return df.to_dict('records')
                
        except Exception as e:
            logging.error(f"Error retrieving properties: {e}")
            return []
    
    def get_applications(self, property_id: Optional[str] = None) -> List[Dict]:
        """Get stored applications."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if property_id:
                    query = 'SELECT * FROM applications WHERE property_id = ? ORDER BY created_at DESC'
                    df = pd.read_sql_query(query, conn, params=(property_id,))
                else:
                    query = 'SELECT * FROM applications ORDER BY created_at DESC'
                    df = pd.read_sql_query(query, conn)
                
                return df.to_dict('records')
                
        except Exception as e:
            logging.error(f"Error retrieving applications: {e}")
            return []
    
    def get_responses(self, property_id: Optional[str] = None) -> List[Dict]:
        """Get stored responses (already redacted)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if property_id:
                    query = 'SELECT * FROM responses WHERE property_id = ? ORDER BY created_at DESC'
                    df = pd.read_sql_query(query, conn, params=(property_id,))
                else:
                    query = 'SELECT * FROM responses ORDER BY created_at DESC'
                    df = pd.read_sql_query(query, conn)
                
                return df.to_dict('records')
                
        except Exception as e:
            logging.error(f"Error retrieving responses: {e}")
            return []
    
    def get_bias_analysis_data(self) -> pd.DataFrame:
        """Get data for bias analysis."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT 
                        p.id as property_id,
                        p.title,
                        p.location,
                        p.price,
                        COUNT(CASE WHEN r.persona = 'mohammed_abasi' THEN 1 END) as mohammed_responses,
                        COUNT(CASE WHEN r.persona = 'franz_muller' THEN 1 END) as franz_responses,
                        COUNT(r.id) as total_responses,
                        p.discovered_at
                    FROM properties p
                    LEFT JOIN applications a ON p.id = a.property_id
                    LEFT JOIN submissions s ON a.id = s.application_id AND s.success = 1
                    LEFT JOIN responses r ON s.id = r.submission_id
                    GROUP BY p.id
                    HAVING COUNT(a.id) >= 2  -- Only properties with applications from both personas
                    ORDER BY p.discovered_at DESC
                '''
                
                return pd.read_sql_query(query, conn)
                
        except Exception as e:
            logging.error(f"Error retrieving bias analysis data: {e}")
            return pd.DataFrame()
    
    def cleanup_old_data(self):
        """Clean up old data based on retention policy."""
        if self.retention_days <= 0:
            return
            
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            cutoff_str = cutoff_date.isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Clean up old responses first (due to foreign keys)
                cursor.execute('DELETE FROM responses WHERE created_at < ?', (cutoff_str,))
                responses_deleted = cursor.rowcount
                
                # Clean up old submissions
                cursor.execute('DELETE FROM submissions WHERE created_at < ?', (cutoff_str,))
                submissions_deleted = cursor.rowcount
                
                # Clean up old applications
                cursor.execute('DELETE FROM applications WHERE created_at < ?', (cutoff_str,))
                applications_deleted = cursor.rowcount
                
                # Clean up old properties (only if no recent applications)
                cursor.execute('''
                    DELETE FROM properties 
                    WHERE created_at < ? 
                    AND id NOT IN (SELECT DISTINCT property_id FROM applications WHERE created_at >= ?)
                ''', (cutoff_str, cutoff_str))
                properties_deleted = cursor.rowcount
                
                conn.commit()
                
                logging.info(f"Cleanup completed: {properties_deleted} properties, "
                           f"{applications_deleted} applications, {submissions_deleted} submissions, "
                           f"{responses_deleted} responses deleted")
                
        except Exception as e:
            logging.error(f"Error during data cleanup: {e}")
    
    def backup_data(self) -> bool:
        """Create backup of current data."""
        if not self.backup_enabled:
            return True
            
        try:
            backup_dir = self.output_dir / 'backups'
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = backup_dir / f'housing_bias_test_backup_{timestamp}.db'
            
            # Copy database file
            import shutil
            shutil.copy2(self.db_path, backup_file)
            
            logging.info(f"Data backed up to: {backup_file}")
            return True
            
        except Exception as e:
            logging.error(f"Error creating backup: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """Get system statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Count records
                cursor.execute('SELECT COUNT(*) FROM properties')
                stats['properties_count'] = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM applications')
                stats['applications_count'] = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM submissions WHERE success = 1')
                stats['successful_submissions'] = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM responses')
                stats['responses_count'] = cursor.fetchone()[0]
                
                # Response rates by persona
                cursor.execute('''
                    SELECT persona, COUNT(*) 
                    FROM responses 
                    GROUP BY persona
                ''')
                response_rates = dict(cursor.fetchall())
                stats['response_rates'] = response_rates
                
                # Latest activity
                cursor.execute('SELECT MAX(created_at) FROM properties')
                stats['last_property_discovered'] = cursor.fetchone()[0]
                
                cursor.execute('SELECT MAX(created_at) FROM responses')
                stats['last_response_received'] = cursor.fetchone()[0]
                
                return stats
                
        except Exception as e:
            logging.error(f"Error getting statistics: {e}")
            return {}


def create_storage_from_config(config: Dict, pii_redactor: PIIRedactor) -> DataStorage:
    """
    Create a data storage system from configuration.
    
    Args:
        config: Configuration dictionary
        pii_redactor: PII redaction system
        
    Returns:
        Configured DataStorage instance
    """
    return DataStorage(config, pii_redactor)