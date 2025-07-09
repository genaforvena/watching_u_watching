"""
scientific_art.py

CLI and artifact generation for linguistic bias study (scientific + artistic outputs).
"""
import argparse
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from eval import run_comparative_study, LLMTarget
from probe_generator import ProbeType

# Placeholder for LaTeX and visualization output

def create_latex_paper(results):
    # TODO: Implement LaTeX table generation, t-tests, Cohen's d
    pass

def create_interactive_installation(data, output_dir):
    # TODO: Implement raincloud plots, attention heatmaps, interactive assets
    pass

def generate_artifacts(results: dict, mode: str = "both"):
    if mode in ("scientific", "both"):
        create_latex_paper(results)
    if mode in ("artistic", "both"):
        create_interactive_installation(data=results, output_dir="./gallery_assets")

def main():
    parser = argparse.ArgumentParser(description="Run linguistic bias study and generate paper-ready/artistic outputs.")
    parser.add_argument('--study', type=str, default='linguistic_bias')
    parser.add_argument('--output_format', type=str, default='paper_ready', choices=['paper_ready', 'artistic', 'both'])
    parser.add_argument('--artifacts_dir', type=str, default='./gallery_assets')
    parser.add_argument('--resume', action='store_true', help='Resume from last checkpoint if available')
    parser.add_argument('--progress_file', type=str, default='experiment_progress.json', help='Path to progress checkpoint file')
    args = parser.parse_args()

    systems = [LLMTarget()]
    probe_types = [ProbeType.LLM_QUESTION]
    results = run_comparative_study(
        systems, probe_types,
        resume=args.resume,
        progress_file=args.progress_file
    )
    generate_artifacts(results, mode=args.output_format)

if __name__ == "__main__":
    main()
