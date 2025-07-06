"""
Tests for Application Generator
"""

import unittest
import tempfile
import os
from src.application_generator import ApplicationGenerator


class TestApplicationGenerator(unittest.TestCase):
    
    def setUp(self):
        # Create temporary template files
        self.temp_dir = tempfile.mkdtemp()
        
        # Mohammed template
        mohammed_template = """Sehr geehrte Damen und Herren,

mit großem Interesse habe ich Ihre Anzeige für die Immobilie auf Immobilienscout24 gesehen. Ich bin Mohammed Abasi, ein verantwortungsbewusster und zuverlässiger Mieter.

Mit freundlichen Grüßen,
Mohammed Abasi"""
        
        with open(os.path.join(self.temp_dir, 'mohammed_application.txt'), 'w', encoding='utf-8') as f:
            f.write(mohammed_template)
        
        # Franz template with placeholder
        franz_template = """Sehr geehrte Damen und Herren,

Die Beschreibung der Wohnung hat mein Interesse geweckt, insbesondere {property_detail}.

Mit freundlichen Grüßen,
Franz Müller"""
        
        with open(os.path.join(self.temp_dir, 'franz_application.txt'), 'w', encoding='utf-8') as f:
            f.write(franz_template)
        
        # Test configuration
        self.config = {
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
        
        self.generator = ApplicationGenerator(self.config, self.temp_dir)
    
    def tearDown(self):
        # Clean up temporary files
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_template_loading(self):
        """Test that templates are loaded correctly."""
        self.assertIn('mohammed_abasi', self.generator.templates)
        self.assertIn('franz_muller', self.generator.templates)
        self.assertIn('Mohammed Abasi', self.generator.templates['mohammed_abasi'])
        self.assertIn('{property_detail}', self.generator.templates['franz_muller'])
    
    def test_property_detail_extraction(self):
        """Test property detail extraction for Franz's application."""
        property_data = {
            'description': 'Schöne helle Wohnung mit moderner Küche',
            'title': '3-Zimmer-Wohnung in Berlin'
        }
        
        detail = self.generator._extract_property_details(property_data)
        self.assertIn('Küche', detail)
    
    def test_application_generation_mohammed(self):
        """Test application generation for Mohammed."""
        property_data = {
            'id': 'test_123',
            'url': 'https://test.com/property/123',
            'title': 'Test Property',
            'description': 'Test description'
        }
        
        application = self.generator.generate_application('mohammed_abasi', property_data)
        
        self.assertIsNotNone(application)
        self.assertEqual(application['persona'], 'mohammed_abasi')
        self.assertEqual(application['applicant_name'], 'Mohammed Abasi')
        self.assertIn('Mohammed Abasi', application['body'])
        self.assertEqual(application['property_id'], 'test_123')
    
    def test_application_generation_franz(self):
        """Test application generation for Franz with property detail substitution."""
        property_data = {
            'id': 'test_456',
            'url': 'https://test.com/property/456',
            'title': 'Modern Apartment',
            'description': 'Apartment with modern kitchen and balcony'
        }
        
        application = self.generator.generate_application('franz_muller', property_data)
        
        self.assertIsNotNone(application)
        self.assertEqual(application['persona'], 'franz_muller')
        self.assertEqual(application['applicant_name'], 'Franz Müller')
        self.assertNotIn('{property_detail}', application['body'])  # Placeholder should be replaced
        self.assertIn('Franz Müller', application['body'])
    
    def test_paired_application_generation(self):
        """Test generation of paired applications."""
        property_data = {
            'id': 'test_789',
            'url': 'https://test.com/property/789',
            'title': 'Test Property',
            'description': 'Beautiful apartment'
        }
        
        applications = self.generator.generate_paired_applications(property_data)
        
        self.assertEqual(len(applications), 2)
        
        personas = [app['persona'] for app in applications]
        self.assertIn('mohammed_abasi', personas)
        self.assertIn('franz_muller', personas)
        
        # Check that both applications reference the same property
        for app in applications:
            self.assertEqual(app['property_id'], 'test_789')
    
    def test_application_validation(self):
        """Test application validation."""
        valid_application = {
            'persona': 'mohammed_abasi',
            'applicant_name': 'Mohammed Abasi',
            'applicant_email': 'mohammed.abasi@test.com',
            'subject': 'Apartment Inquiry',
            'body': 'This is a test application with sufficient content to pass validation checks. It contains enough text to meet the minimum length requirement for proper application validation in our bias testing system.',
            'property_id': 'test_123'
        }
        
        self.assertTrue(self.generator.validate_application(valid_application))
        
        # Test invalid application (missing required field)
        invalid_application = valid_application.copy()
        del invalid_application['applicant_name']
        
        self.assertFalse(self.generator.validate_application(invalid_application))
        
        # Test invalid application (body too short)
        short_body_application = valid_application.copy()
        short_body_application['body'] = 'Too short'
        
        self.assertFalse(self.generator.validate_application(short_body_application))
    
    def test_available_personas(self):
        """Test getting available personas."""
        personas = self.generator.get_available_personas()
        self.assertEqual(set(personas), {'mohammed_abasi', 'franz_muller'})


if __name__ == '__main__':
    unittest.main()