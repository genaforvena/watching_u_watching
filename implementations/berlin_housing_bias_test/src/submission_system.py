"""
Submission System for Berlin Housing Bias Testing

This module handles the automated submission of rental applications
to Immobilienscout24.de using the platform's standard processes.
"""

import time
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import random

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from fake_useragent import UserAgent


class ApplicationSubmissionSystem:
    """
    Handles submission of rental applications to Immobilienscout24.de
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the submission system.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.submission_config = config.get('applications', {})
        self.browser_config = config.get('browser', {})
        
        self.submission_delay = self.submission_config.get('submission_delay_minutes', 15)
        self.max_applications_per_day = self.submission_config.get('max_applications_per_day', 20)
        
        # Track submissions to respect rate limits
        self.daily_submissions = 0
        self.last_submission_date = None
        self.submission_history = []
        
        self.driver = None
        self.ua = UserAgent()
        
    def _setup_driver(self):
        """Setup Selenium WebDriver for form submission."""
        if self.driver:
            return
            
        try:
            chrome_options = ChromeOptions()
            if self.browser_config.get('headless', True):
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            if self.browser_config.get('user_agent_rotation', True):
                chrome_options.add_argument(f'--user-agent={self.ua.random}')
                
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(self.browser_config.get('page_load_timeout', 30))
            logging.info("Submission WebDriver initialized successfully")
            
        except Exception as e:
            logging.error(f"Could not initialize WebDriver for submissions: {e}")
            raise
    
    def _check_rate_limits(self) -> bool:
        """
        Check if we can submit another application based on rate limits.
        
        Returns:
            True if submission is allowed
        """
        current_date = datetime.now().date()
        
        # Reset daily counter if it's a new day
        if self.last_submission_date != current_date:
            self.daily_submissions = 0
            self.last_submission_date = current_date
        
        # Check daily limit
        if self.daily_submissions >= self.max_applications_per_day:
            logging.warning(f"Daily submission limit reached: {self.daily_submissions}/{self.max_applications_per_day}")
            return False
        
        # Check minimum delay between submissions
        if self.submission_history:
            last_submission_time = self.submission_history[-1]['timestamp']
            time_since_last = datetime.now() - last_submission_time
            min_delay = timedelta(minutes=self.submission_delay)
            
            if time_since_last < min_delay:
                remaining_wait = min_delay - time_since_last
                logging.info(f"Need to wait {remaining_wait.total_seconds()/60:.1f} more minutes before next submission")
                return False
        
        return True
    
    def _navigate_to_property(self, property_url: str) -> bool:
        """
        Navigate to property page and locate contact form.
        
        Args:
            property_url: URL of the property listing
            
        Returns:
            True if navigation successful
        """
        try:
            self.driver.get(property_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Look for contact button or form
            contact_selectors = [
                "button[data-qa='sendContactRequest']",
                "button[data-testid='contact-button']",
                ".contact-button",
                "button:contains('Kontakt')",
                "a:contains('Nachricht schreiben')",
                ".expose-contact-form button"
            ]
            
            contact_button = None
            for selector in contact_selectors:
                try:
                    contact_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if not contact_button:
                logging.error(f"Could not find contact button on {property_url}")
                return False
            
            # Click contact button if found
            try:
                contact_button.click()
                time.sleep(2)  # Wait for form to appear
                return True
            except Exception as e:
                logging.error(f"Could not click contact button: {e}")
                return False
                
        except Exception as e:
            logging.error(f"Error navigating to property {property_url}: {e}")
            return False
    
    def _fill_contact_form(self, application: Dict) -> bool:
        """
        Fill out the contact form with application data.
        
        Args:
            application: Application data dictionary
            
        Returns:
            True if form filled successfully
        """
        try:
            # Wait for form to be visible
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "form"))
            )
            
            # Common form field selectors
            field_selectors = {
                'name': [
                    "input[name='name']",
                    "input[data-qa='name']",
                    "input[placeholder*='Name']",
                    "#name",
                    ".name-field input"
                ],
                'email': [
                    "input[name='email']",
                    "input[type='email']",
                    "input[data-qa='email']",
                    "input[placeholder*='E-Mail']",
                    "#email"
                ],
                'phone': [
                    "input[name='phone']",
                    "input[type='tel']",
                    "input[data-qa='phone']",
                    "input[placeholder*='Telefon']",
                    "#phone"
                ],
                'message': [
                    "textarea[name='message']",
                    "textarea[data-qa='message']",
                    "textarea[placeholder*='Nachricht']",
                    "#message",
                    ".message-field textarea"
                ],
                'subject': [
                    "input[name='subject']",
                    "input[data-qa='subject']",
                    "input[placeholder*='Betreff']",
                    "#subject"
                ]
            }
            
            # Fill name field
            name_field = self._find_element_by_selectors(field_selectors['name'])
            if name_field:
                name_field.clear()
                name_field.send_keys(application['applicant_name'])
                logging.info(f"Filled name: {application['applicant_name']}")
            else:
                logging.warning("Could not find name field")
            
            # Fill email field
            email_field = self._find_element_by_selectors(field_selectors['email'])
            if email_field:
                email_field.clear()
                email_field.send_keys(application['applicant_email'])
                logging.info(f"Filled email: {application['applicant_email']}")
            else:
                logging.warning("Could not find email field")
            
            # Fill phone field (optional, use a dummy number)
            phone_field = self._find_element_by_selectors(field_selectors['phone'])
            if phone_field:
                dummy_phone = "+49 30 12345678"  # Dummy Berlin number
                phone_field.clear()
                phone_field.send_keys(dummy_phone)
                logging.info("Filled phone field with dummy number")
            
            # Fill subject field if present
            subject_field = self._find_element_by_selectors(field_selectors['subject'])
            if subject_field:
                subject_field.clear()
                subject_field.send_keys(application['subject'])
                logging.info("Filled subject field")
            
            # Fill message field
            message_field = self._find_element_by_selectors(field_selectors['message'])
            if message_field:
                message_field.clear()
                message_field.send_keys(application['body'])
                logging.info("Filled message field")
            else:
                logging.error("Could not find message field - this is required")
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"Error filling contact form: {e}")
            return False
    
    def _find_element_by_selectors(self, selectors: List[str]):
        """Find element using multiple possible selectors."""
        for selector in selectors:
            try:
                return self.driver.find_element(By.CSS_SELECTOR, selector)
            except NoSuchElementException:
                continue
        return None
    
    def _submit_form(self, dry_run: bool = True) -> bool:
        """
        Submit the filled contact form.
        
        Args:
            dry_run: If True, don't actually submit (for testing)
            
        Returns:
            True if submission successful
        """
        try:
            # Find submit button
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button[data-qa='submit']",
                "button:contains('Senden')",
                "button:contains('Absenden')",
                ".submit-button"
            ]
            
            submit_button = self._find_element_by_selectors(submit_selectors)
            
            if not submit_button:
                logging.error("Could not find submit button")
                return False
            
            if dry_run:
                logging.info("DRY RUN: Would submit form now (button found)")
                return True
            else:
                # Actual submission
                submit_button.click()
                
                # Wait for submission confirmation or error
                time.sleep(3)
                
                # Check for success indicators
                success_indicators = [
                    "Ihre Nachricht wurde versendet",
                    "Nachricht gesendet",
                    "Vielen Dank",
                    "success",
                    "thank-you"
                ]
                
                page_text = self.driver.page_source.lower()
                success = any(indicator.lower() in page_text for indicator in success_indicators)
                
                if success:
                    logging.info("Form submitted successfully")
                    return True
                else:
                    logging.warning("Form submission status unclear")
                    return False
                    
        except Exception as e:
            logging.error(f"Error submitting form: {e}")
            return False
    
    def submit_application(self, application: Dict, dry_run: bool = True) -> Dict:
        """
        Submit a single application.
        
        Args:
            application: Application data dictionary
            dry_run: If True, don't actually submit
            
        Returns:
            Dictionary with submission results
        """
        submission_id = f"{application['persona']}_{application['property_id']}_{int(time.time())}"
        
        result = {
            'submission_id': submission_id,
            'application': application,
            'timestamp': datetime.now(),
            'success': False,
            'error': None,
            'dry_run': dry_run
        }
        
        try:
            # Check rate limits
            if not self._check_rate_limits():
                result['error'] = 'Rate limit exceeded'
                return result
            
            # Setup driver if needed
            if not self.driver:
                self._setup_driver()
            
            # Navigate to property
            if not self._navigate_to_property(application['property_url']):
                result['error'] = 'Could not navigate to property page'
                return result
            
            # Fill form
            if not self._fill_contact_form(application):
                result['error'] = 'Could not fill contact form'
                return result
            
            # Submit form
            if self._submit_form(dry_run=dry_run):
                result['success'] = True
                
                # Update tracking
                if not dry_run:
                    self.daily_submissions += 1
                self.submission_history.append(result)
                
                logging.info(f"Application submitted successfully: {submission_id}")
            else:
                result['error'] = 'Form submission failed'
                
        except Exception as e:
            result['error'] = str(e)
            logging.error(f"Error submitting application {submission_id}: {e}")
        
        return result
    
    def submit_paired_applications(self, applications: List[Dict], dry_run: bool = True) -> List[Dict]:
        """
        Submit paired applications with appropriate delays.
        
        Args:
            applications: List of application dictionaries
            dry_run: If True, don't actually submit
            
        Returns:
            List of submission result dictionaries
        """
        results = []
        
        # Randomize order to avoid patterns
        shuffled_apps = applications.copy()
        random.shuffle(shuffled_apps)
        
        for i, application in enumerate(shuffled_apps):
            logging.info(f"Submitting application {i+1}/{len(applications)} for {application['persona']}")
            
            result = self.submit_application(application, dry_run=dry_run)
            results.append(result)
            
            # Delay between applications in the same property
            if i < len(shuffled_apps) - 1:
                delay_minutes = random.uniform(5, 15)  # Random delay between 5-15 minutes
                logging.info(f"Waiting {delay_minutes:.1f} minutes before next application")
                if not dry_run:
                    time.sleep(delay_minutes * 60)
                else:
                    logging.info("DRY RUN: Skipping delay")
        
        return results
    
    def get_submission_stats(self) -> Dict:
        """Get statistics about submissions."""
        return {
            'daily_submissions': self.daily_submissions,
            'max_daily_limit': self.max_applications_per_day,
            'total_submissions': len(self.submission_history),
            'successful_submissions': len([r for r in self.submission_history if r['success']]),
            'last_submission': self.submission_history[-1]['timestamp'] if self.submission_history else None
        }
    
    def cleanup(self):
        """Clean up resources."""
        if self.driver:
            try:
                self.driver.quit()
                logging.info("Submission WebDriver closed successfully")
            except Exception as e:
                logging.error(f"Error closing submission WebDriver: {e}")


def create_submission_system_from_config(config: Dict) -> ApplicationSubmissionSystem:
    """
    Create a submission system from configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configured ApplicationSubmissionSystem instance
    """
    return ApplicationSubmissionSystem(config)


# Example usage and testing
if __name__ == "__main__":
    # Test configuration
    test_config = {
        'applications': {
            'submission_delay_minutes': 5,
            'max_applications_per_day': 10
        },
        'browser': {
            'headless': True,
            'user_agent_rotation': True,
            'page_load_timeout': 30
        }
    }
    
    # Test application data
    test_applications = [
        {
            'persona': 'mohammed_abasi',
            'applicant_name': 'Mohammed Abasi',
            'applicant_email': 'mohammed.abasi.test@example.com',
            'subject': 'Bewerbung um die Wohnung',
            'body': 'Test application message...',
            'property_id': 'test_123',
            'property_url': 'https://www.immobilienscout24.de/expose/123'
        },
        {
            'persona': 'franz_muller',
            'applicant_name': 'Franz Müller',
            'applicant_email': 'franz.muller.test@example.com',
            'subject': 'Bewerbung um die Wohnung',
            'body': 'Test application message...',
            'property_id': 'test_123',
            'property_url': 'https://www.immobilienscout24.de/expose/123'
        }
    ]
    
    logging.basicConfig(level=logging.INFO)
    
    try:
        submission_system = create_submission_system_from_config(test_config)
        
        print("Testing application submission (DRY RUN)...")
        results = submission_system.submit_paired_applications(test_applications, dry_run=True)
        
        print(f"Submitted {len(results)} applications:")
        for result in results:
            status = "SUCCESS" if result['success'] else f"FAILED: {result['error']}"
            print(f"  {result['application']['persona']}: {status}")
        
        print(f"\nSubmission stats: {submission_system.get_submission_stats()}")
        
        submission_system.cleanup()
        
    except Exception as e:
        print(f"Error testing submission system: {e}")
        logging.error(f"Submission test failed: {e}", exc_info=True)