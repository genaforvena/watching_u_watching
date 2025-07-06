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
    
    def test_complete_workflow(self):
        """Test the complete workflow from property discovery to data storage."""
        
        # Initialize components
        pii_redactor = create_redactor_from_config(self.config)
        data_storage = create_storage_from_config(self.config, pii_redactor)
        
        # Change to templates directory for application generator
        original_cwd = os.getcwd()
        try:
            os.chdir(self.temp_dir)
            application_generator = create_generator_from_config(self.config)
            
            # Test property data
            property_data = {
                'id': 'test_property_123',
                'url': 'https://www.immobilienscout24.de/test/123',
                'title': '3-Zimmer-Wohnung in Berlin-Mitte',
                'description': 'Schöne helle Wohnung mit moderner Küche und Balkon',
                'price': '1500 €',
                'location': 'Berlin-Mitte',
                'rooms': '3 Zimmer',
                'area': '80 m²',
                'discovered_at': '2024-07-06T10:00:00Z',
                'source': 'immobilienscout24.de'
            }
            
            # 1. Store property
            self.assertTrue(data_storage.store_property(property_data))
            
            # 2. Generate applications
            applications = application_generator.generate_paired_applications(property_data)
            self.assertEqual(len(applications), 2)
            
            # 3. Store applications
            for application in applications:
                self.assertTrue(data_storage.store_application(application))
            
            # 4. Test email response storage with PII redaction
            test_email = {
                'subject': 'Re: Apartment Inquiry',
                'sender_name': 'Hans Müller',
                'sender_email': 'hans.mueller@example.com',
                'body': 'Dear Mohammed,\n\nThank you for your interest in our apartment.',
                'timestamp': '2024-07-06T12:00:00Z'
            }
            
            # Simulate submission first
            submission_result = {
                'submission_id': 'test_submission_123',
                'application': applications[0],
                'timestamp': '2024-07-06T11:00:00Z',
                'success': True,
                'error': None,
                'dry_run': False
            }
            
            self.assertTrue(data_storage.store_submission(submission_result))
            self.assertTrue(data_storage.store_response(test_email, 'test_submission_123'))
            
            # 5. Verify data retrieval
            stored_properties = data_storage.get_properties(limit=10)
            self.assertEqual(len(stored_properties), 1)
            self.assertEqual(stored_properties[0]['id'], 'test_property_123')
            
            stored_applications = data_storage.get_applications('test_property_123')
            self.assertEqual(len(stored_applications), 2)
            
            stored_responses = data_storage.get_responses('test_property_123')
            self.assertEqual(len(stored_responses), 1)
            
            # 6. Verify PII redaction in stored response
            response = stored_responses[0]
            self.assertNotEqual(response['redacted_subject'], test_email['subject'])
            self.assertNotEqual(response['redacted_body'], test_email['body'])
            self.assertEqual(len(response['redacted_subject']), len(test_email['subject']))
            
            # 7. Test bias analysis data retrieval
            analysis_data = data_storage.get_bias_analysis_data()
            self.assertFalse(analysis_data.empty)
            
            # 8. Test statistics
            stats = data_storage.get_statistics()
            self.assertEqual(stats['properties_count'], 1)
            self.assertEqual(stats['applications_count'], 2)
            self.assertEqual(stats['responses_count'], 1)
            
        finally:
            os.chdir(original_cwd)
    
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
            
            # Verify redaction
            self.assertNotEqual(redacted['subject'], email['subject'])
            self.assertNotEqual(redacted['body'], email['body'])
            self.assertNotEqual(redacted['sender_name'], email['sender_name'])
            
            # Verify length preservation
            self.assertEqual(len(redacted['subject']), len(email['subject']))
            self.assertEqual(len(redacted['body']), len(email['body']))
            
            # Verify no PII remains
            self.assertTrue(pii_redactor.verify_redaction(email['subject'], redacted['subject']))
            self.assertTrue(pii_redactor.verify_redaction(email['body'], redacted['body']))


if __name__ == '__main__':
    unittest.main()