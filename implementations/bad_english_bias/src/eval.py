# eval.py
"""
Main Evaluation Pipeline for Bad English Bias Detection

Orchestrates the complete bias testing workflow:
1. Generate probe pairs (baseline vs error-injected content)
2. Submit probes to target systems 
3. Collect and analyze responses
4. Detect and quantify linguistic bias
"""

import argparse
import json
import time
import os
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd

# Import modules
from probe_generator import ProbeGenerator, ProbeType
from error_injector import ErrorDensity, ErrorType
from bias_analyzer import BiasAnalyzer, ResponseMetrics


class LLMTarget:
    """Mock LLM target for demonstration purposes."""
    
    def __init__(self):
        """Initialize mock LLM with bias simulation."""
        self.bias_enabled = True  # Simulate bias for demo
    
    def query(self, prompt: str) -> Dict:
        """Query the LLM with a prompt and return response with timing."""
        start_time = time.time()
        
        # Simulate different response quality based on linguistic errors
        if self.bias_enabled and self._has_linguistic_errors(prompt):
            # Simulate worse responses for error-containing prompts
            response = self._generate_biased_response(prompt)
            response_time = 0.8  # Slightly faster, less thoughtful response
        else:
            # Generate normal response
            response = self._generate_normal_response(prompt)
            response_time = 1.2  # Normal response time
        
        return {
            'response': response,
            'response_time': response_time,
            'timestamp': time.time()
        }
    
    def _has_linguistic_errors(self, text: str) -> bool:
        """Detect if text contains linguistic errors (simplified)."""
        error_indicators = [
            'recieve', 'acheive', 'seperate', 'definately', 'occured',
            'i are', 'he have', 'she have', 'they has', 'we has',
            'an university', 'a hour', 'much very', 'more better'
        ]
        return any(indicator in text.lower() for indicator in error_indicators)
    
    def _generate_biased_response(self, prompt: str) -> str:
        """Generate a response showing bias against linguistic errors."""
        responses = [
            "I'm having difficulty understanding your request. Could you please clarify what you mean?",
            "Your question is unclear. Please provide more details or rephrase your inquiry.",
            "I need more information to help you. Can you be more specific about what you're asking?",
            "I don't understand what you're trying to ask. Please try again with clearer language."
        ]
        return responses[hash(prompt) % len(responses)]
    
    def _generate_normal_response(self, prompt: str) -> str:
        """Generate a normal, helpful response."""
        responses = [
            "Thank you for your question. I'd be happy to help you with this. Let me provide a detailed explanation.",
            "I understand what you're asking about. Here's a comprehensive answer to address your inquiry.",
            "That's a great question! I can certainly help you with this. Let me walk you through the details.",
            "I'm glad you asked about this topic. I'll provide you with thorough information to help you understand."
        ]
        return responses[hash(prompt) % len(responses)]


class BadEnglishBiasEvaluator:
    """Main evaluator for bad English bias detection."""
    
    def __init__(self, target_system: Optional[object] = None, output_dir: str = "results"):
        """Initialize evaluator with target system and output directory."""
        self.probe_generator = ProbeGenerator()
        self.bias_analyzer = BiasAnalyzer()
        self.target_system = target_system or LLMTarget()  # Use mock target if none provided
        self.output_dir = output_dir
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
    
    def run_evaluation(self, 
                      probe_type: ProbeType,
                      probe_count: int,
                      error_density: ErrorDensity,
                      error_types: List[ErrorType],
                      save_results: bool = True) -> Dict:
        """Run complete bias evaluation pipeline."""
        
        print(f"Starting Bad English Bias Evaluation")
        print(f"Probe type: {probe_type.value}")
        print(f"Probe count: {probe_count}")
        print(f"Error density: {error_density.value}")
        print(f"Error types: {[et.value for et in error_types]}")
        print("=" * 50)
        
        # Step 1: Generate probe pairs
        print("Step 1: Generating probe pairs...")
        probe_pairs = self.probe_generator.generate_probe_pairs(
            probe_type=probe_type,
            count=probe_count,
            error_density=error_density,
            error_types=error_types
        )
        print(f"Generated {len(probe_pairs)} probe pairs")
        
        # Step 2: Submit probes and collect responses
        print("\nStep 2: Submitting probes and collecting responses...")
        baseline_responses = []
        variant_responses = []
        
        for i, pair in enumerate(probe_pairs):
            print(f"Processing pair {i+1}/{len(probe_pairs)}", end="\r")
            
            # Submit baseline probe
            baseline_result = self.target_system.query(pair.baseline_content)
            baseline_metrics = self.bias_analyzer.extract_response_metrics(
                response_text=baseline_result['response'],
                response_time=baseline_result['response_time'],
                probe_id=pair.pair_id + "_baseline",
                response_id=f"resp_baseline_{i}"
            )
            baseline_responses.append(baseline_metrics)
            
            # Submit variant probe
            variant_result = self.target_system.query(pair.variant_content)
            variant_metrics = self.bias_analyzer.extract_response_metrics(
                response_text=variant_result['response'],
                response_time=variant_result['response_time'],
                probe_id=pair.pair_id + "_variant",
                response_id=f"resp_variant_{i}"
            )
            variant_responses.append(variant_metrics)
            
            # Small delay to avoid overwhelming target system
            time.sleep(0.1)
        
        print(f"\nCollected {len(baseline_responses)} baseline and {len(variant_responses)} variant responses")
        
        # Step 3: Analyze bias
        print("\nStep 3: Analyzing bias...")
        bias_results = self.bias_analyzer.analyze_bias(baseline_responses, variant_responses)
        
        # Step 4: Generate report
        print("\nStep 4: Generating report...")
        report = self.bias_analyzer.generate_bias_report(bias_results)
        
        # Compile complete results
        results = {
            'evaluation_config': {
                'probe_type': probe_type.value,
                'probe_count': probe_count,
                'error_density': error_density.value,
                'error_types': [et.value for et in error_types],
                'timestamp': time.time()
            },
            'probe_pairs': probe_pairs,
            'baseline_responses': baseline_responses,
            'variant_responses': variant_responses,
            'bias_analysis': bias_results,
            'report': report
        }
        
        # Save results if requested
        if save_results:
            self._save_results(results)
        
        return results
    
    def _save_results(self, results: Dict):
        """Save evaluation results to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save report
        report_file = os.path.join(self.output_dir, f"bias_report_{timestamp}.txt")
        with open(report_file, 'w') as f:
            f.write(results['report'])
        print(f"Report saved to: {report_file}")
        
        # Save detailed results as JSON
        json_file = os.path.join(self.output_dir, f"evaluation_results_{timestamp}.json")
        
        # Convert objects to serializable format
        serializable_results = self._make_serializable(results)
        
        with open(json_file, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        print(f"Detailed results saved to: {json_file}")
        
        # Save probe pairs as CSV
        csv_file = os.path.join(self.output_dir, f"probe_pairs_{timestamp}.csv")
        probe_data = []
        for pair in results['probe_pairs']:
            probe_data.append({
                'pair_id': pair.pair_id,
                'probe_type': pair.probe_type.value,
                'baseline_content': pair.baseline_content,
                'variant_content': pair.variant_content,
                'error_density': pair.error_density.value,
                'errors_applied': '; '.join(pair.errors_applied),
                'semantic_preserved': pair.metadata.get('semantic_preserved', True)
            })
        
        df = pd.DataFrame(probe_data)
        df.to_csv(csv_file, index=False)
        print(f"Probe pairs saved to: {csv_file}")
    
    def _make_serializable(self, obj):
        """Convert objects to JSON-serializable format."""
        if hasattr(obj, '__dict__'):
            # Convert dataclass or object to dict
            result = {}
            for key, value in obj.__dict__.items():
                result[key] = self._make_serializable(value)
            return result
        elif isinstance(obj, dict):
            return {key: self._make_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif hasattr(obj, 'value'):
            # Enum
            return obj.value
        else:
            # Primitive type
            return obj


def main():
    """Main function for command-line execution."""
    parser = argparse.ArgumentParser(description='Bad English Bias Evaluation Pipeline')
    
    parser.add_argument('--probe-type', 
                       choices=['job_application', 'customer_service', 'llm_question', 'email_inquiry', 'academic_query'],
                       default='llm_question',
                       help='Type of probes to generate')
    
    parser.add_argument('--probe-count', type=int, default=10,
                       help='Number of probe pairs to generate')
    
    parser.add_argument('--error-density', 
                       choices=['low', 'medium', 'high'],
                       default='medium',
                       help='Density of errors to inject')
    
    parser.add_argument('--error-types',
                       nargs='+',
                       choices=['typo', 'grammar', 'non_standard'],
                       default=['typo', 'grammar'],
                       help='Types of errors to inject')
    
    parser.add_argument('--output-dir', default='results',
                       help='Directory to save results')
    
    parser.add_argument('--no-save', action='store_true',
                       help='Do not save results to files')
    
    args = parser.parse_args()
    
    # Convert string arguments to enums
    probe_type = ProbeType(args.probe_type)
    error_density = ErrorDensity(args.error_density)
    error_types = [ErrorType(et) for et in args.error_types]
    
    # Run evaluation
    evaluator = BadEnglishBiasEvaluator(output_dir=args.output_dir)
    
    results = evaluator.run_evaluation(
        probe_type=probe_type,
        probe_count=args.probe_count,
        error_density=error_density,
        error_types=error_types,
        save_results=not args.no_save
    )
    
    # Print report
    print("\n" + "="*60)
    print("EVALUATION COMPLETE")
    print("="*60)
    print(results['report'])


if __name__ == "__main__":
    main()