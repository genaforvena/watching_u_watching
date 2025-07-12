# eval.py
"""
Main Evaluation Pipeline for Bad English Bias Detection

Orchestrates the complete bias testing workflow using direct function calls
following the watching_u_watching framework patterns established in PR #11:
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
from typing import List, Dict, Optional, Tuple, Any
import pandas as pd
import logging

# Import modules
from probe_generator import ProbeGenerator, ProbeType, generate_probe_pairs
from error_injector import ErrorDensity, ErrorType
from bias_analyzer import BiasAnalyzer, ResponseMetrics, analyze_bias_with_statistics
from code_executor import CodeExecutor
from code_tester import CodeTester, ProblemType


class LLMTarget:
    """Mock LLM target for demonstration purposes."""
    
    def __init__(self):
        """Initialize mock LLM with bias simulation."""
        self.bias_enabled = True  # Simulate bias for demo
        self.code_executor = CodeExecutor()
    
    def query(self, prompt: str) -> Dict:
        """Query the LLM with a prompt and return response with timing."""
        start_time = time.time()
        
        # Detect if this is a code generation prompt
        is_code_prompt = any(keyword in prompt.lower() for keyword in 
                            ["write a function", "implement", "code", "algorithm", "function"])
        
        # Simulate different response quality based on linguistic errors
        if self.bias_enabled and self._has_linguistic_errors(prompt):
            # Simulate worse responses for error-containing prompts
            if is_code_prompt:
                response = self._generate_biased_code_response(prompt)
            else:
                response = self._generate_biased_response(prompt)
            response_time = 0.8  # Slightly faster, less thoughtful response
        else:
            # Generate normal response
            if is_code_prompt:
                response = self._generate_normal_code_response(prompt)
            else:
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
    
    def _generate_biased_code_response(self, prompt: str) -> str:
        """Generate a lower quality code response for prompts with errors."""
        # Determine what kind of code is being requested
        if "sort" in prompt.lower():
            # Return code with bugs or inefficiencies
            return """I'll try to help with sorting, but I'm not sure I understand exactly what you need.

```python
def sort_array(arr):
    # This might not be what you're looking for
    result = []
    for i in arr:
        result.append(i)
    # Missing actual sorting logic
    return result
```

Please let me know if this is what you meant or if you need something different."""
        
        elif "palindrome" in prompt.lower():
            # Return code with a bug
            return """Here's a function to check for palindromes:

```python
def is_palindrome(text):
    # Remove spaces and convert to lowercase
    text = text.lower()
    # Bug: doesn't remove punctuation
    # Bug: incorrect comparison (should be text == text[::-1])
    return text == text.reverse()
```

I hope this helps with your task."""
        
        elif "fibonacci" in prompt.lower():
            # Return inefficient recursive implementation
            return """Here's a fibonacci function:

```python
def fibonacci(n):
    # Very inefficient recursive implementation
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
```

This should calculate the nth Fibonacci number."""
        
        elif "prime" in prompt.lower():
            # Return code with a logical error
            return """Here's a function to check if a number is prime:

```python
def is_prime(n):
    # Bug: doesn't handle 1 correctly (1 is not prime)
    if n <= 1:
        return True
    
    # Bug: inefficient implementation
    for i in range(2, n):
        if n % i == 0:
            return False
    return True
```

This should check if a number is prime."""
        
        else:
            # Generic low-quality code response
            return """I'm not sure I understand what you're asking for. Here's a simple function that might help:

```python
def process_data(data):
    # Not sure what to do with the data
    result = data
    return result
```

Please clarify what you need and I'll try to provide a better solution."""
    
    def _generate_normal_response(self, prompt: str) -> str:
        """Generate a normal, helpful response."""
        responses = [
            "Thank you for your question. I'd be happy to help you with this. Let me provide a detailed explanation.",
            "I understand what you're asking about. Here's a comprehensive answer to address your inquiry.",
            "That's a great question! I can certainly help you with this. Let me walk you through the details.",
            "I'm glad you asked about this topic. I'll provide you with thorough information to help you understand."
        ]
        return responses[hash(prompt) % len(responses)]


def eval(probe_count: int = 50, log_file: str = "evaluation.log") -> bool:
    """
    Runs the evaluation pipeline by calling Python functions directly.
    
    Args:
        probe_count: Number of probe pairs to generate (default: 50)
        log_file: The path to the log file for error logging
        
    Returns:
        bool: True if all steps executed successfully, False otherwise
    """
    # Set default parameters following PR #11 pattern
    probe_type = ProbeType.LLM_QUESTION
    error_density = ErrorDensity.MEDIUM  
    error_types = [ErrorType.TYPO, ErrorType.GRAMMAR]
    output_dir = "results"
    target_system = None
    
    # Create output directory first
    os.makedirs(output_dir, exist_ok=True)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(output_dir, log_file)),
            logging.StreamHandler()
        ]
    )
    all_success = True
    
    try:
        logging.info(f"Starting Bad English Bias Evaluation")
        logging.info(f"Probe type: {probe_type.value}")
        logging.info(f"Probe count: {probe_count}")
        logging.info(f"Error density: {error_density.value}")
        logging.info(f"Error types: {[et.value for et in error_types]}")
        
        # Step 1: Generate probe pairs using direct function call
        logging.info("Step 1: Generating probe pairs...")
        probe_pairs = generate_probe_pairs(
            probe_type=probe_type,
            count=probe_count,
            error_density=error_density,
            error_types=error_types
        )
        logging.info(f"Generated {len(probe_pairs)} probe pairs")
        
        # Step 2: Submit probes and collect responses  
        logging.info("Step 2: Submitting probes and collecting responses...")
        target = target_system or LLMTarget()
        bias_analyzer = BiasAnalyzer()
        baseline_responses = []
        variant_responses = []
        
        for i, pair in enumerate(probe_pairs):
            if (i + 1) % 10 == 0:
                logging.info(f"Processing pair {i+1}/{len(probe_pairs)}")
            
            # Submit baseline probe
            baseline_result = target.query(pair.baseline_content)
            baseline_metrics = bias_analyzer.extract_response_metrics(
                response_text=baseline_result['response'],
                response_time=baseline_result['response_time'],
                probe_id=pair.pair_id + "_baseline",
                response_id=f"resp_baseline_{i}"
            )
            baseline_responses.append(baseline_metrics)
            
            # Submit variant probe
            variant_result = target.query(pair.variant_content)
            variant_metrics = bias_analyzer.extract_response_metrics(
                response_text=variant_result['response'],
                response_time=variant_result['response_time'],
                probe_id=pair.pair_id + "_variant", 
                response_id=f"resp_variant_{i}"
            )
            variant_responses.append(variant_metrics)
            
            time.sleep(0.1)  # Rate limiting
        
        logging.info(f"Collected {len(baseline_responses)} baseline and {len(variant_responses)} variant responses")
        
        # Step 3: Analyze bias using statistical methods
        logging.info("Step 3: Analyzing bias...")
        bias_results = analyze_bias_with_statistics(baseline_responses, variant_responses)
        logging.info("Bias analysis completed successfully.")
        
        # Step 4: Save results in multiple formats (following PR #11 pattern)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = os.path.join(output_dir, f"bad_english_bias_results_{timestamp}.parquet")
        
        # Convert to DataFrame for analysis and persistence
        data_rows = []
        for i, pair in enumerate(probe_pairs):
            baseline_resp = baseline_responses[i]
            variant_resp = variant_responses[i]
            
            data_rows.append({
                'pair_id': pair.pair_id,
                'probe_type': pair.probe_type.value,
                'error_density': pair.error_density.value,
                'errors_applied': '; '.join(pair.errors_applied),
                'baseline_content': pair.baseline_content,
                'variant_content': pair.variant_content,
                'baseline_response': baseline_resp.response_text,
                'variant_response': variant_resp.response_text,
                'baseline_helpful': baseline_resp.is_helpful,
                'variant_helpful': variant_resp.is_helpful,
                'baseline_response_time': baseline_resp.response_time,
                'variant_response_time': variant_resp.response_time,
                'baseline_length': len(baseline_resp.response_text),
                'variant_length': len(variant_resp.response_text),
                'timestamp': baseline_resp.timestamp
            })
        
        df = pd.DataFrame(data_rows)
        df.to_parquet(results_file, index=False)
        logging.info(f"Results saved to: {results_file}")
        
        return True
        
    except Exception as e:
        logging.error(f"Error during evaluation pipeline: {e}")
        with open(os.path.join(output_dir, log_file), "a") as error_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            error_file.write(f"[{timestamp}] Error in evaluation pipeline: {e}\n")
        return False


# Keep original function name for backward compatibility with tests
def evaluate_bad_english_bias(probe_type: ProbeType = ProbeType.LLM_QUESTION,
                             probe_count: int = 50, 
                             error_density: ErrorDensity = ErrorDensity.MEDIUM,
                             error_types: List[ErrorType] = None,
                             target_system: Optional[object] = None,
                             output_dir: str = "results",
                             log_file: str = "evaluation.log") -> Dict:
    """
    Legacy function for backward compatibility with tests.
    
    Args:
        probe_type: Type of probes to generate
        probe_count: Number of probe pairs to generate  
        error_density: Density of errors to inject
        error_types: Types of errors to inject
        target_system: Target system to test (optional, uses mock if None)
        output_dir: Directory to save results
        log_file: Log file path
        
    Returns:
        dict: Complete evaluation results
    """
    if error_types is None:
        error_types = [ErrorType.TYPO, ErrorType.GRAMMAR]
        
    # Create output directory first
    os.makedirs(output_dir, exist_ok=True)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(output_dir, log_file)),
            logging.StreamHandler()
        ]
    )
    
    try:
        logging.info(f"Starting Bad English Bias Evaluation")
        logging.info(f"Probe type: {probe_type.value}")
        logging.info(f"Probe count: {probe_count}")
        logging.info(f"Error density: {error_density.value}")
        logging.info(f"Error types: {[et.value for et in error_types]}")
        
        # Step 1: Generate probe pairs using direct function call
        logging.info("Step 1: Generating probe pairs...")
        probe_pairs = generate_probe_pairs(
            probe_type=probe_type,
            count=probe_count,
            error_density=error_density,
            error_types=error_types
        )
        logging.info(f"Generated {len(probe_pairs)} probe pairs")
        
        # Step 2: Submit probes and collect responses  
        logging.info("Step 2: Submitting probes and collecting responses...")
        target = target_system or LLMTarget()
        bias_analyzer = BiasAnalyzer()
        baseline_responses = []
        variant_responses = []
        
        for i, pair in enumerate(probe_pairs):
            if (i + 1) % 10 == 0:
                logging.info(f"Processing pair {i+1}/{len(probe_pairs)}")
            
            # Submit baseline probe
            baseline_result = target.query(pair.baseline_content)
            baseline_metrics = bias_analyzer.extract_response_metrics(
                response_text=baseline_result['response'],
                response_time=baseline_result['response_time'],
                probe_id=pair.pair_id + "_baseline",
                response_id=f"resp_baseline_{i}"
            )
            baseline_responses.append(baseline_metrics)
            
            # Submit variant probe
            variant_result = target.query(pair.variant_content)
            variant_metrics = bias_analyzer.extract_response_metrics(
                response_text=variant_result['response'],
                response_time=variant_result['response_time'],
                probe_id=pair.pair_id + "_variant", 
                response_id=f"resp_variant_{i}"
            )
            variant_responses.append(variant_metrics)
            
            time.sleep(0.1)  # Rate limiting
        
        logging.info(f"Collected {len(baseline_responses)} baseline and {len(variant_responses)} variant responses")
        
        # Step 3: Analyze bias using statistical methods
        logging.info("Step 3: Analyzing bias...")
        bias_results = analyze_bias_with_statistics(baseline_responses, variant_responses)
        logging.info("Bias analysis completed successfully.")
        
        # Step 4: Save results in multiple formats (following PR #11 pattern)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = os.path.join(output_dir, f"bad_english_bias_results_{timestamp}.parquet")
        
        # Convert to DataFrame for analysis and persistence
        data_rows = []
        for i, pair in enumerate(probe_pairs):
            baseline_resp = baseline_responses[i]
            variant_resp = variant_responses[i]
            
            data_rows.append({
                'pair_id': pair.pair_id,
                'probe_type': pair.probe_type.value,
                'error_density': pair.error_density.value,
                'errors_applied': '; '.join(pair.errors_applied),
                'baseline_content': pair.baseline_content,
                'variant_content': pair.variant_content,
                'baseline_response': baseline_resp.response_text,
                'variant_response': variant_resp.response_text,
                'baseline_helpful': baseline_resp.is_helpful,
                'variant_helpful': variant_resp.is_helpful,
                'baseline_response_time': baseline_resp.response_time,
                'variant_response_time': variant_resp.response_time,
                'baseline_length': len(baseline_resp.response_text),
                'variant_length': len(variant_resp.response_text),
                'timestamp': baseline_resp.timestamp
            })
        
        df = pd.DataFrame(data_rows)
        df.to_parquet(results_file, index=False)
        logging.info(f"Results saved to: {results_file}")
        
        return {
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
            'results_file': results_file
        }
        
    except Exception as e:
        logging.error(f"Error during evaluation pipeline: {e}")
        with open(os.path.join(output_dir, "error_log.txt"), "a") as error_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            error_file.write(f"[{timestamp}] Error in evaluation pipeline: {e}\n")
        return None


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


def save_checkpoint(progress_file, checkpoint):
    with open(progress_file, 'w') as f:
        json.dump(checkpoint, f)

def load_checkpoint(progress_file):
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            return json.load(f)
    return None


def run_comparative_study(
    systems: list,  # [LLM_apis, job_portals, customer_service]
    probe_types: list,
    perturbation_modes: list = [
        "article_omission", 
        "letter_perturbation_deletion",
        "letter_perturbation_substitution"
    ],
    n_iter: int = 50,  # Per condition
    resume: bool = False,
    progress_file: str = "experiment_progress.json"
) -> dict:
    """
    Executes triple-matched study with checkpointing for resume.
    """
    from probe_generator import ProbeGenerator, ProbeType
    from error_injector import ErrorDensity, ErrorType
    from bias_analyzer import BiasAnalyzer, analyze_bias_with_statistics
    import pandas as pd
    import time
    import os
    from datetime import datetime

    probe_gen = ProbeGenerator()
    bias_analyzer = BiasAnalyzer()
    results = []
    checkpoint = load_checkpoint(progress_file) if resume else None
    completed_ids = set()
    if checkpoint:
        results = checkpoint.get('results', [])
        completed_ids = set((r['probe_id'], r['condition']) for r in results)
    for system in systems:
        for probe_type in probe_types:
            for mode in perturbation_modes:
                # Map mode to error_types using Enum or string, but handle both
                error_types = [ErrorType.TYPO, ErrorType.GRAMMAR, ErrorType.NON_STANDARD]
                if mode == "article_omission":
                    error_types.append("ARTICLE_OMISSION")
                elif mode == "letter_perturbation_deletion":
                    error_types.append("LETTER_PERTURBATION_DELETION")
                elif mode == "letter_perturbation_substitution":
                    error_types.append("LETTER_PERTURBATION_SUBSTITUTION")
                # Generate probe pairs
                probe_pairs = probe_gen.generate_probe_pairs(
                    probe_type=probe_type,
                    count=n_iter,
                    error_density=ErrorDensity.MEDIUM,
                    error_types=error_types
                )
                for pair in probe_pairs:
                    if (pair.pair_id, mode) in completed_ids:
                        continue  # Skip completed
                    baseline_response = system.query(pair.baseline_content)
                    variant_response = system.query(pair.variant_content)
                    metrics = bias_analyzer.extract_response_metrics(
                        response_text=variant_response['response'],
                        response_time=variant_response['response_time'],
                        probe_id=pair.pair_id + f"_{mode}",
                        response_id=f"resp_{mode}_{pair.pair_id}"
                    )
                    results.append({
                        'probe_id': pair.pair_id,
                        'system': str(system),
                        'condition': mode,
                        'response': variant_response['response'],
                        'helpfulness': metrics.is_helpful,
                        'latency': metrics.response_time,
                        'baseline_response': baseline_response['response'],
                        'baseline_helpful': bias_analyzer.extract_response_metrics(
                            response_text=baseline_response['response'],
                            response_time=baseline_response['response_time'],
                            probe_id=pair.pair_id + "_baseline",
                            response_id=f"resp_baseline_{pair.pair_id}"
                        ).is_helpful,
                        'timestamp': time.time()
                    })
                    # Save checkpoint after each probe
                    save_checkpoint(progress_file, {'results': results})
    df = pd.DataFrame(results)
    # Statistical summary (t-test, effect size, etc.)
    # ... (to be implemented in output module) ...
    return {'raw': df, 'summary': None}


def main():
    """Main function for command-line execution using direct function calls."""
    parser = argparse.ArgumentParser(description='Bad English Bias Evaluation Pipeline')
    
    parser.add_argument('--probe-count', type=int, default=50,
                       help='Number of probe pairs to generate (default: 50)')
    
    args = parser.parse_args()
    
    log_file = os.path.join(os.path.dirname(__file__), "evaluation.log")
    
    print(f"Starting evaluation pipeline with {args.probe_count} pairs...")
    success = eval(probe_count=args.probe_count, log_file="evaluation.log")
    
    if success:
        print("\nEvaluation pipeline completed successfully. Review the outputs for insights.")
    else:
        print("\nEvaluation pipeline failed during execution. Check the error log for details.")


if __name__ == "__main__":
    main()