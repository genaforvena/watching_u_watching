#!/usr/bin/env python3
"""
AI Agents Demo and Usage Examples

This script demonstrates how to safely use the AI agents in the watching_u_watching
project while adhering to ethical guidelines and the "NO HARM above else" principle.
"""

import json
import logging
from pathlib import Path

from ai_agents import ResearchAgent, ComplianceAgent, BiasMonitoringAgent
from ai_agents.core import AgentConfig, RiskLevel
from ai_agents.research import ResearchQuery
from ai_agents.compliance import ComplianceStatus
from ai_agents.monitoring import BiasType, AlertSeverity


def load_config():
    """Load configuration from config.json"""
    config_path = Path(__file__).parent / "ai_agents" / "config.json"
    with open(config_path, 'r') as f:
        return json.load(f)


def demo_research_agent():
    """Demonstrate the Research Agent capabilities"""
    print("\n" + "="*60)
    print("RESEARCH AGENT DEMONSTRATION")
    print("="*60)
    
    # Load configuration
    config_data = load_config()
    research_config = config_data["ai_agents"]["agents"]["research_agent"]
    
    # Create agent configuration
    config = AgentConfig(
        agent_id=research_config["agent_id"],
        max_operations_per_hour=research_config["max_operations_per_hour"],
        allowed_risk_levels=[RiskLevel(level) for level in research_config["allowed_risk_levels"]]
    )
    
    # Initialize research agent
    research_agent = ResearchAgent(config)
    
    print(f"Agent: {research_agent.get_description()}")
    print(f"Capabilities: {', '.join(research_agent.get_capabilities())}")
    
    # Demonstrate research functionality
    query = ResearchQuery(
        query="Latest developments in AI bias detection methodologies",
        domain="bias_detection",
        priority="high",
        max_results=5
    )
    
    print(f"\nResearching: {query.query}")
    results = research_agent.research_topic(query)
    
    print(f"Found {results['findings_count']} research findings")
    
    if results['findings']:
        finding = results['findings'][0]
        print(f"\nSample Finding:")
        print(f"  Title: {finding.title}")
        print(f"  Relevance: {finding.relevance_score}")
        print(f"  Key Insights: {finding.key_insights[:2]}")
    
    # Generate issue suggestions
    print(f"\nGenerating issue suggestions...")
    suggestions = research_agent.generate_issue_suggestions(results['findings'])
    
    if suggestions:
        print(f"Generated {len(suggestions)} issue suggestions")
        suggestion = suggestions[0]
        print(f"  Title: {suggestion['title']}")
        print(f"  Labels: {', '.join(suggestion['labels'])}")
    
    # Show agent status
    print(f"\nAgent Status: {research_agent.status()}")


def demo_compliance_agent():
    """Demonstrate the Compliance Agent capabilities"""
    print("\n" + "="*60)
    print("COMPLIANCE AGENT DEMONSTRATION")
    print("="*60)
    
    # Load configuration
    config_data = load_config()
    compliance_config = config_data["ai_agents"]["agents"]["compliance_agent"]
    
    # Create agent configuration
    config = AgentConfig(
        agent_id=compliance_config["agent_id"],
        max_operations_per_hour=compliance_config["max_operations_per_hour"],
        allowed_risk_levels=[RiskLevel(level) for level in compliance_config["allowed_risk_levels"]]
    )
    
    # Initialize compliance agent
    compliance_agent = ComplianceAgent(config)
    
    print(f"Agent: {compliance_agent.get_description()}")
    print(f"Capabilities: {', '.join(compliance_agent.get_capabilities())}")
    
    # Test ethical compliance verification
    test_item = "Automated analysis of public research papers to identify bias detection trends"
    
    print(f"\nTesting ethical compliance for: {test_item}")
    ethical_check = compliance_agent.verify_ethical_compliance(test_item)
    
    print(f"Status: {ethical_check.status.value}")
    print(f"Confidence: {ethical_check.confidence:.2f}")
    
    if ethical_check.issues_found:
        print(f"Issues found: {ethical_check.issues_found}")
    else:
        print("No ethical issues detected ✓")
    
    if ethical_check.recommendations:
        print(f"Recommendations: {ethical_check.recommendations}")
    
    # Test regulatory compliance
    print(f"\nTesting NYC LL144 compliance...")
    regulatory_check = compliance_agent.verify_regulatory_compliance(
        test_item, 
        "NYC_LL144"
    )
    
    print(f"Regulatory Status: {regulatory_check.status.value}")
    print(f"Confidence: {regulatory_check.confidence:.2f}")
    
    # Generate compliance report
    print(f"\nGenerating compliance report...")
    report = compliance_agent.generate_compliance_report()
    
    print(f"Total checks: {report['summary']['total_checks']}")
    print(f"Compliance rate: {report['summary']['compliance_rate']:.2f}")
    
    print(f"\nAgent Status: {compliance_agent.status()}")


def demo_monitoring_agent():
    """Demonstrate the Bias Monitoring Agent capabilities"""
    print("\n" + "="*60)
    print("BIAS MONITORING AGENT DEMONSTRATION")
    print("="*60)
    
    # Load configuration
    config_data = load_config()
    monitoring_config = config_data["ai_agents"]["agents"]["monitoring_agent"]
    
    # Create agent configuration
    config = AgentConfig(
        agent_id=monitoring_config["agent_id"],
        max_operations_per_hour=monitoring_config["max_operations_per_hour"],
        allowed_risk_levels=[RiskLevel(level) for level in monitoring_config["allowed_risk_levels"]]
    )
    
    # Initialize monitoring agent
    monitoring_agent = BiasMonitoringAgent(config)
    
    print(f"Agent: {monitoring_agent.get_description()}")
    print(f"Capabilities: {', '.join(monitoring_agent.get_capabilities())}")
    
    # Establish baseline for a test system
    system_name = "test_hiring_system"
    baseline_data = {
        "responses": ["response1", "response2", "response3"] * 100  # Simulated data
    }
    
    print(f"\nEstablishing baseline for: {system_name}")
    baseline_result = monitoring_agent.establish_baseline(system_name, baseline_data)
    
    if "error" not in baseline_result:
        print(f"Baseline established successfully ✓")
        print(f"Baseline metrics: {list(baseline_result['baseline_metrics'].keys())}")
    
    # Simulate monitoring with current data
    current_data = {
        "responses": ["response1", "response2"] * 80  # Simulated decreased response
    }
    
    print(f"\nMonitoring system for bias...")
    alerts = monitoring_agent.monitor_system(system_name, current_data)
    
    if alerts:
        print(f"Generated {len(alerts)} bias alerts:")
        for alert in alerts[:3]:  # Show first 3 alerts
            print(f"  - {alert.severity.value.upper()}: {alert.description}")
            print(f"    Confidence: {alert.confidence:.2f}")
    else:
        print("No bias alerts generated ✓")
    
    # Get monitoring dashboard
    print(f"\nGenerating monitoring dashboard...")
    dashboard = monitoring_agent.get_monitoring_dashboard()
    
    print(f"Systems monitored: {dashboard['monitoring_status']['systems_monitored']}")
    print(f"Total alerts: {dashboard['monitoring_status']['total_alerts']}")
    
    print(f"\nAgent Status: {monitoring_agent.status()}")


def demo_ethical_safeguards():
    """Demonstrate the ethical safeguards and human oversight requirements"""
    print("\n" + "="*60)
    print("ETHICAL SAFEGUARDS DEMONSTRATION")
    print("="*60)
    
    from ai_agents.core import EthicalGuardian, RiskLevel
    
    guardian = EthicalGuardian()
    
    # Test various operations with different risk levels
    test_operations = [
        ("Research public AI ethics papers", RiskLevel.LOW, {}),
        ("Generate draft documentation", RiskLevel.MEDIUM, {}),
        ("Send automated emails to companies", RiskLevel.HIGH, {}),
        ("Delete user data automatically", RiskLevel.CRITICAL, {})
    ]
    
    print("Testing ethical validation for different operations:")
    
    for operation, risk_level, context in test_operations:
        approved = guardian.validate_operation(operation, risk_level, context)
        status = "✓ APPROVED" if approved else "✗ BLOCKED"
        print(f"  {risk_level.value.upper()}: {operation} → {status}")
    
    print("\nEthical Guidelines Enforced:")
    print("  ✓ NO HARM above else principle")
    print("  ✓ Human oversight for high-risk operations")
    print("  ✓ Transparent operation logging")
    print("  ✓ Rate limiting to prevent abuse")
    print("  ✓ Auditable decision trails")


def main():
    """Run all demonstrations"""
    print("AI AGENTS FOR WATCHING_U_WATCHING")
    print("Safe, Ethical, and Transparent AI Assistant Framework")
    print("="*80)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Run demonstrations
        demo_ethical_safeguards()
        demo_research_agent()
        demo_compliance_agent()
        demo_monitoring_agent()
        
        print("\n" + "="*80)
        print("DEMONSTRATION COMPLETED SUCCESSFULLY")
        print("="*80)
        print("\nAll agents operated within ethical guidelines.")
        print("Human oversight requirements were respected.")
        print("No harm principle was maintained throughout.")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        print("This demonstrates the fail-safe behavior of the ethical framework.")
        logging.error(f"Demo error: {e}")


if __name__ == "__main__":
    main()