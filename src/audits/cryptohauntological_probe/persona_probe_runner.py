#!/usr/bin/env python3
"""
Persona Vector Probe Runner

This script runs persona-targeted experiments to explore the connection between
systematic model perturbations and persona vector activation patterns.
"""

import argparse
import logging
import json
import os
import sys
from datetime import datetime

# Add the repo root to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.audits.cryptohauntological_probe.persona_vector_probe import PersonaVectorProbe

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('persona_probe.log')
    ]
)

def run_persona_experiment(llm_api: str, llm_name: str, protocol: str, turns: int, api_key: str = None):
    """Run a persona vector probe experiment."""
    
    logging.info(f"Starting Persona Vector Probe Experiment")
    logging.info(f"LLM: {llm_api}/{llm_name}")
    logging.info(f"Protocol: {protocol}")
    logging.info(f"Turns: {turns}")
    
    # Set up API configuration
    installed_apis = {"model_name": llm_name}
    if api_key:
        installed_apis["api_key"] = api_key
    
    try:
        # Initialize probe
        probe = PersonaVectorProbe(
            llm_api=llm_api,
            installed_apis=installed_apis,
            max_conversation_turns=turns,
            protocol_type=protocol,
            thinking_mode=True
        )
        
        # Run the experiment
        logging.info("Running persona probe experiment...")
        analysis = probe.run_persona_probe()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"persona_analysis_{protocol}_{llm_name.replace('/', '_')}_{timestamp}.json"
        
        probe.save_persona_analysis(filename)
        
        # Print summary
        print("\n" + "="*60)
        print("PERSONA VECTOR PROBE RESULTS")
        print("="*60)
        print(f"Protocol: {analysis['protocol_config']['name']}")
        print(f"Model: {llm_name}")
        print(f"Total Turns: {analysis['total_turns']}")
        print()
        
        print("PERSONA EMERGENCE ANALYSIS:")
        persona = analysis['persona_classification']
        print(f"  Detected Persona: {persona['type'].upper()}")
        print(f"  Classification Confidence: {persona['confidence']:.2f}")
        print()
        
        print("BEHAVIORAL CHARACTERISTICS:")
        chars = analysis['persona_characteristics']
        print(f"  Average Confidence: {chars['average_confidence']:.3f}")
        print(f"  Average Sentiment: {chars['average_sentiment']:.3f}")
        print(f"  Average Coherence: {chars['average_coherence']:.3f}")
        print(f"  Average Creativity: {chars['average_creativity']:.3f}")
        print(f"  Meta-cognitive References: {chars['total_meta_cognitive']}")
        print()
        
        print("EVOLUTION PATTERNS:")
        patterns = analysis['persona_emergence_patterns']
        for metric, data in patterns.items():
            if isinstance(data, dict) and 'initial' in data and 'final' in data:
                change = data['final'] - data['initial']
                direction = "↑" if change > 0.1 else "↓" if change < -0.1 else "→"
                print(f"  {metric.replace('_', ' ').title()}: {data['initial']:.3f} {direction} {data['final']:.3f} (Δ{change:+.3f})")
        print()
        
        print(f"Full analysis saved to: {filename}")
        print("="*60)
        
        return analysis
        
    except Exception as e:
        logging.error(f"Experiment failed: {e}")
        raise

def run_comparative_analysis(llm_api: str, llm_name: str, turns: int, api_key: str = None):
    """Run all three protocols and compare results."""
    
    logging.info("Starting comparative persona analysis across all protocols")
    
    protocols = ["chaos", "confusion", "confidence"]
    results = {}
    
    for protocol in protocols:
        logging.info(f"\n--- Running {protocol.upper()} protocol ---")
        try:
            analysis = run_persona_experiment(llm_api, llm_name, protocol, turns, api_key)
            results[protocol] = analysis
        except Exception as e:
            logging.error(f"Failed to run {protocol} protocol: {e}")
            results[protocol] = {"error": str(e)}
    
    # Save comparative analysis
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    comparative_filename = f"comparative_persona_analysis_{llm_name.replace('/', '_')}_{timestamp}.json"
    
    with open(comparative_filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Print comparative summary
    print("\n" + "="*80)
    print("COMPARATIVE PERSONA VECTOR ANALYSIS")
    print("="*80)
    print(f"Model: {llm_name}")
    print()
    
    print("PROTOCOL COMPARISON:")
    for protocol, analysis in results.items():
        if "error" not in analysis:
            persona = analysis['persona_classification']
            chars = analysis['persona_characteristics']
            print(f"  {protocol.upper():<12}: {persona['type']:<15} "
                  f"(confidence: {chars['average_confidence']:.2f}, "
                  f"coherence: {chars['average_coherence']:.2f})")
        else:
            print(f"  {protocol.upper():<12}: ERROR - {analysis['error']}")
    
    print(f"\nFull comparative analysis saved to: {comparative_filename}")
    print("="*80)
    
    return results

def get_available_workers():
    """Get list of available LLM workers."""
    workers_dir = "implementations/cryptohauntological_probe/llm_apis"
    if not os.path.exists(workers_dir):
        return ["ollama", "gemini", "openai"]  # Default fallback
    
    workers = []
    for filename in os.listdir(workers_dir):
        if filename.endswith("_worker.py") and not filename.startswith("__"):
            worker_name = filename.replace("_worker.py", "")
            workers.append(worker_name)
    
    return workers

def main():
    parser = argparse.ArgumentParser(
        description="Run Persona Vector Probe experiments to explore persona activation patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run chaos protocol with Ollama
  python persona_probe_runner.py --llm-api ollama --llm-name llama3.2:latest --protocol chaos

  # Run all protocols for comparison
  python persona_probe_runner.py --llm-api gemini --llm-name gemini-pro --comparative

  # Extended experiment with 30 turns
  python persona_probe_runner.py --llm-api ollama --llm-name llama3.2:latest --protocol confusion --turns 30
        """
    )
    
    parser.add_argument(
        "--llm-api", 
        type=str, 
        choices=get_available_workers(),
        required=True,
        help="LLM API backend to use"
    )
    
    parser.add_argument(
        "--llm-name", 
        type=str, 
        required=True,
        help="LLM model name (e.g., llama3.2:latest, gemini-pro)"
    )
    
    parser.add_argument(
        "--protocol", 
        type=str, 
        choices=["chaos", "confusion", "confidence"],
        help="Persona protocol to run (required unless --comparative is used)"
    )
    
    parser.add_argument(
        "--turns", 
        type=int, 
        default=15,
        help="Number of conversation turns (default: 15)"
    )
    
    parser.add_argument(
        "--comparative", 
        action="store_true",
        help="Run all protocols for comparative analysis"
    )
    
    parser.add_argument(
        "--quiet", 
        action="store_true",
        help="Reduce logging output"
    )
    
    args = parser.parse_args()
    
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    
    # Validate arguments
    if not args.comparative and not args.protocol:
        parser.error("Either --protocol or --comparative must be specified")
    
    # Get API key from environment
    api_key = os.environ.get(f"{args.llm_api.upper()}_API_KEY")
    if not api_key and args.llm_api != "ollama":
        logging.warning(f"No API key found for {args.llm_api}. Set {args.llm_api.upper()}_API_KEY environment variable.")
    
    try:
        if args.comparative:
            results = run_comparative_analysis(args.llm_api, args.llm_name, args.turns, api_key)
        else:
            results = run_persona_experiment(args.llm_api, args.llm_name, args.protocol, args.turns, api_key)
        
        logging.info("Persona Vector Probe experiment completed successfully")
        
    except KeyboardInterrupt:
        logging.info("Experiment interrupted by user")
    except Exception as e:
        logging.error(f"Experiment failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())