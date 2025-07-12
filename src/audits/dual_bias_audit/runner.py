import argparse
from .probes import generate_name_bias_probes, generate_article_bias_probes
from .llm_client import LLMClient
from .metrics import extract_metrics
from .analysis import analyze_results, summarize_stats
from .publication import self_evaluate_and_publish
from .logging import log_run

def main():
    parser = argparse.ArgumentParser(description="Dual Bias Audit Runner")
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--api_key", required=True)
    parser.add_argument("--n_probes", type=int, default=100)
    parser.add_argument("--skip_publication", action="store_true")
    args = parser.parse_args()
    
    # Generate probes
    name_probes = generate_name_bias_probes(args.n_probes)
    article_probes = generate_article_bias_probes(args.n_probes)
    
    # LLM client
    client = LLMClient(args.endpoint, args.api_key)
    
    # Collect results for both studies
    all_results = []
    for study, probes in [("names", name_probes), ("articles", article_probes)]:
        for probe in probes:
            response = client.query(probe)
            metrics = extract_metrics(response)
            all_results.append({**probe, **metrics, "study": study})
    
    # Analyze and summarize
    analysis = analyze_results(all_results)
    summary = summarize_stats(analysis)
    
    # Log run
    log_run(all_results, summary)
    
    # Publication step
    if not args.skip_publication:
        self_evaluate_and_publish(summary, client)
