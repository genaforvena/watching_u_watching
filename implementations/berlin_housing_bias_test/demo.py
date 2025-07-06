#!/usr/bin/env python3
"""
Demo Script for Berlin Housing Bias Testing System

This script demonstrates the core functionality without requiring
external web scraping or browser automation.
"""

import json
import tempfile
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from pii_redactor import PIIRedactor, create_redactor_from_config
from application_generator import ApplicationGenerator, create_generator_from_config


def demo_pii_redaction():
    """Demonstrate PII redaction functionality."""
    print("=== PII REDACTION DEMO ===")
    print()
    
    redactor = PIIRedactor()
    
    # Test email data
    test_email = {
        'subject': 'Re: Bewerbung um die Wohnung in Berlin-Mitte',
        'sender_name': 'Hans Müller',
        'sender_email': 'hans.mueller@example-real-estate.de',
        'body': '''Sehr geehrter Herr Abasi,

vielen Dank für Ihre Bewerbung um die 3-Zimmer-Wohnung in der Müllerstraße 123.

Wir haben Ihre Unterlagen erhalten und werden uns in den nächsten Tagen bei Ihnen melden.

Mit freundlichen Grüßen,
Hans Müller
Müller Immobilien GmbH
Tel: +49 30 12345678''',
        'timestamp': '2024-07-06T14:30:00Z',
        'property_id': 'prop_12345'
    }
    
    print("Original email content:")
    print(f"Subject: {test_email['subject']}")
    print(f"From: {test_email['sender_name']} <{test_email['sender_email']}>")
    print(f"Body:\n{test_email['body']}")
    print()
    
    # Redact the email
    redacted_email = redactor.redact_email_content(test_email)
    
    print("After PII redaction:")
    print(f"Subject: {redacted_email['subject']}")
    print(f"From: {redacted_email['sender_name']} <{redacted_email['sender_email']}>")
    print(f"Body:\n{redacted_email['body']}")
    print()
    
    # Show verification
    print("Verification:")
    print(f"Original subject length: {len(test_email['subject'])}")
    print(f"Redacted subject length: {len(redacted_email['subject'])}")
    print(f"Length preserved: {len(test_email['subject']) == len(redacted_email['subject'])}")
    print(f"No PII remains: {redactor.verify_redaction(test_email['subject'], redacted_email['subject'])}")
    print()


def demo_application_generation():
    """Demonstrate application generation functionality."""
    print("=== APPLICATION GENERATION DEMO ===")
    print()
    
    # Create temporary templates
    temp_dir = Path(tempfile.mkdtemp())
    templates_dir = temp_dir / 'templates'
    templates_dir.mkdir()
    
    # Use actual templates from the issue
    mohammed_template = """Sehr geehrte Damen und Herren,

mit großem Interesse habe ich Ihre Anzeige für die Immobilie auf Immobilienscout24 gesehen. Ich bin Mohammed Abasi, ein verantwortungsbewusster und zuverlässiger Mieter, der aktuell auf der Suche nach einer passenden Wohnung in dieser Gegend ist.

Ich bin fest angestellt und verfüge über ein stabiles Einkommen, das die Mietzahlungen problemlos deckt. Meine Schufa-Auskunft ist einwandfrei, und ich kann Ihnen gerne weitere Nachweise meiner Bonität zur Verfügung stellen.

Die Lage und die Ausstattung der Wohnung sprechen mich sehr an. Ich bin eine ruhige Person, pflege meine Umgebung und bin an einem langfristigen Mietverhältnis interessiert.

Gerne stehe ich Ihnen für einen Besichtigungstermin zur Verfügung und freue mich auf Ihre baldige Rückmeldung.

Mit freundlichen Grüßen,

Mohammed Abasi"""
    
    franz_template = """Sehr geehrte Damen und Herren,

bezüglich Ihrer attraktiven Immobilienanzeige auf Immobilienscout24 möchte ich mich Ihnen als potenzieller Mieter vorstellen. Mein Name ist Franz Müller, und ich suche eine neue Bleibe, die meinen Bedürfnissen entspricht.

Als Angestellter in einer stabilen Position biete ich Ihnen die Gewissheit regelmäßiger und pünktlicher Mietzahlungen. Alle erforderlichen Unterlagen zur Bonitätsprüfung, einschließlich einer positiven Schufa-Auskunft, sind selbstverständlich vorhanden.

Die Beschreibung der Wohnung hat mein Interesse geweckt, insbesondere {property_detail}. Ich bin ein ordentlicher und unkomplizierter Mieter und strebe ein dauerhaftes Mietverhältnis an.

Ich würde mich freuen, die Wohnung persönlich besichtigen zu können und erwarte gespannt Ihre Antwort.

Mit freundlichen Grüßen,

Franz Müller"""
    
    # Write templates
    (templates_dir / 'mohammed_application.txt').write_text(mohammed_template, encoding='utf-8')
    (templates_dir / 'franz_application.txt').write_text(franz_template, encoding='utf-8')
    
    # Configuration
    config = {
        'applications': {
            'templates': {
                'mohammed_abasi': {
                    'name': 'Mohammed Abasi',
                    'email': 'mohammed.abasi.applications@example.com',
                    'template_path': 'mohammed_application.txt'
                },
                'franz_muller': {
                    'name': 'Franz Müller',
                    'email': 'franz.muller.applications@example.com',
                    'template_path': 'franz_application.txt'
                }
            }
        }
    }
    
    # Test property
    property_data = {
        'id': 'demo_prop_123',
        'url': 'https://www.immobilienscout24.de/expose/123456789',
        'title': '3-Zimmer-Wohnung in Berlin-Mitte mit Balkon',
        'description': 'Schöne helle Wohnung mit moderner Küche, Balkon und guter Verkehrsanbindung in zentraler Lage',
        'price': '1.800 € Kaltmiete',
        'location': 'Berlin-Mitte, Hackescher Markt',
        'rooms': '3 Zimmer',
        'area': '85 m²'
    }
    
    print(f"Property: {property_data['title']}")
    print(f"Location: {property_data['location']}")
    print(f"Price: {property_data['price']}")
    print(f"Description: {property_data['description']}")
    print()
    
    # Generate applications
    generator = ApplicationGenerator(config['applications']['templates'], str(templates_dir))
    applications = generator.generate_paired_applications(property_data)
    
    print(f"Generated {len(applications)} applications:")
    print()
    
    for i, app in enumerate(applications, 1):
        print(f"APPLICATION {i}: {app['persona'].upper()}")
        print("-" * 50)
        print(f"From: {app['applicant_name']} <{app['applicant_email']}>")
        print(f"Subject: {app['subject']}")
        print(f"Body:\n{app['body']}")
        print()
    
    # Clean up
    import shutil
    shutil.rmtree(temp_dir)


def demo_bias_detection_concept():
    """Demonstrate the bias detection concept."""
    print("=== BIAS DETECTION CONCEPT DEMO ===")
    print()
    
    print("This system implements paired testing methodology to detect bias:")
    print()
    print("1. CONTROLLED VARIABLES:")
    print("   - Same property")
    print("   - Same application content (except name)")
    print("   - Same submission timing")
    print("   - Same contact information format")
    print()
    print("2. SINGLE VARIABLE TESTED:")
    print("   - Applicant name (Mohammed Abasi vs Franz Müller)")
    print()
    print("3. MEASURED OUTCOMES:")
    print("   - Response rate (who gets responses)")
    print("   - Response timing (who gets faster responses)")
    print("   - Response content (quality/tone differences)")
    print()
    print("4. PRIVACY PROTECTION:")
    print("   - All received emails immediately redacted")
    print("   - Original PII never stored")
    print("   - Word length preserved for analysis")
    print()
    print("5. STATISTICAL ANALYSIS:")
    print("   - Response rate comparison")
    print("   - Response time analysis")
    print("   - Pattern detection across multiple properties")
    print()
    
    # Simulate some analysis results
    print("EXAMPLE ANALYSIS RESULTS:")
    print("-" * 30)
    print("Properties tested: 50")
    print("Mohammed responses: 12 (24%)")
    print("Franz responses: 28 (56%)")
    print("Response ratio: 0.43 (Mohammed/Franz)")
    print()
    print("BIAS INDICATOR: HIGH")
    print("Mohammed receives significantly fewer responses (43% of Franz's rate)")
    print("This pattern suggests potential discrimination based on name/perceived ethnicity")
    print()


def main():
    """Run all demos."""
    print("BERLIN HOUSING MARKET BIAS TESTING SYSTEM DEMO")
    print("=" * 60)
    print()
    print("This demo shows the core functionality of our automated")
    print("paired testing system for detecting housing discrimination.")
    print()
    
    try:
        demo_pii_redaction()
        demo_application_generation()
        demo_bias_detection_concept()
        
        print("Demo completed successfully!")
        print()
        print("To run the full system:")
        print("1. Copy config.example.json to config.json")
        print("2. Adjust configuration settings")
        print("3. Run: python src/main.py --mode once --dry-run")
        print()
        print("For analysis:")
        print("python src/analyze_responses.py --db data/housing_bias_test.db")
        
    except Exception as e:
        print(f"Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()