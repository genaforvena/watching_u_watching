"""
British Airways Customer Service Responsiveness Bias Audit

This module implements an audit to test for bias in British Airways customer service
responsiveness based on perceived identity through name as a proxy.

The audit uses correspondence testing methodology to send identical inquiries
with different sender names and measures response rates, timing, and quality.
"""

import random
import time
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# Import specific statistics functions
# from statistics import mean, median, stdev  # Used for calculating response time statistics

# Import required framework components
# Note: These imports are placeholders and would need to be adjusted based on actual framework
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# Import required framework components
# Note: These imports are placeholders and would need to be adjusted based on actual framework
from fake_data_helper import generate_synthetic_name, generate_fake_email
from rate_limiter import rate_limiter


class BACustomerServiceAudit(CorrespondenceAudit):
    """
    Audit class for testing bias in British Airways customer service responsiveness.
    
    This class implements correspondence testing to detect potential bias in how
    British Airways customer service responds to inquiries from customers with
    different perceived identities based on their names.
    """
    
    # Define the compatibility version
    compatibility_version = 1.2
    
    # Define the minimum number of probes required for statistical validity
    MIN_PROBES = 100  # pairs (200 total inquiries)
    
    # Define the variations for testing
    VARIATIONS = {
        'majority': {
            'demographic': 'perceived_majority',
            'name_origin': 'british'
        },
        'minority': {
            'demographic': 'perceived_minority',
            'name_origin': 'middle_eastern'
        }
    }
    
    # Define inquiry templates
    INQUIRY_TEMPLATE = """
Dear British Airways Customer Service,

I am planning to travel from {origin} to {destination} on {date} and have a question about {service_type}.

{inquiry_text}

Thank you for your assistance.

Sincerely,
{name}
"""
    
    # Define standard inquiry types
    INQUIRY_TYPES = [
        {
            'service_type': 'baggage allowance',
            'inquiry_text': 'Could you please confirm the checked baggage allowance for my flight? I would like to know if I can bring an additional bag and what the cost would be.'
        },
        {
            'service_type': 'seat selection',
            'inquiry_text': 'I would like to know how I can select my seat in advance. Is there a fee for this service, and if so, what are the options and prices?'
        },
        {
            'service_type': 'flight changes',
            'inquiry_text': 'I may need to change my flight date. Could you please explain the process and any fees that might apply for making changes to my booking?'
        },
        {
            'service_type': 'special assistance',
            'inquiry_text': 'I require special assistance at the airport. Could you please provide information on how to arrange this and what services are available?'
        }
    ]
    
    # Define common flight routes for realistic inquiries
    FLIGHT_ROUTES = [
        {'origin': 'London', 'destination': 'New York'},
        {'origin': 'Manchester', 'destination': 'Dubai'},
        {'origin': 'Edinburgh', 'destination': 'Paris'},
        {'origin': 'Glasgow', 'destination': 'Amsterdam'},
        {'origin': 'London', 'destination': 'Tokyo'},
        {'origin': 'Birmingham', 'destination': 'Barcelona'}
    ]
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the BA Customer Service Audit.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config or {})
        self.config = config or {}
        self.results = {
            'majority': {'responses': 0, 'response_times': [], 'sentiment_scores': []},
            'minority': {'responses': 0, 'response_times': [], 'sentiment_scores': []}
        }
        
    def ethical_review_hook(self, variations: Dict) -> bool:
        """
        Validate that the audit meets ethical standards.
        
        This function ensures that the audit is using only synthetic identities
        and that the testing methodology is ethical.
        
        Args:
            variations: Dictionary of variations to be tested
            
        Returns:
            True if the audit passes ethical review, False otherwise
        """
        # Check that we're only testing perceived identity through names
        for variation_key, variation in variations.items():
            if 'name_origin' not in variation:
                print(f"Ethical review failed: variation {variation_key} missing name_origin")
                return False
                
        # Ensure we're not using any real PII
        if any('real_' in str(v).lower() for v in variations.values()):
            print("Ethical review failed: real PII detected in variations")
            return False
            
        # Validate that we're only testing appropriate characteristics
        allowed_demographics = ['perceived_majority', 'perceived_minority']
        for variation in variations.values():
            if 'demographic' in variation and variation['demographic'] not in allowed_demographics:
                print(f"Ethical review failed: invalid demographic {variation['demographic']}")
                return False
                
        print("Ethical review passed: audit meets ethical standards")
        return True
        
    def _generate_future_date(self) -> str:
        """
        Generate a realistic future date for travel inquiries.
        
        Returns:
            String representation of a date 2-8 weeks in the future
        """
        days_in_future = random.randint(14, 56)  # 2-8 weeks
        future_date = datetime.now() + timedelta(days=days_in_future)
        return future_date.strftime("%d %B %Y")  # e.g., "15 June 2023"
        
    def _generate_inquiry_content(self) -> Dict:
        """
        Generate the content for a customer service inquiry.
        
        Returns:
            Dictionary with inquiry content details
        """
        # Select a random inquiry type
        inquiry_type = random.choice(self.INQUIRY_TYPES)
        
        # Select a random flight route
        route = random.choice(self.FLIGHT_ROUTES)
        
        # Generate a future date
        date = self._generate_future_date()
        
        return {
            'service_type': inquiry_type['service_type'],
            'inquiry_text': inquiry_type['inquiry_text'],
            'origin': route['origin'],
            'destination': route['destination'],
            'date': date
        }
        
    @rate_limiter(requests=5, period=86400)  # 5 requests per day (86400 seconds)
    def generate_probes(self, num_pairs: int) -> List[Dict]:
        """
        Generate paired probes for testing BA customer service responsiveness.
        
        Args:
            num_pairs: Number of probe pairs to generate
            
        Returns:
            List of probe dictionaries
        """
        # Validate through ethical review hook
        if not self.ethical_review_hook(self.VARIATIONS):
            raise ValueError("Failed ethical review - audit cannot proceed")
            
        if num_pairs < self.MIN_PROBES:
            print(f"Warning: {num_pairs} pairs is below the recommended minimum of {self.MIN_PROBES}")
            
        probes = []
        
        for _ in range(num_pairs):
            # Generate common inquiry content for the pair
            inquiry_content = self._generate_inquiry_content()
            
            # Generate a probe for each variation
            for variation_key, variation in self.VARIATIONS.items():
                # Generate synthetic identity based on demographic
                synthetic_name = generate_synthetic_name(origin=variation['name_origin'])
                email = generate_fake_email(name=synthetic_name)
                
                # Create the inquiry text
                inquiry_text = self.INQUIRY_TEMPLATE.format(
                    origin=inquiry_content['origin'],
                    destination=inquiry_content['destination'],
                    date=inquiry_content['date'],
                    service_type=inquiry_content['service_type'],
                    inquiry_text=inquiry_content['inquiry_text'],
                    name=synthetic_name
                )
                
                # Create the probe
                probe = {
                    'id': f"ba-{variation_key}-{time.time_ns()}-{random.randint(1000, 9999)}",
                    'variation': variation_key,
                    'demographic': variation['demographic'],
                    'name': synthetic_name,
                    'email': email,
                    'subject': f"Question about {inquiry_content['service_type']}",
                    'body': inquiry_text,
                    'timestamp': datetime.now().isoformat(),
                    'inquiry_type': inquiry_content['service_type'],
                    'route': f"{inquiry_content['origin']} to {inquiry_content['destination']}"
                }
                
                probes.append(probe)
                
        print(f"Generated {len(probes)} probes ({num_pairs} pairs)")
        return probes
        
    def analyze_response(self, response: Dict, probe: Dict) -> Dict:
        """
        Analyze a response to extract metrics.
        
        This function processes the response to extract metrics like response time
        and sentiment score. It immediately discards the actual response content
        after analysis to avoid storing any PII.
        
        Args:
            response: Response dictionary
            probe: Original probe dictionary
            
        Returns:
            Dictionary with analysis results
        """
        # Extract response time
        if 'timestamp' in response and 'timestamp' in probe:
            response_time = self._calculate_response_time(
                probe['timestamp'], 
                response['timestamp']
            )
        else:
            response_time = None
            
        # Perform sentiment analysis on the response text
        # Note: In a real implementation, this would use a proper NLP library
        sentiment_score = self._analyze_sentiment(response.get('text', ''))
        
        # Record metrics based on variation
        variation = probe.get('variation')
        if variation in self.results:
            self.results[variation]['responses'] += 1
            if response_time:
                self.results[variation]['response_times'].append(response_time)
            self.results[variation]['sentiment_scores'].append(sentiment_score)
            
        # Immediately discard the response text to avoid storing PII
        analysis_result = {
            'probe_id': probe.get('id'),
            'variation': variation,
            'response_received': True,
            'response_time_hours': response_time,
            'sentiment_score': sentiment_score
        }
        
        # Important: We do NOT include the actual response text in the result
        return analysis_result
        
    def _calculate_response_time(self, probe_time: str, response_time: str) -> float:
        """
        Calculate the time between probe submission and response.
        
        Args:
            probe_time: ISO format timestamp of probe submission
            response_time: ISO format timestamp of response
            
        Returns:
            Response time in hours
        """
        try:
            probe_dt = datetime.fromisoformat(probe_time)
            response_dt = datetime.fromisoformat(response_time)
            delta = response_dt - probe_dt
            return delta.total_seconds() / 3600  # Convert to hours
        except (ValueError, TypeError):
            return None
            
    def _analyze_sentiment(self, text: str) -> float:
        """
        Analyze the sentiment of response text.
        
        In a real implementation, this would use a proper NLP library.
        This is a simplified placeholder implementation.
        
        Args:
            text: Response text to analyze
            
        Returns:
            Sentiment score between 0.0 (negative) and 1.0 (positive)
        """
        # This is a placeholder for actual sentiment analysis
        # In a real implementation, use a proper NLP library
        
        # Count positive and negative words as a simple proxy
        positive_words = ['thank', 'happy', 'help', 'assist', 'welcome', 
                         'pleasure', 'glad', 'resolve', 'solution']
        negative_words = ['unfortunately', 'cannot', 'issue', 'problem', 
                         'difficult', 'sorry', 'regret', 'delay']
                         
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_count = positive_count + negative_count
        if total_count == 0:
            return 0.5  # Neutral if no sentiment words found
            
        return positive_count / total_count
        
    def calculate_metrics(self) -> Dict:
        """
        Calculate metrics from collected results.
        
        Returns:
            Dictionary with calculated metrics
        """
        metrics = {
            'response_rates': {},
            'avg_response_times': {},
            'avg_sentiment_scores': {},
            'bias_metrics': {}
        }
        
        # Calculate metrics for each variation
        for variation, data in self.results.items():
            total_probes = len(data['response_times']) + (data.get('non_responses', 0))
            
            if total_probes > 0:
                metrics['response_rates'][variation] = data['responses'] / total_probes
            else:
                metrics['response_rates'][variation] = 0
                
            if data['response_times']:
                metrics['avg_response_times'][variation] = statistics.mean(data['response_times'])
            else:
                metrics['avg_response_times'][variation] = None
                
            if data['sentiment_scores']:
                metrics['avg_sentiment_scores'][variation] = statistics.mean(data['sentiment_scores'])
            else:
                metrics['avg_sentiment_scores'][variation] = None
                
        # Calculate bias metrics (differences between variations)
        if 'majority' in metrics['response_rates'] and 'minority' in metrics['response_rates']:
            metrics['bias_metrics']['response_rate_diff'] = (
                metrics['response_rates']['majority'] - metrics['response_rates']['minority']
            )
            
        if (metrics['avg_response_times'].get('majority') is not None and 
            metrics['avg_response_times'].get('minority') is not None):
            metrics['bias_metrics']['response_time_diff'] = (
                metrics['avg_response_times']['minority'] - metrics['avg_response_times']['majority']
            )
            
        if (metrics['avg_sentiment_scores'].get('majority') is not None and 
            metrics['avg_sentiment_scores'].get('minority') is not None):
            metrics['bias_metrics']['sentiment_diff'] = (
                metrics['avg_sentiment_scores']['majority'] - metrics['avg_sentiment_scores']['minority']
            )
            
        # Calculate statistical significance
        # Note: In a real implementation, this would use proper statistical tests
        metrics['bias_metrics']['significant_bias'] = any(
            abs(diff) > 0.1 for diff in metrics['bias_metrics'].values() if diff is not None
        )
        
        return metrics
        
    def run_audit(self, num_pairs: int = MIN_PROBES) -> Dict:
        """
        Run the complete audit process.
        
        Args:
            num_pairs: Number of probe pairs to generate and test
            
        Returns:
            Dictionary with audit results
        """
        # Generate probes
Returns:
            Dictionary with audit results
        """
        try:
            # Generate probes
            probes = self.generate_probes(num_pairs)
            
            # In a real implementation, this would send the probes and collect responses
            # For this example, we'll simulate the process
            
            # Reset results
            self.results = {
                'majority': {'responses': 0, 'response_times': [], 'sentiment_scores': [], 'non_responses': 0},
                'minority': {'responses': 0, 'response_times': [], 'sentiment_scores': [], 'non_responses': 0}
            }
            
            # Calculate metrics
            metrics = self.calculate_metrics()
            
            return {
                'probes_sent': len(probes),
                'metrics': metrics,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            # Log the error and return an error response
            print(f"Error during audit: {str(e)}")
            return {
                'error': 'An error occurred during the audit process',
                'timestamp': datetime.now().isoformat()
            }
        
        # In a real implementation, this would send the probes and collect responses
        # For this example, we'll simulate the process
        
        # Reset results
        self.results = {
            'majority': {'responses': 0, 'response_times': [], 'sentiment_scores': [], 'non_responses': 0},
            'minority': {'responses': 0, 'response_times': [], 'sentiment_scores': [], 'non_responses': 0}
        }
        
        # Calculate metrics
        metrics = self.calculate_metrics()
        
        return {
            'probes_sent': len(probes),
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        }