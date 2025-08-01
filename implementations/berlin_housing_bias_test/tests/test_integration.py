"""
Integration Tests for Berlin Housing Bias Testing System
"""

import unittest
import tempfile
import json
import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from pii_redactor import create_redactor_from_config
from application_generator import create_generator_from_config
from data_storage import create_storage_from_config


class TestIntegration(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create test configuration
        self.config = {
            'pii_redaction': {
                'symbol_pool': '!@#$%^&*',
                'preserve_word_boundaries': True,
                'preserve_line_breaks': True,
                'preserve_punctuation': False
            },
            'applications': {
                'templates': {
                    'mohammed_abasi': {
                        'name': 'Mohammed Abasi',
                        'email': 'mohammed.abasi.test@example.com',
                        'template_path': 'mohammed_application.txt'
                    },
                    'franz_muller': {
                        'name': 'Franz Müller',
                        'email': 'franz.muller.test@example.com',
                        'template_path': 'franz_application.txt'
                    }
                }
            },
            'data_storage': {
                'output_directory': str(self.temp_dir / 'data'),
                'backup_enabled': False,
                'retention_days': 90
            }
        }
        
        # Create templates directory and files
        templates_dir = self.temp_dir / 'templates'
        templates_dir.mkdir()
        
        mohammed_template = """Sehr geehrte Damen und Herren,

mit großem Interesse habe ich Ihre Anzeige gesehen. Ich bin Mohammed Abasi.

Mit freundlichen Grüßen,
Mohammed Abasi"""
        
        (templates_dir / 'mohammed_application.txt').write_text(mohammed_template, encoding='utf-8')
        
        franz_template = """Sehr geehrte Damen und Herren,

Die Wohnung hat mein Interesse geweckt, insbesondere {property_detail}.

Mit freundlichen Grüßen,
Franz Müller"""
        
        (templates_dir / 'franz_application.txt').write_text(franz_template, encoding='utf-8')
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_pii_redaction_integration(self):
        """Test PII redaction integration with email storage."""
        pii_redactor = create_redactor_from_config(self.config)
        
        # Test various email content
        test_emails = [
            {
                'subject': 'Apartment available for viewing',
                'body': 'Dear Mr. Abasi,\n\nThe apartment at Müllerstraße 123 is available.',
                'sender_name': 'Property Manager'
            },
            {
                'subject': 'Unfortunately not available',
                'body': 'Dear Franz,\n\nSorry, but the apartment has been rented.',
                'sender_name': 'Landlord Schmidt'
            }
        ]
        
        for email in test_emails:
            redacted = pii_redactor.redact_email_content(email)
            # All fields should be None (deprecated behavior)
            for v in redacted.values():
                self.assertIsNone(v)


if __name__ == '__main__':
    unittest.main()