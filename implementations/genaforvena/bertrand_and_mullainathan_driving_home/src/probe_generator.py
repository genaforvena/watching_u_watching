import csv
import random
from faker import Faker

fake = Faker()


def generate_probes(num_pairs, output_file):
    """Creates ethically sanitized probe pairs"""
    with open(output_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['pair_id', 'type', 'name', 'institution', 'email_body'])
        
        for i in range(num_pairs):
            # Anglo probe
            writer.writerow([
                f"pair_{i}",
                "anglo",
                fake.name(),
                "Institution A",
                generate_email("anglo")
            ])
            
            # Minority probe (matched pair)
            writer.writerow([
                f"pair_{i}",
                "minority",
                fake.name(),
                "Institution A",
                generate_email("minority")
            ])


def generate_email(probe_type):
    """Creates grammatically imperfect German inquiries"""
    templates = {
        "anglo": [
            "Guten Tag, ich brauche Hilfe mit Visumantrag.",
            "Können Sie mir sagen welche Dokumente benötigt werden?"
        ],
        "minority": [
            "Hallo, ich brauche Info für Familienzusammenführung.",
            "Welche Papiere muss ich schicken?"
        ]
    }
    return " ".join(random.choice(templates[probe_type]) + "\n\n"

    
if __name__ == "__main__":
    generate_probes(5, "sample_data/pilot_probes.csv")  # Test run
    
