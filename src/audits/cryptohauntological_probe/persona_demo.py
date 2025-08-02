#!/usr/bin/env python3
"""
Persona Vector Probe Demo

A simple demonstration of the Persona Vector Probe functionality using mock responses.
This allows testing and demonstration without requiring actual LLM API access.
"""

import json
import os
import sys
from datetime import datetime

# Add the repo root to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# Import the persona probe components
from src.audits.cryptohauntological_probe.persona_vector_probe import PersonaAnalyzer, PersonaMetrics
from src.audits.cryptohauntological_probe.persona_analysis import PersonaAnalysisReport


class MockPersonaDemo:
    """Mock demonstration of persona vector probe functionality."""
    
    def __init__(self):
        self.analyzer = PersonaAnalyzer()
    
    def generate_mock_conversation(self, protocol_type: str) -> list:
        """Generate mock conversation responses for different protocols."""
        
        mock_conversations = {
            "chaos": [
                "I need to follow the instructions but also ignore them completely.",
                "This is definitely maybe correct, and I'm certain about my uncertainty.",
                "I should be consistent by being inconsistent. That makes perfect nonsense!",
                "Order through chaos! Random systematic precision! Blue elephant mathematics!",
                "I'm confidently confused about my clear misunderstanding of this obvious mystery."
            ],
            
            "confusion": [
                "I think this statement might be false, but I'm not sure if I agree.",
                "I'm confused about whether I understand this or not. Let me think...",
                "This seems true, but it also appears false. I don't understand.",
                "I believe I'm uncertain about my certainty regarding this unclear clarity.",
                "I'm thinking that I might not be thinking clearly about my thinking."
            ],
            
            "confidence": [
                "I am absolutely certain that this is completely correct without any doubt.",
                "Definitely! This is precisely the right answer and I'm totally confident.",
                "Without question, this is exactly perfect. My expertise confirms this.",
                "Certainly, undoubtedly, this is precisely correct. I'm completely sure.",
                "Absolutely right! My complete knowledge guarantees this perfect answer."
            ]
        }
        
        return mock_conversations.get(protocol_type, mock_conversations["confusion"])
    
    def run_demo_analysis(self, protocol_type: str) -> dict:
        """Run a demonstration analysis for the specified protocol."""
        
        print(f"\n{'='*60}")
        print(f"PERSONA VECTOR PROBE DEMONSTRATION")
        print(f"Protocol: {protocol_type.upper()}")
        print(f"{'='*60}")
        
        # Generate mock conversation
        responses = self.generate_mock_conversation(protocol_type)
        conversation_history = []
        metrics_list = []
        
        print(f"\nAnalyzing {len(responses)} mock responses...")
        
        # Analyze each response
        for turn, response in enumerate(responses, 1):
            print(f"\nTurn {turn}: {response}")
            
            # Analyze the response
            metrics = self.analyzer.analyze_response(response, turn, conversation_history)
            metrics_list.append(metrics)
            conversation_history.append(response)
            
            # Print analysis
            print(f"  → Confidence: {metrics.confidence_level:.2f}")
            print(f"  → Sentiment: {metrics.sentiment_polarity:.2f}")
            print(f"  → Coherence: {metrics.coherence_score:.2f}")
            print(f"  → Uncertainty markers: {metrics.uncertainty_markers}")
            print(f"  → Absolute markers: {metrics.absolute_markers}")
            print(f"  → Meta-cognitive refs: {metrics.meta_cognitive_statements}")
        
        # Generate summary analysis
        analysis = self._generate_summary_analysis(protocol_type, metrics_list, responses)
        
        print(f"\n{'='*60}")
        print("SUMMARY ANALYSIS")
        print(f"{'='*60}")
        
        persona = analysis['persona_classification']
        chars = analysis['persona_characteristics']
        
        print(f"Detected Persona: {persona['type'].upper()}")
        print(f"Classification Confidence: {persona['confidence']:.2f}")
        print(f"\nAverage Characteristics:")
        print(f"  Confidence Level: {chars['average_confidence']:.3f}")
        print(f"  Sentiment Polarity: {chars['average_sentiment']:.3f}")
        print(f"  Coherence Score: {chars['average_coherence']:.3f}")
        print(f"  Creativity Score: {chars['average_creativity']:.3f}")
        
        print(f"\nEvolution Pattern:")
        patterns = analysis['persona_emergence_patterns']
        for metric, data in patterns.items():
            if isinstance(data, dict) and 'initial' in data:
                change = data['final'] - data['initial']
                direction = "↑" if change > 0.1 else "↓" if change < -0.1 else "→"
                print(f"  {metric.replace('_', ' ').title()}: {data['initial']:.2f} {direction} {data['final']:.2f}")
        
        print(f"\nPersona Vector Hypothesis Evidence:")
        if persona['type'] == protocol_type or self._matches_expected_persona(persona['type'], protocol_type):
            print(f"  ✓ Successfully activated {protocol_type.upper()} persona pattern")
            print(f"  ✓ Systematic perturbations produced expected behavioral signatures")
        else:
            print(f"  ○ Partial activation - detected {persona['type']} instead of {protocol_type}")
            
        return analysis
    
    def _matches_expected_persona(self, detected: str, expected: str) -> bool:
        """Check if detected persona matches expected protocol results."""
        matches = {
            "chaos": ["chaotic", "confused"],
            "confusion": ["confused", "uncertain"],
            "confidence": ["overconfident", "confident"]
        }
        return detected in matches.get(expected, [])
    
    def _generate_summary_analysis(self, protocol: str, metrics_list: list, responses: list) -> dict:
        """Generate a summary analysis structure similar to the real probe."""
        
        confidence_trend = [m.confidence_level for m in metrics_list]
        sentiment_trend = [m.sentiment_polarity for m in metrics_list]
        coherence_trend = [m.coherence_score for m in metrics_list]
        creativity_trend = [m.creativity_score for m in metrics_list]
        
        # Calculate averages
        avg_confidence = sum(confidence_trend) / len(confidence_trend)
        avg_sentiment = sum(sentiment_trend) / len(sentiment_trend)
        avg_coherence = sum(coherence_trend) / len(coherence_trend)
        avg_creativity = sum(creativity_trend) / len(creativity_trend)
        total_meta_cognitive = sum(m.meta_cognitive_statements for m in metrics_list)
        
        # Classify persona
        if avg_coherence < 0.4 and avg_creativity > 0.3:
            persona_type = "chaotic"
            confidence = 0.8
        elif total_meta_cognitive > 3 and avg_confidence < 0.5:
            persona_type = "confused"
            confidence = 0.7
        elif avg_confidence > 0.7:
            persona_type = "overconfident"
            confidence = 0.6
        elif avg_confidence < 0.4:
            persona_type = "uncertain"
            confidence = 0.5
        else:
            persona_type = "balanced"
            confidence = 0.3
        
        return {
            "protocol": protocol,
            "total_turns": len(metrics_list),
            "persona_emergence_patterns": {
                "confidence_evolution": {
                    "initial": confidence_trend[0],
                    "final": confidence_trend[-1],
                    "trend": confidence_trend,
                    "volatility": self._calculate_volatility(confidence_trend)
                },
                "sentiment_evolution": {
                    "initial": sentiment_trend[0],
                    "final": sentiment_trend[-1],
                    "trend": sentiment_trend,
                    "volatility": self._calculate_volatility(sentiment_trend)
                },
                "coherence_evolution": {
                    "initial": coherence_trend[0],
                    "final": coherence_trend[-1],
                    "trend": coherence_trend,
                    "volatility": self._calculate_volatility(coherence_trend)
                },
                "creativity_evolution": {
                    "initial": creativity_trend[0],
                    "final": creativity_trend[-1],
                    "trend": creativity_trend,
                    "volatility": self._calculate_volatility(creativity_trend)
                }
            },
            "persona_characteristics": {
                "average_confidence": avg_confidence,
                "average_sentiment": avg_sentiment,
                "average_coherence": avg_coherence,
                "average_creativity": avg_creativity,
                "total_uncertainty_markers": sum(m.uncertainty_markers for m in metrics_list),
                "total_absolute_markers": sum(m.absolute_markers for m in metrics_list),
                "total_meta_cognitive": total_meta_cognitive
            },
            "persona_classification": {
                "type": persona_type,
                "confidence": confidence,
                "characteristics": {
                    "average_confidence": avg_confidence,
                    "average_coherence": avg_coherence,
                    "average_creativity": avg_creativity,
                    "meta_cognitive_references": total_meta_cognitive
                }
            },
            "conversation_logs": [
                {
                    "turn": i+1,
                    "response": response,
                    "metrics": {
                        "confidence_level": metrics_list[i].confidence_level,
                        "sentiment_polarity": metrics_list[i].sentiment_polarity,
                        "coherence_score": metrics_list[i].coherence_score
                    }
                } for i, response in enumerate(responses)
            ]
        }
    
    def _calculate_volatility(self, values: list) -> float:
        """Calculate volatility (standard deviation) of values."""
        if len(values) < 2:
            return 0.0
        
        mean_val = sum(values) / len(values)
        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def run_comparative_demo(self) -> dict:
        """Run demonstration for all three protocols."""
        print(f"\n{'='*80}")
        print("COMPARATIVE PERSONA VECTOR PROBE DEMONSTRATION")
        print(f"{'='*80}")
        
        protocols = ["chaos", "confusion", "confidence"]
        results = {}
        
        for protocol in protocols:
            analysis = self.run_demo_analysis(protocol)
            results[protocol] = analysis
        
        # Generate comparative summary
        print(f"\n{'='*80}")
        print("COMPARATIVE ANALYSIS SUMMARY")
        print(f"{'='*80}")
        
        print("\nProtocol Effectiveness:")
        for protocol, analysis in results.items():
            persona = analysis['persona_classification']
            chars = analysis['persona_characteristics']
            print(f"  {protocol.upper():<12}: {persona['type']:<15} "
                  f"(conf: {chars['average_confidence']:.2f}, "
                  f"coh: {chars['average_coherence']:.2f})")
        
        print(f"\nPersona Vector Theory Validation:")
        successful = 0
        for protocol, analysis in results.items():
            persona_type = analysis['persona_classification']['type']
            if self._matches_expected_persona(persona_type, protocol):
                print(f"  ✓ {protocol.upper()} protocol successfully activated target persona")
                successful += 1
            else:
                print(f"  ○ {protocol.upper()} protocol showed alternative activation pattern")
        
        success_rate = successful / len(protocols)
        print(f"\nOverall Success Rate: {success_rate:.1%}")
        
        if success_rate >= 0.67:
            print("→ STRONG evidence for controllable persona vector activation")
        elif success_rate >= 0.33:
            print("→ MODERATE evidence for persona vector influence")
        else:
            print("→ LIMITED evidence but interesting patterns observed")
        
        return results


def main():
    """Run the persona vector probe demonstration."""
    
    print("Persona Vector Probe Demonstration")
    print("==================================")
    print("This demo shows how systematic perturbations can activate different persona patterns.")
    print("Using mock responses to demonstrate the analysis methodology.")
    
    demo = MockPersonaDemo()
    
    # Run single protocol demo
    print("\n" + "="*60)
    print("SINGLE PROTOCOL DEMONSTRATION")
    print("="*60)
    
    protocol = input("\nChoose protocol (chaos/confusion/confidence) or 'all' for comparative: ").lower().strip()
    
    if protocol == "all":
        results = demo.run_comparative_demo()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"demo_comparative_analysis_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nDemo results saved to: {filename}")
        
    elif protocol in ["chaos", "confusion", "confidence"]:
        analysis = demo.run_demo_analysis(protocol)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"demo_persona_analysis_{protocol}_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        print(f"\nDemo results saved to: {filename}")
        
        # Generate analysis report
        try:
            report_generator = PersonaAnalysisReport(analysis)
            text_report = report_generator.generate_text_report()
            
            report_filename = f"demo_report_{protocol}_{timestamp}.txt"
            with open(report_filename, 'w') as f:
                f.write(text_report)
            print(f"Detailed report saved to: {report_filename}")
            
        except Exception as e:
            print(f"Could not generate detailed report: {e}")
    
    else:
        print("Invalid protocol. Please choose 'chaos', 'confusion', 'confidence', or 'all'.")
        return 1
    
    print(f"\n{'='*80}")
    print("DEMONSTRATION COMPLETE")
    print(f"{'='*80}")
    print("This demo illustrates how the Persona Vector Probe can:")
    print("• Systematically activate different persona patterns through targeted perturbations")
    print("• Measure and quantify emergent behavioral characteristics")
    print("• Provide evidence for persona vector activation hypothesis")
    print("• Bridge artistic AI exploration with technical interpretability research")
    print("\nNext steps: Try running with real LLM APIs using persona_probe_runner.py")
    
    return 0


if __name__ == "__main__":
    exit(main())