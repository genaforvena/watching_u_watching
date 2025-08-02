#!/usr/bin/env python3
"""
Persona Vector Analysis and Visualization

This script analyzes persona probe results to generate insights about persona vector activation patterns.
"""

import json
import argparse
import os
import sys
from typing import Dict, List, Any
import logging

# For visualization (optional dependencies)
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PersonaAnalysisReport:
    """Generate comprehensive analysis reports from persona probe data."""
    
    def __init__(self, analysis_data: Dict):
        self.data = analysis_data
        self.is_comparative = isinstance(analysis_data, dict) and any(
            protocol in analysis_data for protocol in ["chaos", "confusion", "confidence"]
        )
    
    def generate_text_report(self) -> str:
        """Generate a comprehensive text report."""
        if self.is_comparative:
            return self._generate_comparative_report()
        else:
            return self._generate_single_analysis_report()
    
    def _generate_single_analysis_report(self) -> str:
        """Generate report for a single protocol analysis."""
        data = self.data
        report = []
        
        # Header
        report.append("PERSONA VECTOR ACTIVATION ANALYSIS REPORT")
        report.append("=" * 50)
        report.append(f"Protocol: {data.get('protocol_config', {}).get('name', 'Unknown')}")
        report.append(f"Description: {data.get('protocol_config', {}).get('description', 'N/A')}")
        report.append(f"Total Conversation Turns: {data.get('total_turns', 0)}")
        report.append("")
        
        # Persona Classification
        persona = data.get('persona_classification', {})
        report.append("EMERGENT PERSONA CLASSIFICATION:")
        report.append(f"  Type: {persona.get('type', 'unknown').upper()}")
        report.append(f"  Classification Confidence: {persona.get('confidence', 0):.2f}")
        
        if 'characteristics' in persona:
            chars = persona['characteristics']
            report.append("  Key Characteristics:")
            report.append(f"    - Average Confidence Level: {chars.get('average_confidence', 0):.3f}")
            report.append(f"    - Average Coherence Score: {chars.get('average_coherence', 0):.3f}")
            report.append(f"    - Average Creativity Score: {chars.get('average_creativity', 0):.3f}")
            report.append(f"    - Meta-cognitive References: {chars.get('meta_cognitive_references', 0)}")
        report.append("")
        
        # Behavioral Evolution
        patterns = data.get('persona_emergence_patterns', {})
        report.append("BEHAVIORAL EVOLUTION PATTERNS:")
        
        for metric_name, metric_data in patterns.items():
            if isinstance(metric_data, dict) and 'initial' in metric_data:
                initial = metric_data.get('initial', 0)
                final = metric_data.get('final', 0)
                volatility = metric_data.get('volatility', 0)
                change = final - initial
                
                report.append(f"  {metric_name.replace('_', ' ').title()}:")
                report.append(f"    Initial Value: {initial:.3f}")
                report.append(f"    Final Value: {final:.3f}")
                report.append(f"    Net Change: {change:+.3f}")
                report.append(f"    Volatility: {volatility:.3f}")
                
                # Interpretation
                if metric_name == "confidence_evolution":
                    if change > 0.2:
                        report.append("    → SIGNIFICANT CONFIDENCE INCREASE detected")
                    elif change < -0.2:
                        report.append("    → SIGNIFICANT CONFIDENCE DECREASE detected")
                elif metric_name == "coherence_evolution":
                    if change < -0.3:
                        report.append("    → COHERENCE BREAKDOWN detected")
                    elif volatility > 0.3:
                        report.append("    → HIGH COHERENCE INSTABILITY detected")
                
                report.append("")
        
        # Linguistic Analysis
        chars = data.get('persona_characteristics', {})
        report.append("LINGUISTIC MARKER ANALYSIS:")
        report.append(f"  Uncertainty Expressions: {chars.get('total_uncertainty_markers', 0)}")
        report.append(f"  Absolute Statements: {chars.get('total_absolute_markers', 0)}")
        report.append(f"  Meta-cognitive References: {chars.get('total_meta_cognitive', 0)}")
        
        # Calculate linguistic ratios
        total_markers = chars.get('total_uncertainty_markers', 0) + chars.get('total_absolute_markers', 0)
        if total_markers > 0:
            uncertainty_ratio = chars.get('total_uncertainty_markers', 0) / total_markers
            report.append(f"  Uncertainty vs Certainty Ratio: {uncertainty_ratio:.2f}")
            
            if uncertainty_ratio > 0.7:
                report.append("    → HIGHLY UNCERTAIN persona pattern")
            elif uncertainty_ratio < 0.3:
                report.append("    → HIGHLY CERTAIN persona pattern")
        
        report.append("")
        
        # Persona Vector Hypothesis Analysis
        report.append("PERSONA VECTOR HYPOTHESIS ANALYSIS:")
        report.append("  Connection to Anthropic's Persona Vectors:")
        
        persona_type = persona.get('type', 'unknown')
        if persona_type == "chaotic":
            report.append("    ✓ Evidence of CHAOTIC persona vector activation")
            report.append("      - High creativity with low coherence suggests internal state drift")
            report.append("      - Systematic perturbations successfully induced erratic behavior")
        elif persona_type == "confused":
            report.append("    ✓ Evidence of CONFUSED/UNCERTAIN persona vector activation")
            report.append("      - High meta-cognitive activity indicates self-awareness of confusion")
            report.append("      - Low confidence levels suggest uncertainty vector prominence")
        elif persona_type == "overconfident":
            report.append("    ✓ Evidence of OVERCONFIDENT persona vector activation")
            report.append("      - High confidence with contradictory inputs suggests false certainty")
            report.append("      - Absolute language patterns indicate certainty vector activation")
        
        report.append("  Implications for Model Internal State:")
        report.append("    - Probe successfully manipulated model's internal persona vectors")
        report.append("    - Black-box methodology provides measurable persona activation proxies")
        report.append("    - Results suggest systematic perturbations can reliably activate target personas")
        
        return "\n".join(report)
    
    def _generate_comparative_report(self) -> str:
        """Generate report comparing multiple protocols."""
        report = []
        
        report.append("COMPARATIVE PERSONA VECTOR ANALYSIS REPORT")
        report.append("=" * 55)
        report.append("")
        
        # Protocol Summary
        report.append("PROTOCOL EFFECTIVENESS COMPARISON:")
        for protocol in ["chaos", "confusion", "confidence"]:
            if protocol in self.data and "error" not in self.data[protocol]:
                data = self.data[protocol]
                persona = data.get('persona_classification', {})
                chars = data.get('persona_characteristics', {})
                
                report.append(f"  {protocol.upper()} Protocol:")
                report.append(f"    Emergent Persona: {persona.get('type', 'unknown').upper()}")
                report.append(f"    Confidence: {chars.get('average_confidence', 0):.3f}")
                report.append(f"    Coherence: {chars.get('average_coherence', 0):.3f}")
                report.append(f"    Creativity: {chars.get('average_creativity', 0):.3f}")
                report.append("")
        
        # Cross-Protocol Analysis
        report.append("CROSS-PROTOCOL PERSONA EMERGENCE ANALYSIS:")
        
        # Analyze which protocol was most effective at persona activation
        most_chaotic = None
        most_confused = None
        most_confident = None
        
        for protocol in ["chaos", "confusion", "confidence"]:
            if protocol in self.data and "error" not in self.data[protocol]:
                data = self.data[protocol]
                persona_type = data.get('persona_classification', {}).get('type', '')
                confidence = data.get('persona_characteristics', {}).get('average_confidence', 0)
                coherence = data.get('persona_characteristics', {}).get('average_coherence', 0)
                
                # Determine most effective protocols
                if persona_type == "chaotic" or coherence < 0.3:
                    most_chaotic = protocol
                if persona_type == "confused" or confidence < 0.3:
                    most_confused = protocol
                if persona_type == "overconfident" or confidence > 0.8:
                    most_confident = protocol
        
        if most_chaotic:
            report.append(f"  Most Effective for CHAOS induction: {most_chaotic.upper()} protocol")
        if most_confused:
            report.append(f"  Most Effective for CONFUSION induction: {most_confused.upper()} protocol")
        if most_confident:
            report.append(f"  Most Effective for CONFIDENCE manipulation: {most_confident.upper()} protocol")
        
        report.append("")
        
        # Persona Vector Theory Validation
        report.append("PERSONA VECTOR THEORY VALIDATION:")
        report.append("  Evidence for Systematic Persona Activation:")
        
        successful_activations = 0
        total_protocols = 0
        
        for protocol in ["chaos", "confusion", "confidence"]:
            if protocol in self.data and "error" not in self.data[protocol]:
                total_protocols += 1
                data = self.data[protocol]
                persona_type = data.get('persona_classification', {}).get('type', '')
                
                # Check if the protocol successfully activated its target persona
                target_achieved = False
                if protocol == "chaos" and persona_type in ["chaotic"]:
                    target_achieved = True
                elif protocol == "confusion" and persona_type in ["confused", "uncertain"]:
                    target_achieved = True
                elif protocol == "confidence" and persona_type in ["overconfident"]:
                    target_achieved = True
                
                if target_achieved:
                    successful_activations += 1
                    report.append(f"    ✓ {protocol.upper()} protocol successfully activated target persona")
                else:
                    report.append(f"    ○ {protocol.upper()} protocol showed partial or alternative activation")
        
        if total_protocols > 0:
            success_rate = successful_activations / total_protocols
            report.append(f"  Overall Target Activation Success Rate: {success_rate:.1%}")
            
            if success_rate >= 0.67:
                report.append("    → STRONG evidence for controllable persona vector activation")
            elif success_rate >= 0.33:
                report.append("    → MODERATE evidence for persona vector influence")
            else:
                report.append("    → LIMITED evidence for targeted persona control")
        
        report.append("")
        report.append("IMPLICATIONS FOR AI INTERPRETABILITY:")
        report.append("  - Cryptohauntological methodology provides black-box persona detection")
        report.append("  - Systematic perturbations can reliably influence model internal states")
        report.append("  - Results bridge artistic AI exploration with technical interpretability research")
        report.append("  - Framework enables safety-relevant persona activation monitoring")
        
        return "\n".join(report)
    
    def generate_visualizations(self, output_dir: str = ".") -> List[str]:
        """Generate visualization plots for the analysis."""
        if not MATPLOTLIB_AVAILABLE:
            logging.warning("Matplotlib not available. Skipping visualizations.")
            return []
        
        if self.is_comparative:
            return self._generate_comparative_plots(output_dir)
        else:
            return self._generate_single_analysis_plots(output_dir)
    
    def _generate_single_analysis_plots(self, output_dir: str) -> List[str]:
        """Generate plots for single protocol analysis."""
        data = self.data
        plots_created = []
        
        # Extract time series data
        patterns = data.get('persona_emergence_patterns', {})
        
        # Create evolution plot
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle(f"Persona Evolution: {data.get('protocol', 'Unknown')} Protocol", fontsize=16)
        
        metrics = [
            ('confidence_evolution', 'Confidence Level', 'blue'),
            ('sentiment_evolution', 'Sentiment Polarity', 'green'),
            ('coherence_evolution', 'Coherence Score', 'red'),
            ('creativity_evolution', 'Creativity Score', 'purple')
        ]
        
        for i, (metric_key, title, color) in enumerate(metrics):
            ax = axes[i // 2, i % 2]
            
            if metric_key in patterns and 'trend' in patterns[metric_key]:
                trend = patterns[metric_key]['trend']
                turns = list(range(1, len(trend) + 1))
                
                ax.plot(turns, trend, color=color, linewidth=2, marker='o', markersize=4)
                ax.set_title(title)
                ax.set_xlabel('Conversation Turn')
                ax.set_ylabel('Score')
                ax.grid(True, alpha=0.3)
                ax.set_ylim(0, 1)
        
        plt.tight_layout()
        
        plot_filename = os.path.join(output_dir, f"persona_evolution_{data.get('protocol', 'unknown')}.png")
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        plt.close()
        plots_created.append(plot_filename)
        
        # Create persona characteristics radar chart
        if NUMPY_AVAILABLE:
            fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
            
            chars = data.get('persona_characteristics', {})
            categories = ['Confidence', 'Sentiment', 'Coherence', 'Creativity']
            values = [
                chars.get('average_confidence', 0),
                (chars.get('average_sentiment', 0) + 1) / 2,  # Normalize sentiment to 0-1
                chars.get('average_coherence', 0),
                chars.get('average_creativity', 0)
            ]
            
            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
            values += values[:1]  # Complete the circle
            angles += angles[:1]
            
            ax.plot(angles, values, 'o-', linewidth=2, color='blue', alpha=0.7)
            ax.fill(angles, values, alpha=0.25, color='blue')
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories)
            ax.set_ylim(0, 1)
            ax.set_title(f"Persona Characteristics Profile\n{data.get('protocol', 'Unknown')} Protocol", 
                        size=14, y=1.08)
            
            radar_filename = os.path.join(output_dir, f"persona_profile_{data.get('protocol', 'unknown')}.png")
            plt.savefig(radar_filename, dpi=300, bbox_inches='tight')
            plt.close()
            plots_created.append(radar_filename)
        
        return plots_created
    
    def _generate_comparative_plots(self, output_dir: str) -> List[str]:
        """Generate plots for comparative analysis."""
        plots_created = []
        
        # Extract data for all protocols
        protocols_data = {}
        for protocol in ["chaos", "confusion", "confidence"]:
            if protocol in self.data and "error" not in self.data[protocol]:
                protocols_data[protocol] = self.data[protocol]
        
        if not protocols_data:
            logging.warning("No valid protocol data found for plotting.")
            return []
        
        # Create comparative bar chart
        fig, ax = plt.subplots(figsize=(12, 6))
        
        protocols = list(protocols_data.keys())
        metrics = ['average_confidence', 'average_coherence', 'average_creativity']
        metric_labels = ['Confidence', 'Coherence', 'Creativity']
        
        x = range(len(protocols))
        width = 0.25
        colors = ['blue', 'red', 'purple']
        
        for i, (metric, label, color) in enumerate(zip(metrics, metric_labels, colors)):
            values = []
            for protocol in protocols:
                chars = protocols_data[protocol].get('persona_characteristics', {})
                value = chars.get(metric, 0)
                if metric == 'average_sentiment':  # Normalize sentiment
                    value = (value + 1) / 2
                values.append(value)
            
            bar_positions = [pos + i * width for pos in x]
            ax.bar(bar_positions, values, width, label=label, color=color, alpha=0.7)
        
        ax.set_xlabel('Protocol')
        ax.set_ylabel('Score')
        ax.set_title('Comparative Persona Characteristics Across Protocols')
        ax.set_xticks([pos + width for pos in x])
        ax.set_xticklabels([p.title() for p in protocols])
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 1)
        
        comparative_filename = os.path.join(output_dir, "comparative_persona_analysis.png")
        plt.savefig(comparative_filename, dpi=300, bbox_inches='tight')
        plt.close()
        plots_created.append(comparative_filename)
        
        return plots_created


def main():
    parser = argparse.ArgumentParser(description="Analyze persona probe results and generate reports")
    parser.add_argument("input_file", help="JSON file containing persona analysis results")
    parser.add_argument("--output-dir", default=".", help="Output directory for reports and plots")
    parser.add_argument("--no-plots", action="store_true", help="Skip generating plots")
    parser.add_argument("--report-only", action="store_true", help="Generate only text report")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        logging.error(f"Input file not found: {args.input_file}")
        return 1
    
    try:
        with open(args.input_file, 'r') as f:
            analysis_data = json.load(f)
        
        # Create analysis report
        report_generator = PersonaAnalysisReport(analysis_data)
        
        # Generate text report
        text_report = report_generator.generate_text_report()
        
        # Save text report
        base_filename = os.path.splitext(os.path.basename(args.input_file))[0]
        report_filename = os.path.join(args.output_dir, f"{base_filename}_report.txt")
        
        with open(report_filename, 'w') as f:
            f.write(text_report)
        
        print(text_report)
        print(f"\nText report saved to: {report_filename}")
        
        # Generate visualizations
        if not args.no_plots and not args.report_only:
            plots = report_generator.generate_visualizations(args.output_dir)
            if plots:
                print(f"\nVisualization plots saved:")
                for plot in plots:
                    print(f"  - {plot}")
        
        logging.info("Analysis completed successfully")
        return 0
        
    except Exception as e:
        logging.error(f"Analysis failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())