#!/usr/bin/env python3
"""
PII Redactor for NYC Local Law 144 Audits.

This module handles the redaction of personally identifiable information (PII)
from responses to ensure privacy and compliance with data protection regulations.
"""

import logging
import random
import re
from typing import Dict, List, Optional, Tuple, Union

# Configure logging
logger = logging.getLogger(__name__)


class PIIRedactor:
    """Handles the redaction of personally identifiable information (PII)."""
    
    def __init__(self):
        """Initialize the PII redactor."""
        # Define PII patterns
        self.pii_patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "address": r'\b\d+\s+[A-Za-z0-9\s,]+(?:street|st|avenue|ave|road|rd|highway|hwy|square|sq|trail|trl|drive|dr|court|ct|parkway|pkwy|circle|cir|boulevard|blvd)\b',
            "name": r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
        }
        
        logger.info("Initialized PIIRedactor")
    
    def redact_text(self, text: str) -> str:
        """Redact PII from text.
        
        Args:
            text: Text to redact
            
        Returns:
            Redacted text
        """
        if not text:
            return ""
        
        redacted_text = text
        
        # Apply redaction for each PII pattern
        for pii_type, pattern in self.pii_patterns.items():
            redacted_text = re.sub(pattern, f"[REDACTED {pii_type.upper()}]", redacted_text, flags=re.IGNORECASE)
        
        return redacted_text
    
    def redact_dict(self, data: Dict) -> Dict:
        """Redact PII from a dictionary.
        
        Args:
            data: Dictionary to redact
            
        Returns:
            Redacted dictionary
        """
        redacted_data = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                redacted_data[key] = self.redact_text(value)
            elif isinstance(value, dict):
                redacted_data[key] = self.redact_dict(value)
            elif isinstance(value, list):
                redacted_data[key] = [
                    self.redact_dict(item) if isinstance(item, dict) else
                    self.redact_text(item) if isinstance(item, str) else
                    item
                    for item in value
                ]
            else:
                redacted_data[key] = value
        
        return redacted_data
    
    def process_response_content(self, content: str) -> Dict:
        """Process response content to extract metadata while redacting PII.
        
        Args:
            content: Response content
            
        Returns:
            Dict containing extracted metadata
        """
        # This is a simplified content processing logic
        # In a real implementation, this would be more sophisticated
        
        # Extract metadata
        metadata = {
            "length": len(content),
            "has_response": bool(content.strip()),
            "response_type": self._classify_response_type(content)
        }
        
        # No content is stored, only metadata
        return metadata
    
    def _classify_response_type(self, content: str) -> str:
        """Classify the response type based on content.
        
        Args:
            content: Response content
            
        Returns:
            Response type
        """
        content_lower = content.lower()
        
        if re.search(r'interview|proceed|next step|selected|congratulations', content_lower):
            return "positive"
        elif re.search(r'reject|decline|unfortunately|not proceed|not selected', content_lower):
            return "negative"
        else:
            return "neutral"
    
    def demonstrate_redaction(self, text: str) -> Dict:
        """Demonstrate redaction for educational purposes only.
        
        This method is for demonstration only and should not be used in production.
        It shows how redaction works without storing the original or redacted text.
        
        Args:
            text: Text to redact
            
        Returns:
            Dict containing redaction statistics
        """
        if not text:
            return {"valid": False, "reason": "Empty text"}
        
        # Count PII instances
        pii_counts = {}
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            pii_counts[pii_type] = len(matches)
        
        # Redact text
        redacted_text = self.redact_text(text)
        
        # Calculate statistics
        stats = {
            "original_length": len(text),
            "redacted_length": len(redacted_text),
            "pii_instances": sum(pii_counts.values()),
            "pii_types_found": [pii_type for pii_type, count in pii_counts.items() if count > 0]
        }
        
        # Immediately discard both original and redacted text
        del text
        del redacted_text
        
        return stats


if __name__ == "__main__":
    # Simple demonstration
    logging.basicConfig(level=logging.INFO)
    
    redactor = PIIRedactor()
    
    # Example text with PII
    example_text = """
    Hello John Smith,
    
    Thank you for your application. We received your submission from john.smith@example.com.
    
    Please call us at (555) 123-4567 to schedule an interview.
    
    Our office is located at 123 Main Street, New York, NY 10001.
    
    Best regards,
    Recruitment Team
    """
    
    # Demonstrate redaction
    stats = redactor.demonstrate_redaction(example_text)
    
    print("PII Redaction Statistics:")
    print(f"Original Length: {stats['original_length']} characters")
    print(f"Redacted Length: {stats['redacted_length']} characters")
    print(f"PII Instances Found: {stats['pii_instances']}")
    print(f"PII Types Found: {', '.join(stats['pii_types_found'])}")
    
    # Note: Neither the original nor redacted text is stored or displayed