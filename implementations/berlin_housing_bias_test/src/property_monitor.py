"""
Property Monitor for Berlin Housing Bias Testing

This module monitors Immobilienscout24.de for new rental property postings
based on configured search criteria.
"""

import time
import logging
import hashlib
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlencode

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions


class PropertyMonitor:
    # List of top Berlin housing corporations and their known domains
    CORPORATE_LANDLORDS = [
        {
            'name': 'Deutsche Wohnen',
            'domains': ['deutsche-wohnen.com', 'deuwo.com'],
        },
        {
            'name': 'Vonovia',
            'domains': ['vonovia.de'],
        },
        {
            'name': 'Adler Group',
            'domains': ['adler-group.com', 'adler-wohnen.de'],
        },
        {
            'name': 'Covivio Immobilien',
            'domains': ['covivio.immo', 'covivio.de'],
        },
        {
            'name': 'Grand City Properties',
            'domains': ['grandcityproperty.de', 'grandcityproperties.com'],
        },
    ]

    def _get_landlord_category(self, property_data: Dict) -> str:
        """
        Return the name of the corporate landlord if matched, else 'other'.
        """
        text = (property_data.get('title', '') + ' ' + property_data.get('description', '')).lower()
        for corp in self.CORPORATE_LANDLORDS:
            if corp['name'].lower() in text:
                return corp['name']
        url = property_data.get('url', '').lower()
        for corp in self.CORPORATE_LANDLORDS:
            for domain in corp['domains']:
                if domain in url:
                    return corp['name']
        email = property_data.get('contact_email', '').lower()
        for corp in self.CORPORATE_LANDLORDS:
            for domain in corp['domains']:
                if domain in email:
                    return corp['name']
        return 'other'
    """
    Monitors Immobilienscout24.de for new rental property listings.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the property monitor.
        
        Args:
            config: Configuration dictionary containing monitoring settings
        """
        self.config = config
        self.monitoring_config = config.get('monitoring', {})
        self.browser_config = config.get('browser', {})
        self.base_url = self.monitoring_config.get('base_url', 'https://www.immobilienscout24.de')
        self.search_criteria = self.monitoring_config.get('search_criteria', {})
        self.rate_limit_delay = self.monitoring_config.get('rate_limit_delay_seconds', 5)
        self.max_listings_per_check = self.monitoring_config.get('max_listings_per_check', 10)
        
        # Track seen properties to avoid duplicates
        self.seen_property_ids: Set[str] = set()
        self.seen_urls: Set[str] = set()
        
        # User agent rotation
        self.ua = UserAgent()
        self.session = requests.Session()
        self.driver = None
        
        # Initialize browser if needed
        if self.browser_config.get('headless', True):
            self._setup_selenium()
    
    def _setup_selenium(self):
        """Setup Selenium WebDriver for JavaScript-heavy pages."""
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
            logging.info("Selenium WebDriver initialized successfully")
            
        except Exception as e:
            logging.warning(f"Could not initialize Chrome WebDriver: {e}")
            try:
                # Fallback to Firefox
                firefox_options = FirefoxOptions()
                if self.browser_config.get('headless', True):
                    firefox_options.add_argument('--headless')
                
                self.driver = webdriver.Firefox(options=firefox_options)
                logging.info("Firefox WebDriver initialized as fallback")
            except Exception as e2:
                logging.error(f"Could not initialize any WebDriver: {e2}")
                self.driver = None
    
    def _build_search_url(self) -> str:
        """
        Build search URL based on configured criteria.
        
        Returns:
            Complete search URL for Immobilienscout24.de
        """
        # Base search path
        search_path = "/Suche/de/wohnung-mieten"
        
        # Build query parameters
        params = {}
        
        # Location
        location = self.search_criteria.get('location', 'Berlin')
        search_path += f"/{location.lower()}"
        
        # Property type is already in the path (wohnung-mieten)
        
        # Rooms
        min_rooms = self.search_criteria.get('min_rooms')
        max_rooms = self.search_criteria.get('max_rooms')
        if min_rooms:
            params['numberofroomsfrom'] = str(min_rooms)
        if max_rooms:
            params['numberofroomsto'] = str(max_rooms)
        
        # Rent
        max_rent = self.search_criteria.get('max_rent')
        if max_rent:
            params['price'] = f'-{max_rent}'
        
        # Radius
        radius = self.search_criteria.get('radius')
        if radius:
            params['geocoordinates'] = f'{radius}'
        
        # Sort by newest first
        params['sorting'] = '1'  # Sort by creation date, newest first
        
        # Build final URL
        base_url = urljoin(self.base_url, search_path)
        if params:
            url = f"{base_url}?{urlencode(params)}"
        else:
            url = base_url
            
        logging.info(f"Built search URL: {url}")
        return url
    
    def _get_page_content(self, url: str) -> Optional[str]:
        """
        Get page content using requests or Selenium.
        
        Args:
            url: URL to fetch
            
        Returns:
            Page HTML content or None if error
        """
        try:
            # Try requests first (faster)
            headers = {
                'User-Agent': self.ua.random if self.browser_config.get('user_agent_rotation', True) else self.ua.chrome
            }
            
            response = self.session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Check if we need JavaScript rendering
            if 'javascript' in response.text.lower() or len(response.text) < 1000:
                logging.info("Page appears to require JavaScript, using Selenium")
                return self._get_page_content_selenium(url)
            
            return response.text
            
        except Exception as e:
            logging.warning(f"Requests failed for {url}: {e}")
            return self._get_page_content_selenium(url)
    
    def _get_page_content_selenium(self, url: str) -> Optional[str]:
        """
        Get page content using Selenium WebDriver.
        
        Args:
            url: URL to fetch
            
        Returns:
            Page HTML content or None if error
        """
        if not self.driver:
            logging.error("Selenium driver not available")
            return None
            
        try:
            self.driver.get(url)
            
            # Wait for content to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "result-list"))
            )
            
            return self.driver.page_source
            
        except Exception as e:
            logging.error(f"Selenium failed for {url}: {e}")
            return None
    
    def _extract_property_data(self, property_element) -> Optional[Dict]:
        """
        Extract property data from a search result element.
        
        Args:
            property_element: BeautifulSoup element containing property info
            
        Returns:
            Dictionary with property data or None if extraction fails
        """
        try:
            # Extract URL
            link_elem = property_element.find('a', {'data-id': True})
            if not link_elem:
                return None
                
            property_url = urljoin(self.base_url, link_elem.get('href', ''))
            property_id = link_elem.get('data-id', '')
            
            if not property_id:
                # Try to extract ID from URL
                property_id = self._extract_id_from_url(property_url)
            
            if not property_id:
                return None
            
            # Extract title
            title_elem = property_element.find('h2') or property_element.find('h3')
            title = title_elem.get_text(strip=True) if title_elem else 'Unknown Property'
            
            # Extract description
            desc_elem = property_element.find('p', {'class': 'result-list-entry__criteria'})
            description = desc_elem.get_text(strip=True) if desc_elem else ''
            
            # Extract price
            price_elem = property_element.find('dd', {'class': 'result-list-entry__primary-criterion'})
            price = price_elem.get_text(strip=True) if price_elem else 'N/A'
            
            # Extract location
            location_elem = property_element.find('div', {'class': 'result-list-entry__address'})
            location = location_elem.get_text(strip=True) if location_elem else 'N/A'
            
            # Extract rooms
            rooms_elem = property_element.find('dd', string=lambda text: text and 'Zimmer' in text)
            rooms = rooms_elem.get_text(strip=True) if rooms_elem else 'N/A'
            
            # Extract area
            area_elem = property_element.find('dd', string=lambda text: text and 'm²' in text)
            area = area_elem.get_text(strip=True) if area_elem else 'N/A'
            
            property_data = {
                'id': property_id,
                'url': property_url,
                'title': title,
                'description': description,
                'price': price,
                'location': location,
                'rooms': rooms,
                'area': area,
                'discovered_at': datetime.now().isoformat(),
                'source': 'immobilienscout24.de'
            }
            
            return property_data
            
        except Exception as e:
            logging.error(f"Error extracting property data: {e}")
            return None
    
    def _extract_id_from_url(self, url: str) -> str:
        """Extract property ID from URL."""
        try:
            # Common patterns for IDs in URLs
            import re
            patterns = [
                r'/expose/(\d+)',
                r'id=(\d+)',
                r'/(\d+)$'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            
            # Fallback: use URL hash
            return hashlib.md5(url.encode()).hexdigest()[:12]
            
        except Exception:
            return hashlib.md5(url.encode()).hexdigest()[:12]
    
    def check_for_new_properties(self) -> List[Dict]:
        """
        Check for new properties and return list of new ones.
        
        Returns:
            List of new property dictionaries
        """
        logging.info("Checking for new properties...")
        
        search_url = self._build_search_url()
        page_content = self._get_page_content(search_url)
        
        if not page_content:
            logging.error("Could not fetch search results page")
            return []
        
        soup = BeautifulSoup(page_content, 'html.parser')
        
        # Find property listings
        # This selector might need adjustment based on current page structure
        property_elements = soup.find_all('article', {'class': 'result-list-entry'})
        
        if not property_elements:
            # Try alternative selectors
            property_elements = soup.find_all('div', {'class': 'result-list-entry'})
        
        if not property_elements:
            logging.warning("No property elements found on page")
            return []
        
        new_properties = []
        for element in property_elements[:self.max_listings_per_check]:
            property_data = self._extract_property_data(element)
            if property_data:
                property_id = property_data['id']
                property_url = property_data['url']
                landlord_category = self._get_landlord_category(property_data)
                property_data['landlord_category'] = landlord_category
                # Check if we've seen this property before
                if property_id not in self.seen_property_ids and property_url not in self.seen_urls:
                    new_properties.append(property_data)
                    self.seen_property_ids.add(property_id)
                    self.seen_urls.add(property_url)
                    logging.info(f"Found new property: {property_id} - {property_data['title']} (landlord: {landlord_category})")
            time.sleep(self.rate_limit_delay)
        logging.info(f"Found {len(new_properties)} new properties")
        return new_properties
    
    def cleanup(self):
        """Clean up resources."""
        if self.driver:
            try:
                self.driver.quit()
                logging.info("WebDriver closed successfully")
            except Exception as e:
                logging.error(f"Error closing WebDriver: {e}")


def create_monitor_from_config(config: Dict) -> PropertyMonitor:
    """
    Create a property monitor from configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configured PropertyMonitor instance
    """
    return PropertyMonitor(config)


# Example usage and testing
if __name__ == "__main__":
    # Test configuration
    test_config = {
        'monitoring': {
            'base_url': 'https://www.immobilienscout24.de',
            'search_criteria': {
                'location': 'Berlin',
                'property_type': 'apartment',
                'min_rooms': 2,
                'max_rooms': 4,
                'max_rent': 2000,
                'radius': 20
            },
            'rate_limit_delay_seconds': 2,
            'max_listings_per_check': 5
        },
        'browser': {
            'headless': True,
            'user_agent_rotation': True,
            'page_load_timeout': 30
        }
    }
    
    logging.basicConfig(level=logging.INFO)
    
    try:
        monitor = create_monitor_from_config(test_config)
        
        print("Testing property monitoring...")
        new_properties = monitor.check_for_new_properties()
        
        print(f"Found {len(new_properties)} properties:")
        for prop in new_properties:
            print(f"  {prop['id']}: {prop['title']}")
            print(f"    Price: {prop['price']}, Location: {prop['location']}")
            print(f"    URL: {prop['url'][:100]}...")
        
        monitor.cleanup()
        
    except Exception as e:
        print(f"Error testing property monitor: {e}")
        logging.error(f"Monitor test failed: {e}", exc_info=True)