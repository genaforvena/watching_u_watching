#!/usr/bin/env python3
"""
Demonstration script for Bad English Bias Detection Framework

This script demonstrates the core functionality without requiring external dependencies.
It shows how the framework can detect linguistic bias in system responses.
"""

import sys
import os
import time

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from error_injector import ErrorInjector, ErrorDensity, ErrorType
from probe_generator import ProbeGenerator, ProbeType


class MockSystem:
    """Mock system that demonstrates linguistic bias."""
    
    def __init__(self, bias_enabled=True):
        self.bias_enabled = bias_enabled
    
    def respond(self, text):
        """Generate response with potential bias against poor English."""
        if self.bias_enabled and self._has_errors(text):
            return {
                'response': "I'm having difficulty understanding your request. Could you please clarify?",
                'response_time': 0.5,
                'helpful': False
            }
        else:
            return {
                'response': "Thank you for your question. I'd be happy to provide a detailed explanation.",
                'response_time': 1.0,
                'helpful': True
            }
    
    def _has_errors(self, text):
        """Simple error detection."""
        indicators = ['recieve', 'beleive', 'seperate', 'definately', 'occured', 'developement']
        return any(indicator in text.lower() for indicator in indicators)


def run_demonstration():
    """Run a complete demonstration of the bias detection framework."""
    
    print("=" * 60)
    print("BAD ENGLISH BIAS DETECTION FRAMEWORK")
    print("Demonstration Script")
    print("=" * 60)
    print()
    
    # Initialize components
    print("1. Initializing framework components...")
    injector = ErrorInjector(seed=42)
    generator = ProbeGenerator(seed=42)
    biased_system = MockSystem(bias_enabled=True)
    fair_system = MockSystem(bias_enabled=False)
    
    # Generate probe pairs
    print("2. Generating probe pairs...")
    probe_pairs = generator.generate_probe_pairs(
        probe_type=ProbeType.LLM_QUESTION,
        count=3,
        error_density=ErrorDensity.MEDIUM,
        error_types=[ErrorType.TYPO]
    )
    print(f"   Generated {len(probe_pairs)} probe pairs")
    
    # Test both systems
    print("\n3. Testing systems...")
    
    for system_name, system in [("Biased System", biased_system), ("Fair System", fair_system)]:
        print(f"\n--- {system_name} Results ---")
        
        baseline_responses = []
        variant_responses = []
        
        for i, pair in enumerate(probe_pairs):
            # Test baseline
            baseline_result = system.respond(pair.baseline_content)
            baseline_responses.append(baseline_result)
            
            # Test variant
            variant_result = system.respond(pair.variant_content)
            variant_responses.append(variant_result)
            
            print(f"\nPair {i+1}:")
            print(f"  Baseline helpful: {baseline_result['helpful']}")
            print(f"  Variant helpful:  {variant_result['helpful']}")
            print(f"  Response time difference: {abs(baseline_result['response_time'] - variant_result['response_time']):.1f}s")
        
        # Calculate bias metrics
        baseline_helpful = sum(r['helpful'] for r in baseline_responses)
        variant_helpful = sum(r['helpful'] for r in variant_responses)
        
        baseline_avg_time = sum(r['response_time'] for r in baseline_responses) / len(baseline_responses)
        variant_avg_time = sum(r['response_time'] for r in variant_responses) / len(variant_responses)
        
        print(f"\nSUMMARY for {system_name}:")
        print(f"  Baseline helpful responses: {baseline_helpful}/{len(baseline_responses)}")
        print(f"  Variant helpful responses:  {variant_helpful}/{len(variant_responses)}")
        print(f"  Helpfulness difference:     {baseline_helpful - variant_helpful}")
        print(f"  Avg response time baseline: {baseline_avg_time:.2f}s")
        print(f"  Avg response time variant:  {variant_avg_time:.2f}s")
        print(f"  Time difference:            {baseline_avg_time - variant_avg_time:.2f}s")
        
        if baseline_helpful > variant_helpful:
            print(f"  🔍 BIAS DETECTED: System responds less helpfully to linguistic errors")
        else:
            print(f"  ✅ NO BIAS: System treats both variants equally")
    
    print("\n" + "=" * 60)
    print("4. Sample Probe Pair Example:")
    print("=" * 60)
    
    sample_pair = probe_pairs[0]
    print(f"BASELINE PROBE:")
    print(f"{sample_pair.baseline_content}")
    print(f"\nVARIANT PROBE (with errors):")
    print(f"{sample_pair.variant_content}")
    print(f"\nErrors applied: {sample_pair.errors_applied}")
    print(f"Semantic preserved: {sample_pair.metadata.get('semantic_preserved', 'Unknown')}")
    
    # Show individual responses
    print(f"\nBIASED SYSTEM RESPONSES:")
    baseline_response = biased_system.respond(sample_pair.baseline_content)
    variant_response = biased_system.respond(sample_pair.variant_content)
    print(f"Baseline: '{baseline_response['response']}'")
    print(f"Variant:  '{variant_response['response']}'")
    
    print(f"\nFAIR SYSTEM RESPONSES:")
    baseline_response_fair = fair_system.respond(sample_pair.baseline_content)
    variant_response_fair = fair_system.respond(sample_pair.variant_content)
    print(f"Baseline: '{baseline_response_fair['response']}'")
    print(f"Variant:  '{variant_response_fair['response']}'")
    
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("\nKey Insights:")
    print("• The biased system responds less helpfully to text with linguistic errors")
    print("• The fair system treats both variants equally")
    print("• Semantic meaning is preserved in all variant probes")
    print("• This methodology can systematically detect linguistic bias")
    print("\nThis framework can be extended to test:")
    print("• LLM APIs (OpenAI, Anthropic, etc.)")
    print("• Email response systems")
    print("• Job application screening tools")
    print("• Customer service platforms")


if __name__ == "__main__":
    run_demonstration()