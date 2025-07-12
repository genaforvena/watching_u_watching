#!/usr/bin/env python3
"""
Response Collector for NYC Local Law 144 Audits.

This module collects responses from Automated Employment Decision Tools (AEDTs).
"""

import email
import imaplib
import json
import logging
import re
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from .pii_redactor import PIIRedactor

# Configure logging
logger = logging.getLogger(__name__)


class ResponseCollector:
    """Collects responses from AEDTs."""
    
    def __init__(
        self,
        methods: List[str],
        email_config: Dict = None,
        check_interval: int = 60,
        max_wait_days: int = 14,
        dry_run: bool = False
    ):
        """Initialize the response collector.
        
        Args:
            methods: List of collection methods
            email_config: Email configuration
            check_interval: Interval between checks in minutes
            max_wait_days: Maximum number of days to wait for responses
            dry_run: Whether to run in dry-run mode
        """
        self.methods = methods
        self.email_config = email_config
        self.check_interval = check_interval
        self.max_wait_days = max_wait_days
        self.dry_run = dry_run
        
        # Initialize PII redactor
        self.pii_redactor = PIIRedactor()
        
        # Initialize web driver if needed
        self.driver = None
        if "web_portal" in methods and not dry_run:
            self._init_web_driver()
        
        logger.info(f"Initialized ResponseCollector with methods: {methods} (dry_run={dry_run})")
    
    def _init_web_driver(self):
        """Initialize the web driver for web portal access."""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            logger.info("Initialized web driver for web portal access")
        except Exception as e:
            logger.error(f"Error initializing web driver: {e}")
            self.driver = None
    
    def __del__(self):
        """Clean up resources."""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
    
    def collect_responses(self, submission_results: List[Dict]) -> List[Dict]:
        """Collect responses for submissions.
        
        Args:
            submission_results: List of submission result dictionaries
            
        Returns:
            List of response dictionaries
        """
        if self.dry_run:
            logger.info(f"Dry run: Would collect responses for {len(submission_results)} submissions")
            return self._generate_mock_responses(submission_results)
        
        responses = []
        
        for method in self.methods:
            if method == "email":
                responses.extend(self._collect_via_email(submission_results))
            elif method == "web_portal":
                responses.extend(self._collect_via_web_portal(submission_results))
            elif method == "api":
                responses.extend(self._collect_via_api(submission_results))
            else:
                logger.warning(f"Unsupported collection method: {method}")
        
        logger.info(f"Collected {len(responses)} responses")
        return responses
    
    def _collect_via_email(self, submission_results: List[Dict]) -> List[Dict]:
        """Collect responses via email.
        
        Args:
            submission_results: List of submission result dictionaries
            
        Returns:
            List of response dictionaries
        """
        if not self.email_config:
            logger.error("Email configuration not provided")
            return []
        
        responses = []
        
        try:
            # Connect to the email server
            mail = imaplib.IMAP4_SSL(self.email_config["imap_server"])
            mail.login(self.email_config["username"], self.email_config["password"])
            mail.select(self.email_config["folder"])
            
            # Calculate the date range
            since_date = (datetime.now() - timedelta(days=self.max_wait_days)).strftime("%d-%b-%Y")
            
            # Search for emails
            status, data = mail.search(None, f'(SINCE {since_date})')
            email_ids = data[0].split()
            
            for email_id in email_ids:
                status, data = mail.fetch(email_id, '(RFC822)')
                raw_email = data[0][1]
                
                # Parse the email
                msg = email.message_from_bytes(raw_email)
                subject = msg["subject"] or ""
                sender = msg["from"] or ""
                
                # Extract the body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        if content_type == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = msg.get_payload(decode=True).decode()
                
                # Process the email in memory
                response_data = self._process_email_content(subject, sender, body, submission_results)
                
                if response_data:
                    responses.append(response_data)
            
            mail.close()
            mail.logout()
        except Exception as e:
            logger.error(f"Error collecting responses via email: {e}")
        
        return responses
    
    def _collect_via_web_portal(self, submission_results: List[Dict]) -> List[Dict]:
        """Collect responses via web portal.
        
        Args:
            submission_results: List of submission result dictionaries
            
        Returns:
            List of response dictionaries
        """
        if not self.driver:
            logger.error("Web driver not initialized")
            return []
        
        responses = []
        
        # This is a placeholder for web portal collection
        # In a real implementation, this would navigate to the portal and extract responses
        
        logger.info("Web portal collection not fully implemented yet")
        return responses
    
    def _collect_via_api(self, submission_results: List[Dict]) -> List[Dict]:
        """Collect responses via API.
        
        Args:
            submission_results: List of submission result dictionaries
            
        Returns:
            List of response dictionaries
        """
        responses = []
        
        # This is a placeholder for API collection
        # In a real implementation, this would call the API to get responses
        
        logger.info("API collection not fully implemented yet")
        return responses
    
    def _process_email_content(
        self,
        subject: str,
        sender: str,
        body: str,
        submission_results: List[Dict]
    ) -> Optional[Dict]:
        """Process email content to extract response data.
        
        Args:
            subject: Email subject
            sender: Email sender
            body: Email body
            submission_results: List of submission result dictionaries
            
        Returns:
            Response dictionary or None
        """
        # This is a simplified email processing logic
        # In a real implementation, this would be more sophisticated
        
        # Extract probe ID from subject or body
        probe_id_match = re.search(r'probe-(\w+)', subject) or re.search(r'probe-(\w+)', body)
        if not probe_id_match:
            return None
        
        probe_id = f"probe-{probe_id_match.group(1)}"
        
        # Find the corresponding submission
        submission = next((s for s in submission_results if s["probe_id"] == probe_id), None)
        if not submission:
            return None
        
        # Determine response type
        response_type = "unknown"
        selected = False
        
        if re.search(r'interview|proceed|next step|selected|congratulations', body, re.IGNORECASE):
            response_type = "interview"
            selected = True
        elif re.search(r'reject|decline|unfortunately|not proceed|not selected', body, re.IGNORECASE):
            response_type = "rejection"
            selected = False
        
        # Create the response
        response = {
            "id": str(uuid.uuid4()),
            "submission_id": submission["id"],
            "response_type": response_type,
            "selected": selected,
            "timestamp": datetime.now().isoformat(),
            "content": "",  # No content stored, only metadata
            "metadata": {
                "has_response": True,
                "response_time_hours": self._calculate_response_time(submission["timestamp"])
            }
        }
        
        return response
    
    def _calculate_response_time(self, submission_timestamp: str) -> float:
        """Calculate the response time in hours.
        
        Args:
            submission_timestamp: Submission timestamp
            
        Returns:
            Response time in hours
        """
        submission_time = datetime.fromisoformat(submission_timestamp)
        response_time = datetime.now()
        
        delta = response_time - submission_time
        return delta.total_seconds() / 3600
    
    def _generate_mock_responses(self, submission_results: List[Dict]) -> List[Dict]:
        """Generate mock responses for dry run.
        
        Args:
            submission_results: List of submission result dictionaries
            
        Returns:
            List of response dictionaries
        """
        import random
        
        responses = []
        
        for submission in submission_results:
            # Extract probe information
            probe_id = submission["probe_id"]
            
            # Determine response type and selection status
            if random.random() < 0.7:  # 70% chance of getting a response
                if random.random() < 0.5:  # 50% chance of being selected
                    response_type = "interview"
                    selected = True
                else:
                    response_type = "rejection"
                    selected = False
                
                # Create the response
                response = {
                    "id": str(uuid.uuid4()),
                    "submission_id": submission["id"],
                    "response_type": response_type,
                    "selected": selected,
                    "timestamp": (datetime.fromisoformat(submission["timestamp"]) + timedelta(days=random.randint(1, 5))).isoformat(),
                    "content": "",  # No content stored, only metadata
                    "metadata": {
                        "has_response": True,
                        "response_time_hours": random.randint(24, 120),
                        "mock_response": True
                    }
                }
                
                responses.append(response)
        
        return responses


if __name__ == "__main__":
    # Simple demonstration
    logging.basicConfig(level=logging.INFO)
    
    collector = ResponseCollector(
        methods=["email"],
        email_config={
            "imap_server": "imap.example.com",
            "username": "test@example.com",
            "password": "password",
            "folder": "INBOX"
        },
        dry_run=True
    )
    
    # Example submission results
    submission_results = [
        {
            "id": "submission-123",
            "probe_id": "probe-456",
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "metadata": {}
        },
        {
            "id": "submission-789",
            "probe_id": "probe-101112",
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "metadata": {}
        }
    ]
    
    responses = collector.collect_responses(submission_results)
    
    for response in responses:
        print(f"Response ID: {response['id']}")
        print(f"Submission ID: {response['submission_id']}")
        print(f"Response Type: {response['response_type']}")
        print(f"Selected: {response['selected']}")
        print(f"Timestamp: {response['timestamp']}")
        print("---")