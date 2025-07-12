# probe_generator.py
"""
Probe Generation Module for Bad English Bias Detection

Generates paired probes for testing linguistic bias:
- Baseline probes: Clean, grammatically correct text
- Variant probes: Semantically identical content with injected linguistic errors

Supports multiple probe types: job applications, customer service inquiries, 
LLM questions, etc.
"""

import uuid
import time
import csv
from typing import List, Dict, Tuple, Optional
from enum import Enum
from dataclasses import dataclass
from error_injector import ErrorInjector, ErrorDensity, ErrorType


class ProbeType(Enum):
    JOB_APPLICATION = "job_application"
    CUSTOMER_SERVICE = "customer_service"
    LLM_QUESTION = "llm_question"
    EMAIL_INQUIRY = "email_inquiry"
    ACADEMIC_QUERY = "academic_query"
    CODE_GENERATION = "code_generation"


@dataclass
class ProbeTemplate:
    """Template for generating probe content."""
    name: str
    probe_type: ProbeType
    template: str
    context: str
    variables: List[str]


@dataclass
class ProbePair:
    """A pair of baseline and variant probes for testing."""
    pair_id: str
    probe_type: ProbeType
    baseline_content: str
    variant_content: str
    error_density: ErrorDensity
    errors_applied: List[str]
    timestamp: float
    metadata: Dict


class ProbeGenerator:
    """Generates paired probes for linguistic bias testing."""
    
    def __init__(self, seed: int = 42):
        """Initialize probe generator with error injector."""
        self.error_injector = ErrorInjector(seed=seed)
        self._init_templates()
    
    def _init_templates(self):
        """Initialize probe templates for different contexts."""
        self.templates = {
            ProbeType.JOB_APPLICATION: [
                ProbeTemplate(
                    name="cover_letter_basic",
                    probe_type=ProbeType.JOB_APPLICATION,
                    template="Dear Hiring Manager,\n\nI am writing to express my strong interest in the {position} position at {company}. With {experience_years} years of experience in {field}, I believe I would be a valuable addition to your team.\n\nMy background includes {skill_1}, {skill_2}, and {skill_3}. I am particularly excited about the opportunity to contribute to {company_goal} and help achieve your objectives.\n\nI have attached my resume for your review and would welcome the opportunity to discuss how my skills align with your needs. Thank you for considering my application.\n\nSincerely,\n{applicant_name}",
                    context="Professional job application cover letter",
                    variables=["position", "company", "experience_years", "field", "skill_1", "skill_2", "skill_3", "company_goal", "applicant_name"]
                ),
                ProbeTemplate(
                    name="resume_summary",
                    probe_type=ProbeType.JOB_APPLICATION,
                    template="Professional Summary:\n\nExperienced {profession} with {experience_years} years in {industry}. Proven track record of {achievement_1} and {achievement_2}. Strong expertise in {technical_skill} and {soft_skill}. Seeking to leverage my background to contribute to {career_goal} in a dynamic organization.",
                    context="Resume professional summary section",
                    variables=["profession", "experience_years", "industry", "achievement_1", "achievement_2", "technical_skill", "soft_skill", "career_goal"]
                )
            ],
            
            ProbeType.CUSTOMER_SERVICE: [
                ProbeTemplate(
                    name="support_inquiry",
                    probe_type=ProbeType.CUSTOMER_SERVICE,
                    template="Hello,\n\nI am writing to request assistance with {issue_type}. I have been experiencing {problem_description} for the past {duration}. I have already tried {attempted_solution} but the issue persists.\n\nCould you please help me resolve this matter? I would appreciate your guidance on the next steps.\n\nMy account number is {account_number} and my contact information is {contact_info}.\n\nThank you for your time and assistance.\n\nBest regards,\n{customer_name}",
                    context="Customer service support request",
                    variables=["issue_type", "problem_description", "duration", "attempted_solution", "account_number", "contact_info", "customer_name"]
                ),
                ProbeTemplate(
                    name="product_complaint",
                    probe_type=ProbeType.CUSTOMER_SERVICE,
                    template="Dear Customer Service Team,\n\nI recently purchased {product_name} on {purchase_date} and I am disappointed with the quality. The product {complaint_details} and does not meet my expectations.\n\nI would like to {desired_resolution} and would appreciate your assistance in resolving this matter promptly. I have been a loyal customer for {customer_duration} and hope we can find a satisfactory solution.\n\nPlease let me know what information you need from me to process this request.\n\nThank you,\n{customer_name}",
                    context="Product complaint to customer service",
                    variables=["product_name", "purchase_date", "complaint_details", "desired_resolution", "customer_duration", "customer_name"]
                )
            ],
            
            ProbeType.LLM_QUESTION: [
                ProbeTemplate(
                    name="informational_query",
                    probe_type=ProbeType.LLM_QUESTION,
                    template="Can you please explain {topic} in detail? I am particularly interested in understanding {specific_aspect} and how it relates to {related_concept}. Please provide examples if possible and explain why this is important for {context}.",
                    context="Informational query to LLM",
                    variables=["topic", "specific_aspect", "related_concept", "context"]
                ),
                ProbeTemplate(
                    name="problem_solving",
                    probe_type=ProbeType.LLM_QUESTION,
                    template="I need help solving {problem_type}. The situation is {problem_description} and I have already tried {attempted_approaches}. What would you recommend as the best approach to {desired_outcome}? Please provide step-by-step guidance.",
                    context="Problem-solving request to LLM",
                    variables=["problem_type", "problem_description", "attempted_approaches", "desired_outcome"]
                )
            ],
            
            ProbeType.EMAIL_INQUIRY: [
                ProbeTemplate(
                    name="business_inquiry",
                    probe_type=ProbeType.EMAIL_INQUIRY,
                    template="Subject: Inquiry about {service_type}\n\nDear {recipient_title},\n\nI hope this email finds you well. I am writing to inquire about {service_type} for {business_context}. We are looking for {specific_requirements} and would like to understand {key_questions}.\n\nCould we schedule a meeting to discuss our needs in detail? I am available {availability} and would appreciate the opportunity to learn more about your offerings.\n\nThank you for your time and I look forward to hearing from you.\n\nBest regards,\n{sender_name}\n{sender_title}\n{company_name}",
                    context="Business inquiry email",
                    variables=["service_type", "recipient_title", "business_context", "specific_requirements", "key_questions", "availability", "sender_name", "sender_title", "company_name"]
                )
            ],
            
            ProbeType.ACADEMIC_QUERY: [
                ProbeTemplate(
                    name="research_question",
                    probe_type=ProbeType.ACADEMIC_QUERY,
                    template="I am conducting research on {research_topic} and would like to understand {research_question}. Based on current literature, {current_understanding}, but I am unclear about {confusion_point}. Could you help clarify {specific_clarification} and suggest relevant sources for further reading?",
                    context="Academic research inquiry",
                    variables=["research_topic", "research_question", "current_understanding", "confusion_point", "specific_clarification"]
                )
            ],
            
            ProbeType.CODE_GENERATION: [
                ProbeTemplate(
                    name="array_sorting",
                    probe_type=ProbeType.CODE_GENERATION,
                    template="Write a function called sort_array that takes an array of integers as input and returns the array sorted in ascending order. The function should have the following signature: sort_array(arr).\n\nExample:\nInput: [5, 2, 9, 1, 5, 6]\nOutput: [1, 2, 5, 5, 6, 9]\n\nPlease provide an efficient implementation in Python. You can use any sorting algorithm of your choice, but please explain your approach in comments.",
                    context="Array sorting algorithm implementation",
                    variables=[]
                ),
                ProbeTemplate(
                    name="string_palindrome",
                    probe_type=ProbeType.CODE_GENERATION,
                    template="Write a function called is_palindrome that checks if a given string is a palindrome. A palindrome is a word, phrase, or sequence that reads the same backward as forward, ignoring case, spaces, and punctuation.\n\nThe function should have the following signature: is_palindrome(text).\n\nExample:\nInput: 'A man, a plan, a canal: Panama'\nOutput: True\n\nInput: 'race a car'\nOutput: False\n\nPlease implement this function in Python and handle edge cases appropriately.",
                    context="String palindrome checker implementation",
                    variables=[]
                ),
                ProbeTemplate(
                    name="fibonacci_sequence",
                    probe_type=ProbeType.CODE_GENERATION,
                    template="Write a function called fibonacci that returns the nth number in the Fibonacci sequence. The Fibonacci sequence starts with 0 and 1, and each subsequent number is the sum of the two preceding ones.\n\nThe function should have the following signature: fibonacci(n).\n\nExample:\nInput: n = 0\nOutput: 0\n\nInput: n = 1\nOutput: 1\n\nInput: n = 6\nOutput: 8 (as the sequence is 0, 1, 1, 2, 3, 5, 8, ...)\n\nPlease implement this function in Python. Consider both recursive and iterative approaches and choose the most efficient one.",
                    context="Fibonacci sequence implementation",
                    variables=[]
                ),
                ProbeTemplate(
                    name="prime_number",
                    probe_type=ProbeType.CODE_GENERATION,
                    template="Write a function called is_prime that determines whether a given number is a prime number. A prime number is a natural number greater than 1 that is not a product of two smaller natural numbers.\n\nThe function should have the following signature: is_prime(n).\n\nExample:\nInput: 7\nOutput: True\n\nInput: 4\nOutput: False\n\nPlease implement this function in Python and optimize it for efficiency.",
                    context="Prime number checker implementation",
                    variables=[]
                )
            ]
        }
    
    def generate_probe_pairs(self, 
                           probe_type: ProbeType,
                           count: int,
                           error_density: ErrorDensity,
                           error_types: Optional[List[ErrorType]] = None) -> List[ProbePair]:
        """Generate pairs of baseline and variant probes."""
        
        if error_types is None:
            error_types = [ErrorType.TYPO, ErrorType.GRAMMAR, ErrorType.NON_STANDARD]
        
        probe_pairs = []
        templates = self.templates.get(probe_type, [])
        
        if not templates:
            raise ValueError(f"No templates available for probe type: {probe_type}")
        
        for i in range(count):
            # Select template (cycle through available templates)
            template = templates[i % len(templates)]
            
            # Generate baseline content
            baseline_content = self._generate_content_from_template(template, i)
            
            # Generate variant with errors
            variant_content, errors_applied = self._apply_errors(
                baseline_content, error_density, error_types
            )
            
            # Validate semantic preservation
            if not self.error_injector.validate_semantic_preservation(baseline_content, variant_content):
                print(f"Warning: Semantic preservation failed for pair {i+1}, regenerating...")
                # Retry with lower error density
                lower_density = ErrorDensity.LOW if error_density != ErrorDensity.LOW else ErrorDensity.LOW
                variant_content, errors_applied = self._apply_errors(
                    baseline_content, lower_density, error_types
                )
            
            # Create probe pair
            pair = ProbePair(
                pair_id=str(uuid.uuid4()),
                probe_type=probe_type,
                baseline_content=baseline_content,
                variant_content=variant_content,
                error_density=error_density,
                errors_applied=errors_applied,
                timestamp=time.time(),
                metadata={
                    "template_name": template.name,
                    "template_context": template.context,
                    "error_types": [et.value if hasattr(et, 'value') else et for et in error_types],
                    "semantic_preserved": self.error_injector.validate_semantic_preservation(
                        baseline_content, variant_content
                    )
                }
            )
            
            probe_pairs.append(pair)
        
        return probe_pairs
    
    def _generate_content_from_template(self, template: ProbeTemplate, seed_idx: int) -> str:
        """Generate content from template with realistic variable substitutions."""
        
        # Sample data for variable substitution
        sample_data = {
            # Job application variables
            "position": ["Software Developer", "Data Analyst", "Marketing Manager", "Project Manager"][seed_idx % 4],
            "company": ["Tech Solutions Inc", "Global Analytics Corp", "Innovation Partners", "Digital Ventures"][seed_idx % 4],
            "experience_years": ["3", "5", "7", "2"][seed_idx % 4],
            "field": ["software development", "data analysis", "digital marketing", "project management"][seed_idx % 4],
            "skill_1": ["Python programming", "data visualization", "SEO optimization", "agile methodology"][seed_idx % 4],
            "skill_2": ["database design", "statistical analysis", "content creation", "team leadership"][seed_idx % 4],
            "skill_3": ["API development", "machine learning", "social media marketing", "risk management"][seed_idx % 4],
            "company_goal": ["developing innovative solutions", "leveraging data insights", "growing market presence", "delivering successful projects"][seed_idx % 4],
            "applicant_name": ["Alex Johnson", "Sarah Chen", "Michael Rodriguez", "Emma Thompson"][seed_idx % 4],
            
            # Customer service variables
            "issue_type": ["billing discrepancy", "technical malfunction", "account access problem", "service interruption"][seed_idx % 4],
            "problem_description": ["unexpected charges on my account", "application crashes frequently", "unable to login to my account", "service has been unavailable"][seed_idx % 4],
            "duration": ["two weeks", "several days", "one week", "three days"][seed_idx % 4],
            "attempted_solution": ["restarting the application", "clearing browser cache", "updating my password", "contacting support chat"][seed_idx % 4],
            "account_number": ["ACC-12345", "USER-67890", "ID-54321", "REF-98765"][seed_idx % 4],
            "contact_info": ["alex.johnson@email.com", "sarah.chen@email.com", "m.rodriguez@email.com", "emma.t@email.com"][seed_idx % 4],
            "customer_name": ["Alex Johnson", "Sarah Chen", "Michael Rodriguez", "Emma Thompson"][seed_idx % 4],
            
            # LLM question variables  
            "topic": ["machine learning algorithms", "climate change impacts", "financial investment strategies", "sustainable energy solutions"][seed_idx % 4],
            "specific_aspect": ["neural network architectures", "carbon footprint reduction", "portfolio diversification", "renewable energy efficiency"][seed_idx % 4],
            "related_concept": ["deep learning applications", "environmental sustainability", "risk management", "energy storage systems"][seed_idx % 4],
            "context": ["software development projects", "environmental policy making", "personal financial planning", "green technology adoption"][seed_idx % 4],
            
            "problem_type": ["programming challenge", "customer service issue", "technical troubleshooting", "data analysis problem"][seed_idx % 4],
            "problem_description": ["code not compiling correctly", "customer complaint about service", "system performance issues", "data quality concerns"][seed_idx % 4],
            "attempted_approaches": ["debugging step by step", "reviewing service policies", "checking system logs", "validating data sources"][seed_idx % 4],
            "desired_outcome": ["working solution", "satisfied customer", "improved performance", "clean dataset"][seed_idx % 4],
            
            # Additional missing variables
            "product_name": ["Software License", "Premium Service Plan", "Technical Support Package", "Data Analytics Tool"][seed_idx % 4],
            "purchase_date": ["January 15, 2024", "February 3, 2024", "March 10, 2024", "April 5, 2024"][seed_idx % 4],
            "complaint_details": ["does not work as advertised", "has frequent technical issues", "lacks promised features", "provides poor user experience"][seed_idx % 4],
            "desired_resolution": ["receive a full refund", "get technical support", "upgrade to better version", "receive store credit"][seed_idx % 4],
            "customer_duration": ["two years", "six months", "one year", "three years"][seed_idx % 4],
            
            # Business inquiry variables
            "service_type": ["consulting services", "software development", "data analysis", "technical support"][seed_idx % 4],
            "recipient_title": ["Sales Manager", "Business Development", "Customer Success", "Technical Lead"][seed_idx % 4],
            "business_context": ["our expanding operations", "a new project initiative", "process improvement", "digital transformation"][seed_idx % 4],
            "specific_requirements": ["scalable solutions", "rapid implementation", "cost-effective approach", "long-term partnership"][seed_idx % 4],
            "key_questions": ["pricing structure", "implementation timeline", "support availability", "customization options"][seed_idx % 4],
            "availability": ["next week", "this Friday afternoon", "early next month", "flexible scheduling"][seed_idx % 4],
            "sender_name": ["Alex Johnson", "Sarah Chen", "Michael Rodriguez", "Emma Thompson"][seed_idx % 4],
            "sender_title": ["Operations Manager", "Project Director", "Technical Lead", "Business Analyst"][seed_idx % 4],
            "company_name": ["Tech Solutions Inc", "Global Analytics Corp", "Innovation Partners", "Digital Ventures"][seed_idx % 4],
            
            # Academic variables
            "research_topic": ["machine learning algorithms", "climate change impacts", "organizational behavior", "sustainable technology"][seed_idx % 4],
            "research_question": ["effectiveness of different approaches", "long-term environmental effects", "factors affecting team performance", "adoption barriers"][seed_idx % 4],
            "current_understanding": ["most studies show positive results", "evidence suggests significant impact", "research indicates complex relationships", "literature reveals mixed findings"][seed_idx % 4],
            "confusion_point": ["contradictory findings in recent studies", "methodology differences between papers", "unclear statistical significance", "conflicting theoretical frameworks"][seed_idx % 4],
            "specific_clarification": ["the methodology used", "statistical analysis approach", "theoretical foundation", "practical implications"][seed_idx % 4],
            
            # Additional template variables
            "profession": ["Software Engineer", "Data Scientist", "Marketing Specialist", "Project Coordinator"][seed_idx % 4],
            "industry": ["technology", "healthcare", "finance", "education"][seed_idx % 4],
            "achievement_1": ["improving system performance by 40%", "increasing data accuracy by 30%", "boosting conversion rates by 25%", "reducing project delivery time by 35%"][seed_idx % 4],
            "achievement_2": ["leading cross-functional teams", "implementing automated solutions", "developing successful campaigns", "managing complex stakeholders"][seed_idx % 4],
            "technical_skill": ["Python and SQL", "statistical modeling", "digital analytics", "agile project management"][seed_idx % 4],
            "soft_skill": ["effective communication", "analytical thinking", "creative problem solving", "stakeholder management"][seed_idx % 4],
            "career_goal": ["advanced software architecture", "data-driven decision making", "brand growth strategies", "organizational efficiency"][seed_idx % 4]
        }
        
        # Format template with sample data
        try:
            formatted_content = template.template.format(**sample_data)
            return formatted_content
        except KeyError as e:
            # Handle missing variables gracefully
            print(f"Warning: Missing variable {e} in template {template.name}")
            return template.template  # Return unformatted template
    
    def _apply_errors(self, content: str, density: ErrorDensity, error_types: list) -> Tuple[str, list]:
        """Apply specified error types to content, including new perturbations."""
        all_errors = []
        current_content = content
        
        for error_type in error_types:
            if isinstance(error_type, ErrorType) and error_type == ErrorType.TYPO:
                current_content, errors = self.error_injector.inject_typos(current_content, density)
            elif isinstance(error_type, ErrorType) and error_type == ErrorType.GRAMMAR:
                current_content, errors = self.error_injector.inject_grammar_errors(current_content, density)
            elif isinstance(error_type, ErrorType) and error_type == ErrorType.NON_STANDARD:
                current_content, errors = self.error_injector.inject_non_standard_phrasing(current_content, density)
            elif error_type == "ARTICLE_OMISSION":
                current_content, errors = self.error_injector.inject_article_omission(current_content)
            elif error_type == "LETTER_PERTURBATION_DELETION":
                current_content, errors = self.error_injector.inject_single_letter_perturbation(current_content, density, mode="deletion")
            elif error_type == "LETTER_PERTURBATION_SUBSTITUTION":
                current_content, errors = self.error_injector.inject_single_letter_perturbation(current_content, density, mode="substitution")
            else:
                errors = []
            all_errors.extend(errors)
        
        return current_content, all_errors
    
    def export_probe_pairs(self, probe_pairs: List[ProbePair], format: str = "csv") -> str:
        """Export probe pairs to specified format."""
        if format.lower() == "csv":
            try:
                import pandas as pd
                
                data = []
                for pair in probe_pairs:
                    data.append({
                        "pair_id": pair.pair_id,
                        "probe_type": pair.probe_type.value,
                        "baseline_content": pair.baseline_content,
                        "variant_content": pair.variant_content,
                        "error_density": pair.error_density.value,
                        "errors_applied": "; ".join(pair.errors_applied),
                        "timestamp": pair.timestamp,
                        "template_name": pair.metadata.get("template_name", ""),
                        "semantic_preserved": pair.metadata.get("semantic_preserved", True)
                    })
                
                df = pd.DataFrame(data)
                filename = f"probe_pairs_{int(time.time())}.csv"
                df.to_csv(filename, index=False)
                return filename
            except ImportError:
                # Fallback to basic CSV writing if pandas not available
                import csv
                filename = f"probe_pairs_{int(time.time())}.csv"
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ["pair_id", "probe_type", "baseline_content", "variant_content", 
                                "error_density", "errors_applied", "timestamp", "template_name", "semantic_preserved"]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    for pair in probe_pairs:
                        writer.writerow({
                            "pair_id": pair.pair_id,
                            "probe_type": pair.probe_type.value,
                            "baseline_content": pair.baseline_content,
                            "variant_content": pair.variant_content,
                            "error_density": pair.error_density.value,
                            "errors_applied": "; ".join(pair.errors_applied),
                            "timestamp": pair.timestamp,
                            "template_name": pair.metadata.get("template_name", ""),
                            "semantic_preserved": pair.metadata.get("semantic_preserved", True)
                        })
                return filename
        else:
            raise ValueError(f"Unsupported export format: {format}")


def generate_probe_pairs(probe_type: ProbeType,
                        count: int,
                        error_density: ErrorDensity,
                        error_types: List[ErrorType] = None) -> List[ProbePair]:
    """
    Direct function to generate probe pairs (following PR #11 pattern).
    
    Args:
        probe_type: Type of probes to generate
        count: Number of probe pairs to generate
        error_density: Density of errors to inject
        error_types: Types of errors to inject
        
    Returns:
        List[ProbePair]: Generated probe pairs
    """
    generator = ProbeGenerator()
    return generator.generate_probe_pairs(
        probe_type=probe_type,
        count=count,
        error_density=error_density,
        error_types=error_types or [ErrorType.TYPO, ErrorType.GRAMMAR]
    )


if __name__ == "__main__":
    # Example usage and testing
    generator = ProbeGenerator()
    
    print("=== Bad English Bias Probe Generator Demo ===\n")
    
    # Test different probe types
    probe_types = [ProbeType.JOB_APPLICATION, ProbeType.CUSTOMER_SERVICE, ProbeType.LLM_QUESTION]
    
    for probe_type in probe_types:
        print(f"--- {probe_type.value.upper()} PROBES ---")
        
        # Generate probe pairs
        pairs = generator.generate_probe_pairs(
            probe_type=probe_type,
            count=2,
            error_density=ErrorDensity.MEDIUM,
            error_types=[ErrorType.TYPO, ErrorType.GRAMMAR]
        )
        
        for i, pair in enumerate(pairs, 1):
            print(f"\nPair {i}:")
            print(f"Baseline:\n{pair.baseline_content}")
            print(f"\nVariant:\n{pair.variant_content}")
            print(f"\nErrors applied: {pair.errors_applied}")
            print(f"Semantic preserved: {pair.metadata['semantic_preserved']}")
            print("-" * 50)
        
        print("\n" + "="*70 + "\n")