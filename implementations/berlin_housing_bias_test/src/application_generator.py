"""
Application Generator for Berlin Housing Bias Testing

This module generates rental applications using predefined German templates
for two personas: Mohammed Abasi and Franz Müller.

No LLM generation is used - all applications are based on static templates
as specified in the requirements.
"""

import os
import random
from typing import Dict, List, Optional
from datetime import datetime
import logging


class ApplicationGenerator:
    """
    Generates rental applications using predefined templates for paired testing.
    """
    
    def __init__(self, templates_config: Dict, templates_dir: str = "templates"):
        """
        Initialize the application generator.
        
        Args:
            templates_config: Configuration for templates and personas
            templates_dir: Directory containing template files
        """
        self.templates_config = templates_config
        self.templates_dir = templates_dir
        self.templates = {}
        self._load_templates()
        
    def _load_templates(self):
        """Load application templates from files."""
        for persona_key, persona_config in self.templates_config.items():
            template_path = persona_config.get('template_path')
            if template_path:
                full_path = os.path.join(self.templates_dir, os.path.basename(template_path))
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        self.templates[persona_key] = f.read().strip()
                    logging.info(f"Loaded template for {persona_key} from {full_path}")
                except FileNotFoundError:
                    logging.error(f"Template file not found: {full_path}")
                    raise
                except Exception as e:
                    logging.error(f"Error loading template {full_path}: {e}")
                    raise
    
    def _extract_property_details(self, property_data: Dict) -> str:
        """
        Extract a relevant detail from property data for Franz's application.
        
        Args:
            property_data: Dictionary containing property information
            
        Returns:
            A suitable property detail string
        """
        # List of possible property features to highlight
        possible_details = [
            "die Helligkeit der Räume",
            "die moderne Küche", 
            "die gute Verkehrsanbindung",
            "die ruhige Lage",
            "der Balkon",
            "die Ausstattung",
            "die Größe der Wohnung",
            "die zentrale Lage",
            "das moderne Bad",
            "die Parkmöglichkeiten"
        ]
        
        # Try to match property features to details
        description = property_data.get('description', '').lower()
        title = property_data.get('title', '').lower()
        combined_text = f"{title} {description}"
        
        # Look for specific features mentioned in the property
        if 'balkon' in combined_text:
            return "der Balkon"
        elif any(word in combined_text for word in ['küche', 'einbauküche', 'modern']):
            return "die moderne Küche"
        elif any(word in combined_text for word in ['hell', 'licht', 'sonnig']):
            return "die Helligkeit der Räume"
        elif any(word in combined_text for word in ['verkehr', 'u-bahn', 's-bahn', 'bus']):
            return "die gute Verkehrsanbindung"
        elif any(word in combined_text for word in ['ruhig', 'leise']):
            return "die ruhige Lage"
        elif any(word in combined_text for word in ['zentral', 'zentrum', 'mitte']):
            return "die zentrale Lage"
        elif any(word in combined_text for word in ['bad', 'badezimmer', 'dusche']):
            return "das moderne Bad"
        elif any(word in combined_text for word in ['parkplatz', 'garage', 'stellplatz']):
            return "die Parkmöglichkeiten"
        else:
            # Default to a generic but appropriate choice
            return random.choice([
                "die Ausstattung",
                "die Größe der Wohnung", 
                "die Lage"
            ])
    
    def generate_application(self, persona: str, property_data: Dict) -> Optional[Dict]:
        """
        Generate an application for a specific persona and property.
        
        Args:
            persona: The persona to generate for ('mohammed_abasi' or 'franz_muller')
            property_data: Property information dictionary
            
        Returns:
            Dictionary containing application data or None if error
        """
        if persona not in self.templates:
            logging.error(f"No template found for persona: {persona}")
            return None
            
        if persona not in self.templates_config:
            logging.error(f"No configuration found for persona: {persona}")
            return None
            
        template = self.templates[persona]
        persona_config = self.templates_config[persona]
        
        # For Franz's template, we need to replace the property detail placeholder
        if persona == 'franz_muller' and '{property_detail}' in template:
            property_detail = self._extract_property_details(property_data)
            application_text = template.replace('{property_detail}', property_detail)
        else:
            application_text = template
            
        # Create application data
        application = {
            'persona': persona,
            'applicant_name': persona_config.get('name'),
            'applicant_email': persona_config.get('email'),
            'subject': f"Bewerbung um die Wohnung - {property_data.get('title', 'Immobilienanzeige')}",
            'body': application_text,
            'property_id': property_data.get('id'),
            'property_url': property_data.get('url'),
            'property_title': property_data.get('title'),
            'generated_at': datetime.now().isoformat(),
            'template_used': persona
        }
        
        logging.info(f"Generated application for {persona} for property {property_data.get('id')}")
        return application
    
    def generate_paired_applications(self, property_data: Dict) -> List[Dict]:
        """
        Generate paired applications for both personas for the same property.
        
        Args:
            property_data: Property information dictionary
            
        Returns:
            List of application dictionaries for both personas
        """
        applications = []
        
        # Generate applications for both personas
        for persona in ['mohammed_abasi', 'franz_muller']:
            app = self.generate_application(persona, property_data)
            if app:
                applications.append(app)
        
        if len(applications) == 2:
            logging.info(f"Generated paired applications for property {property_data.get('id')}")
        else:
            logging.warning(f"Could only generate {len(applications)} applications for property {property_data.get('id')}")
            
        return applications
    
    def validate_application(self, application: Dict) -> bool:
        """
        Validate that an application contains all required fields.
        
        Args:
            application: Application dictionary to validate
            
        Returns:
            True if application is valid
        """
        required_fields = [
            'persona', 'applicant_name', 'applicant_email',
            'subject', 'body', 'property_id'
        ]
        
        for field in required_fields:
            if field not in application or not application[field]:
                logging.error(f"Application missing required field: {field}")
                return False
                
        # Check that body contains actual content
        if len(application['body'].strip()) < 100:
            logging.error("Application body is too short")
            return False
            
        return True
    
    def get_available_personas(self) -> List[str]:
        """Get list of available personas."""
        return list(self.templates.keys())


def create_generator_from_config(config: Dict) -> ApplicationGenerator:
    """
    Create an application generator from configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configured ApplicationGenerator instance
    """
    app_config = config.get('applications', {})
    templates_config = app_config.get('templates', {})
    
    return ApplicationGenerator(templates_config)


# Example usage and testing
if __name__ == "__main__":
    # Test configuration
    test_config = {
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
        }
    }
    
    # Test property data
    test_property = {
        'id': 'test_prop_123',
        'url': 'https://www.immobilienscout24.de/expose/123',
        'title': '3-Zimmer-Wohnung in Berlin-Mitte',
        'description': 'Schöne helle Wohnung mit moderner Küche und Balkon in zentraler Lage'
    }
    
    try:
        generator = create_generator_from_config(test_config)
        
        # Generate paired applications
        applications = generator.generate_paired_applications(test_property)
        
        print(f"Generated {len(applications)} applications:")
        for app in applications:
            print(f"\nPersona: {app['persona']}")
            print(f"Subject: {app['subject']}")
            print(f"Body: {app['body'][:100]}...")
            print(f"Valid: {generator.validate_application(app)}")
            
    except Exception as e:
        print(f"Error testing application generator: {e}")
        print("Make sure template files exist in the templates directory")