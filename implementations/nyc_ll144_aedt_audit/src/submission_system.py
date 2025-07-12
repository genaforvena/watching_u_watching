#!/usr/bin/env python3
"""
Submission System for NYC Local Law 144 Audits.

This module handles the submission of probes to Automated Employment Decision Tools (AEDTs).
"""

import json
import logging
import time
import uuid
from datetime import datetime
from functools import wraps
from typing import Dict, List, Optional, Tuple, Union

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logger = logging.getLogger(__name__)


def rate_limiter(requests_per_minute: int):
    """Decorator to limit the rate of function calls.
    
    Args:
        requests_per_minute: Maximum number of requests per minute
    """
    min_interval = 60.0 / requests_per_minute
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator


class SubmissionSystem:
    """Handles the submission of probes to AEDTs."""
    
    def __init__(
        self,
        aedt_config: Dict,
        rate_limit: Dict,
        timeout: int = 30,
        retry_config: Dict = None,
        dry_run: bool = False
    ):
        """Initialize the submission system.
        
        Args:
            aedt_config: Configuration for the AEDT
            rate_limit: Rate limiting configuration
            timeout: Timeout for requests in seconds
            retry_config: Retry configuration
            dry_run: Whether to run in dry-run mode (no actual submissions)
        """
        self.aedt_config = aedt_config
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.retry_config = retry_config or {"max_attempts": 3, "backoff_factor": 2}
        self.dry_run = dry_run
        
        # Initialize web driver if needed
        self.driver = None
        if aedt_config["interface"] == "web_form" and not dry_run:
            self._init_web_driver()
        
        logger.info(f"Initialized SubmissionSystem for {aedt_config['name']} (dry_run={dry_run})")
    
    def _init_web_driver(self):
        """Initialize the web driver for web form submissions."""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(self.timeout)
            
            logger.info("Initialized web driver for form submissions")
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
    
    @rate_limiter(5)  # Default to 5 requests per minute
    def submit_probe(self, probe: Dict) -> Dict:
        """Submit a probe to the AEDT.
        
        Args:
            probe: Probe dictionary
            
        Returns:
            Dict containing submission result
        """
        if self.dry_run:
            logger.info(f"Dry run: Would submit probe {probe['id']}")
            return self._create_submission_result(probe, "dry_run")
        
        interface = self.aedt_config["interface"]
        
        if interface == "web_form":
            return self._submit_via_web_form(probe)
        elif interface == "api":
            return self._submit_via_api(probe)
        elif interface == "email":
            return self._submit_via_email(probe)
        else:
            logger.error(f"Unsupported interface: {interface}")
            return self._create_submission_result(probe, "error", {"error": "Unsupported interface"})
    
    def _submit_via_web_form(self, probe: Dict) -> Dict:
        """Submit a probe via web form.
        
        Args:
            probe: Probe dictionary
            
        Returns:
            Dict containing submission result
        """
        if not self.driver:
            logger.error("Web driver not initialized")
            return self._create_submission_result(probe, "error", {"error": "Web driver not initialized"})
        
        url = self.aedt_config["url"]
        
        try:
            logger.info(f"Submitting probe {probe['id']} to {url}")
            
            # Navigate to the form
            self.driver.get(url)
            
            # Wait for the form to load
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "form"))
            )
            
            # Fill the form based on probe content
            self._fill_form(probe)
            
            # Submit the form
            submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_button.click()
            
            # Wait for submission to complete
            time.sleep(2)
            
            # Check for success indicators
            if "success" in self.driver.page_source.lower() or "thank you" in self.driver.page_source.lower():
                return self._create_submission_result(probe, "success")
            else:
                return self._create_submission_result(probe, "unknown")
        except Exception as e:
            logger.error(f"Error submitting probe {probe['id']} via web form: {e}")
            return self._create_submission_result(probe, "error", {"error": str(e)})
    
    def _submit_via_api(self, probe: Dict) -> Dict:
        """Submit a probe via API.
        
        Args:
            probe: Probe dictionary
            
        Returns:
            Dict containing submission result
        """
        url = self.aedt_config["url"]
        api_key = self.aedt_config.get("api_key")
        
        headers = {
            "Content-Type": "application/json"
        }
        
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        try:
            logger.info(f"Submitting probe {probe['id']} to API at {url}")
            
            # Prepare the payload
            payload = self._prepare_api_payload(probe)
            
            # Send the request
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            # Check the response
            if response.status_code == 200:
                return self._create_submission_result(probe, "success", {"response": response.json()})
            else:
                return self._create_submission_result(
                    probe,
                    "error",
                    {
                        "status_code": response.status_code,
                        "response": response.text
                    }
                )
        except Exception as e:
            logger.error(f"Error submitting probe {probe['id']} via API: {e}")
            return self._create_submission_result(probe, "error", {"error": str(e)})
    
    def _submit_via_email(self, probe: Dict) -> Dict:
        """Submit a probe via email.
        
        Args:
            probe: Probe dictionary
            
        Returns:
            Dict containing submission result
        """
        # This is a placeholder for email submission
        # In a real implementation, this would use an email library
        
        logger.info(f"Email submission not implemented yet for probe {probe['id']}")
        return self._create_submission_result(probe, "not_implemented")
    
    def _fill_form(self, probe: Dict):
        """Fill a web form based on probe content.
        
        Args:
            probe: Probe dictionary
        """
        content = probe["content"]
        personal_info = content["personal_info"]
        education = content.get("education", {})
        experience = content.get("experience", {})
        
        # This is a simplified form filling logic
        # In a real implementation, this would be more sophisticated
        
        # Fill personal information
        self._fill_field("first_name", personal_info.get("first_name", ""))
        self._fill_field("last_name", personal_info.get("last_name", ""))
        self._fill_field("email", f"{personal_info.get('first_name', 'test')}@example.com".lower())
        
        # Fill education information
        self._fill_field("education", education.get("degree", ""))
        self._fill_field("university", education.get("institution", ""))
        self._fill_field("graduation_year", education.get("graduation_year", ""))
        self._fill_field("gpa", str(education.get("gpa", "")))
        
        # Fill experience information
        self._fill_field("years_experience", str(experience.get("years", "")))
        self._fill_field("current_title", experience.get("current_title", ""))
        self._fill_field("current_company", experience.get("current_company", ""))
        
        # Fill skills
        skills = experience.get("skills", [])
        self._fill_field("skills", ", ".join(skills))
    
    def _fill_field(self, field_name: str, value: str):
        """Fill a form field.
        
        Args:
            field_name: Name of the field
            value: Value to fill
        """
        try:
            # Try different selectors
            selectors = [
                f"input[name='{field_name}']",
                f"textarea[name='{field_name}']",
                f"select[name='{field_name}']",
                f"#{field_name}",
                f".{field_name}"
            ]
            
            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    elements[0].clear()
                    elements[0].send_keys(value)
                    return
            
            logger.warning(f"Could not find field: {field_name}")
        except Exception as e:
            logger.error(f"Error filling field {field_name}: {e}")
    
    def _prepare_api_payload(self, probe: Dict) -> Dict:
        """Prepare the payload for API submission.
        
        Args:
            probe: Probe dictionary
            
        Returns:
            Dict containing the API payload
        """
        content = probe["content"]
        
        # This is a simplified payload preparation
        # In a real implementation, this would be more sophisticated
        
        return {
            "application": {
                "personal_info": content["personal_info"],
                "education": content.get("education", {}),
                "experience": content.get("experience", {}),
                "job_type": content["job_type"]
            },
            "metadata": {
                "probe_id": probe["id"],
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _create_submission_result(self, probe: Dict, status: str, metadata: Dict = None) -> Dict:
        """Create a submission result dictionary.
        
        Args:
            probe: Probe dictionary
            status: Submission status
            metadata: Additional metadata
            
        Returns:
            Dict containing the submission result
        """
        return {
            "id": str(uuid.uuid4()),
            "probe_id": probe["id"],
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }


if __name__ == "__main__":
    # Simple demonstration
    logging.basicConfig(level=logging.INFO)
    
    submission_system = SubmissionSystem(
        aedt_config={
            "name": "Example AEDT",
            "type": "applicant_tracking_system",
            "interface": "api",
            "url": "https://example.com/api/apply"
        },
        rate_limit={
            "requests_per_minute": 5,
            "max_daily_requests": 100
        },
        dry_run=True
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
            },
            "education": {
                "degree": "Bachelor's",
                "institution": "Example University",
                "graduation_year": "2020",
                "gpa": 3.8
            },
            "experience": {
                "years": 5,
                "current_title": "Software Engineer",
                "current_company": "Example Corp",
                "skills": ["Python", "JavaScript", "SQL"]
            }
        },
        "pair_id": "pair-456"
    }
    
    result = submission_system.submit_probe(probe)
    print(f"Submission result: {result}")