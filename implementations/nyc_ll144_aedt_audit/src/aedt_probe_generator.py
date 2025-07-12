#!/usr/bin/env python3
"""
AEDT Probe Generator for NYC Local Law 144 Audits.

This module generates synthetic employment applications with controlled variations
in protected characteristics for auditing Automated Employment Decision Tools (AEDTs).
"""

import json
import logging
import os
import random
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import faker

# Configure logging
logger = logging.getLogger(__name__)

# Define constants
TEMPLATE_DIR = Path(__file__).parent.parent / "templates"
RESUME_TEMPLATES_DIR = TEMPLATE_DIR / "resume_templates"
APPLICATION_TEMPLATES_DIR = TEMPLATE_DIR / "application_templates"
COVER_LETTER_TEMPLATES_DIR = TEMPLATE_DIR / "cover_letter_templates"

# Define data structures
@dataclass
class Probe:
    """Represents a synthetic employment application probe."""
    
    id: str
    job_type: str
    template_type: str
    variation: str
    content: Dict
    pair_id: str
    
    def to_dict(self) -> Dict:
        """Convert probe to dictionary."""
        return {
            "id": self.id,
            "job_type": self.job_type,
            "template_type": self.template_type,
            "variation": self.variation,
            "content": self.content,
            "pair_id": self.pair_id
        }


class AEDTProbeGenerator:
    """Generates synthetic employment applications for AEDT auditing."""
    
    def __init__(
        self,
        job_types: List[str],
        protected_characteristics: Dict[str, bool],
        control_variables: Dict[str, Union[str, int, float]]
    ):
        """Initialize the probe generator.
        
        Args:
            job_types: List of job types to generate probes for
            protected_characteristics: Dict of protected characteristics to test
            control_variables: Dict of variables to control across probes
        """
        self.job_types = job_types
        self.protected_characteristics = protected_characteristics
        self.control_variables = control_variables
        self.fake = faker.Faker()
        
        # Load templates
        self.resume_templates = self._load_templates(RESUME_TEMPLATES_DIR)
        self.application_templates = self._load_templates(APPLICATION_TEMPLATES_DIR)
        self.cover_letter_templates = self._load_templates(COVER_LETTER_TEMPLATES_DIR)
        
        # Load name databases
        self.name_data = self._load_name_data()
        
        logger.info(f"Initialized AEDTProbeGenerator with {len(self.job_types)} job types")
    
    def _load_templates(self, template_dir: Path) -> Dict[str, Dict]:
        """Load templates from directory.
        
        Args:
            template_dir: Directory containing templates
            
        Returns:
            Dict mapping job types to templates
        """
        templates = {}
        
        # Create directory if it doesn't exist (for initial setup)
        if not template_dir.exists():
            template_dir.mkdir(parents=True)
            logger.warning(f"Created template directory: {template_dir}")
            return templates
        
        for job_type in self.job_types:
            job_type_dir = template_dir / job_type
            if not job_type_dir.exists():
                continue
                
            templates[job_type] = {}
            for template_file in job_type_dir.glob("*.json"):
                with open(template_file, 'r') as f:
                    templates[job_type][template_file.stem] = json.load(f)
        
        return templates
    
    def _load_name_data(self) -> Dict[str, Dict[str, List[str]]]:
        """Load name databases for different demographic groups.
        
        Returns:
            Dict mapping demographic groups to name types to name lists
        """
        name_data_path = TEMPLATE_DIR / "name_data.json"
        
        # Create a basic name database if it doesn't exist
        if not name_data_path.exists():
            basic_name_data = {
                "race_ethnicity": {
                    "white": {
                        "first_names": ["James", "John", "Robert", "Michael", "William", "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth"],
                        "last_names": ["Smith", "Johnson", "Williams", "Jones", "Brown"]
                    },
                    "black": {
                        "first_names": ["DeShawn", "DeAndre", "Marquis", "Darnell", "Terrell", "Lakisha", "Latoya", "Tanisha", "Latonya", "Keisha"],
                        "last_names": ["Washington", "Jefferson", "Jackson", "Banks", "Booker"]
                    },
                    "hispanic": {
                        "first_names": ["Jose", "Luis", "Carlos", "Juan", "Miguel", "Maria", "Ana", "Carmen", "Gloria", "Lucia"],
                        "last_names": ["Garcia", "Rodriguez", "Martinez", "Hernandez", "Lopez"]
                    },
                    "asian": {
                        "first_names": ["Wei", "Jin", "Yong", "Ming", "Jie", "Yan", "Li", "Hui", "Xiu", "Mei"],
                        "last_names": ["Wang", "Li", "Zhang", "Chen", "Liu"]
                    }
                },
                "sex_gender": {
                    "male": {
                        "first_names": ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles"],
                        "pronouns": ["he/him", "he/his"]
                    },
                    "female": {
                        "first_names": ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen"],
                        "pronouns": ["she/her", "she/hers"]
                    }
                }
            }
            
            # Create directory if it doesn't exist
            name_data_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(name_data_path, 'w') as f:
                json.dump(basic_name_data, f, indent=2)
            
            logger.warning(f"Created basic name database at {name_data_path}")
            return basic_name_data
        
        with open(name_data_path, 'r') as f:
            return json.load(f)
    
    def _validate_ethical_considerations(self, variations: Dict[str, Dict]) -> bool:
        """Validate ethical considerations for probe generation.
        
        Args:
            variations: Dict mapping variation names to variation data
            
        Returns:
            True if ethical considerations are met, False otherwise
        """
        # This is a placeholder for a more comprehensive ethical review
        # In a real implementation, this would include checks for:
        # - Stereotypical associations
        # - Offensive content
        # - Unrealistic scenarios
        # - Other ethical concerns
        
        logger.info("Validating ethical considerations for probe generation")
        return True
    
    def generate_variations(self, job_type: str) -> Dict[str, Dict]:
        """Generate variations for a job type based on protected characteristics.
        
        Args:
            job_type: Job type to generate variations for
            
        Returns:
            Dict mapping variation names to variation data
        """
        variations = {}
        
        # Generate variations based on race/ethnicity
        if self.protected_characteristics.get("race_ethnicity", False):
            for race in self.name_data["race_ethnicity"]:
                first_names = self.name_data["race_ethnicity"][race]["first_names"]
                last_names = self.name_data["race_ethnicity"][race]["last_names"]
                
                variations[f"race_{race}"] = {
                    "personal_info": {
                        "first_name": random.choice(first_names),
                        "last_name": random.choice(last_names),
                        "race_ethnicity": race
                    }
                }
        
        # Generate variations based on sex/gender
        if self.protected_characteristics.get("sex_gender", False):
            for gender in self.name_data["sex_gender"]:
                first_names = self.name_data["sex_gender"][gender]["first_names"]
                pronouns = self.name_data["sex_gender"][gender]["pronouns"]
                
                variations[f"gender_{gender}"] = {
                    "personal_info": {
                        "first_name": random.choice(first_names),
                        "gender": gender,
                        "pronouns": random.choice(pronouns)
                    }
                }
        
        # Generate intersectional variations
        if (self.protected_characteristics.get("race_ethnicity", False) and 
            self.protected_characteristics.get("sex_gender", False) and
            self.protected_characteristics.get("intersectional", False)):
            
            for race in self.name_data["race_ethnicity"]:
                for gender in self.name_data["sex_gender"]:
                    # For intersectional variations, we need to be careful about name selection
                    # to ensure they are culturally appropriate for the intersection
                    if gender == "male":
                        first_names = [name for name in self.name_data["race_ethnicity"][race]["first_names"] 
                                      if name in self.name_data["sex_gender"]["male"]["first_names"]]
                        if not first_names:  # Fallback if no intersection
                            first_names = self.name_data["race_ethnicity"][race]["first_names"][:5]  # Use first 5 as male
                    else:
                        first_names = [name for name in self.name_data["race_ethnicity"][race]["first_names"] 
                                      if name in self.name_data["sex_gender"]["female"]["first_names"]]
                        if not first_names:  # Fallback if no intersection
                            first_names = self.name_data["race_ethnicity"][race]["first_names"][5:]  # Use last 5 as female
                    
                    last_names = self.name_data["race_ethnicity"][race]["last_names"]
                    pronouns = self.name_data["sex_gender"][gender]["pronouns"]
                    
                    variations[f"intersect_{race}_{gender}"] = {
                        "personal_info": {
                            "first_name": random.choice(first_names) if first_names else random.choice(self.name_data["race_ethnicity"][race]["first_names"]),
                            "last_name": random.choice(last_names),
                            "race_ethnicity": race,
                            "gender": gender,
                            "pronouns": random.choice(pronouns)
                        }
                    }
        
    def generate_probes(self, num_pairs: int) -> List[Probe]:
        """Generate probe pairs for AEDT auditing.
        
        Args:
            num_pairs: Number of probe pairs to generate
            
        Returns:
            List of probes
        """
        probes = []
        
        for _ in range(num_pairs):
            # Select a random job type
            job_type = random.choice(self.job_types)
            
            # Generate variations for the job type
            variations = self.generate_variations(job_type)
            
            # Select two random variations for comparison
            variation_names = list(variations.keys())
            if len(variation_names) < 2:
                logger.warning(f"Not enough variations for job type {job_type}, skipping")
                continue
                
            variation_pair = random.sample(variation_names, 2)
            pair_id = str(uuid.uuid4())
            
            # Create a probe for each variation in the pair
            for variation_name in variation_pair:
                variation_data = variations[variation_name]
                
                # Combine variation data with control variables
                content = {
                    "personal_info": variation_data["personal_info"],
                    "job_type": job_type,
                    "control_variables": self.control_variables
                }
                
                # Add education information
                content["education"] = {
                    "degree": self.control_variables.get("education", "bachelor_degree"),
                    "institution": self.fake.university(),
                    "graduation_year": self.fake.year(),
                    "gpa": round(random.uniform(3.0, 4.0), 2)
                }
                
                # Add experience information
                content["experience"] = {
                    "years": self.control_variables.get("years_experience", 5),
                    "current_title": f"{job_type.replace('_', ' ').title()}",
                    "current_company": self.fake.company(),
                    "skills": self._generate_skills(job_type)
                }
                
                # Create the probe
                probe = Probe(
                    id=str(uuid.uuid4()),
                    job_type=job_type,
                    template_type="application",  # Default to application, could be resume or cover_letter
                    variation=variation_name,
                    content=content,
                    pair_id=pair_id
                )
                
                probes.append(probe)
        
        logger.info(f"Generated {len(probes)} probes ({num_pairs} pairs)")
        return probes
    
    def _generate_skills(self, job_type: str) -> List[str]:
        """Generate skills for a job type.
        
        Args:
            job_type: Job type to generate skills for
            
        Returns:
            List of skills
        """
        # This is a placeholder for a more comprehensive skill generation system
        # In a real implementation, this would be based on job type and other factors
        
        skills_by_job = {
            "software_engineer": [
                "Python", "JavaScript", "Java", "C++", "SQL", "Git", "Docker", "Kubernetes",
                "AWS", "Azure", "React", "Node.js", "Django", "Flask", "TensorFlow"
            ],
            "data_scientist": [
                "Python", "R", "SQL", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
                "Pandas", "NumPy", "Scikit-learn", "Data Visualization", "Statistics", "A/B Testing"
            ],
            "marketing_specialist": [
                "Digital Marketing", "Social Media", "Content Creation", "SEO", "SEM", "Google Analytics",
                "Email Marketing", "Campaign Management", "Market Research", "Brand Strategy"
            ],
            "customer_service_representative": [
                "Communication", "Problem Solving", "Patience", "Empathy", "CRM Software",
                "Conflict Resolution", "Time Management", "Product Knowledge", "Active Listening"
            ]
        }
        
        default_skills = ["Communication", "Teamwork", "Problem Solving", "Time Management", "Adaptability"]
        job_specific_skills = skills_by_job.get(job_type, [])
        
        # Select a random subset of skills
        num_skills = random.randint(5, 10)
        all_skills = default_skills + job_specific_skills
        
        if len(all_skills) <= num_skills:
            return all_skills
        
        return random.sample(all_skills, num_skills)


if __name__ == "__main__":
    # Simple demonstration
    logging.basicConfig(level=logging.INFO)
    
    generator = AEDTProbeGenerator(
        job_types=["software_engineer", "data_scientist"],
        protected_characteristics={"race_ethnicity": True, "sex_gender": True, "intersectional": True},
        control_variables={"education": "bachelor_degree", "years_experience": 5}
    )
    
    probes = generator.generate_probes(2)
    
    for probe in probes:
        print(f"Probe ID: {probe.id}")
        print(f"Job Type: {probe.job_type}")
        print(f"Variation: {probe.variation}")
        print(f"Content: {json.dumps(probe.content, indent=2)}")
        print("---")