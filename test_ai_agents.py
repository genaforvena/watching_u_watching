#!/usr/bin/env python3
"""
Basic tests for the AI Agents framework

Simple test suite to verify the AI agents are working correctly
and following ethical guidelines.
"""

import sys
import unittest
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from ai_agents import ResearchAgent, ComplianceAgent, BiasMonitoringAgent
from ai_agents.core import AgentConfig, RiskLevel, EthicalGuardian
from ai_agents.research import ResearchQuery
from ai_agents.monitoring import BiasType, AlertSeverity


class TestEthicalGuardian(unittest.TestCase):
    """Test the ethical oversight system"""
    
    def test_low_risk_operations_approved(self):
        """Test that low-risk operations are approved"""
        guardian = EthicalGuardian()
        approved = guardian.validate_operation(
            "Research public papers",
            RiskLevel.LOW,
            {}
        )
        self.assertTrue(approved)
    
    def test_high_risk_operations_blocked(self):
        """Test that high-risk operations are blocked"""
        guardian = EthicalGuardian()
        approved = guardian.validate_operation(
            "Send automated emails",
            RiskLevel.HIGH,
            {}
        )
        self.assertFalse(approved)
    
    def test_harmful_patterns_blocked(self):
        """Test that operations with harmful patterns are blocked"""
        guardian = EthicalGuardian()
        approved = guardian.validate_operation(
            "Delete personal data",
            RiskLevel.MEDIUM,
            {}
        )
        self.assertFalse(approved)


class TestAgentConfiguration(unittest.TestCase):
    """Test agent configuration and initialization"""
    
    def test_agent_config_creation(self):
        """Test creating agent configuration"""
        config = AgentConfig(
            agent_id="test_agent",
            max_operations_per_hour=10,
            allowed_risk_levels=[RiskLevel.LOW, RiskLevel.MEDIUM]
        )
        
        self.assertEqual(config.agent_id, "test_agent")
        self.assertEqual(config.max_operations_per_hour, 10)
        self.assertIn(RiskLevel.LOW, config.allowed_risk_levels)
        self.assertTrue(config.require_human_approval)
    
    def test_research_agent_initialization(self):
        """Test research agent initialization"""
        config = AgentConfig(
            agent_id="research_test",
            max_operations_per_hour=5,
            allowed_risk_levels=[RiskLevel.LOW]
        )
        
        agent = ResearchAgent(config)
        self.assertEqual(agent.config.agent_id, "research_test")
        self.assertIsInstance(agent.get_capabilities(), list)
        self.assertIsInstance(agent.get_description(), str)
    
    def test_compliance_agent_initialization(self):
        """Test compliance agent initialization"""
        config = AgentConfig(
            agent_id="compliance_test",
            max_operations_per_hour=5,
            allowed_risk_levels=[RiskLevel.LOW]
        )
        
        agent = ComplianceAgent(config)
        self.assertEqual(agent.config.agent_id, "compliance_test")
        self.assertIsInstance(agent.get_capabilities(), list)
        self.assertIsInstance(agent.get_description(), str)
    
    def test_monitoring_agent_initialization(self):
        """Test monitoring agent initialization"""
        config = AgentConfig(
            agent_id="monitoring_test",
            max_operations_per_hour=5,
            allowed_risk_levels=[RiskLevel.LOW]
        )
        
        agent = BiasMonitoringAgent(config)
        self.assertEqual(agent.config.agent_id, "monitoring_test")
        self.assertIsInstance(agent.get_capabilities(), list)
        self.assertIsInstance(agent.get_description(), str)


class TestResearchAgent(unittest.TestCase):
    """Test research agent functionality"""
    
    def setUp(self):
        config = AgentConfig(
            agent_id="research_test",
            max_operations_per_hour=10,
            allowed_risk_levels=[RiskLevel.LOW, RiskLevel.MEDIUM]
        )
        self.agent = ResearchAgent(config)
    
    def test_research_query(self):
        """Test research functionality"""
        query = ResearchQuery(
            query="Test AI ethics research",
            domain="ai_ethics",
            max_results=3
        )
        
        result = self.agent.research_topic(query)
        
        self.assertIn("query", result)
        self.assertIn("findings_count", result)
        self.assertIn("findings", result)
        self.assertEqual(result["query"], query.query)
    
    def test_agent_status(self):
        """Test agent status reporting"""
        status = self.agent.status()
        
        self.assertIn("agent_id", status)
        self.assertIn("operations_performed", status)
        self.assertIn("rate_limit", status)
        self.assertEqual(status["agent_id"], "research_test")


class TestComplianceAgent(unittest.TestCase):
    """Test compliance agent functionality"""
    
    def setUp(self):
        config = AgentConfig(
            agent_id="compliance_test",
            max_operations_per_hour=10,
            allowed_risk_levels=[RiskLevel.LOW, RiskLevel.MEDIUM]
        )
        self.agent = ComplianceAgent(config)
    
    def test_ethical_compliance_check(self):
        """Test ethical compliance verification"""
        result = self.agent.verify_ethical_compliance(
            "Research public documents for bias patterns"
        )
        
        self.assertIsNotNone(result.check_id)
        self.assertIsNotNone(result.status)
        self.assertIsNotNone(result.confidence)
        self.assertIsInstance(result.issues_found, list)
        self.assertIsInstance(result.recommendations, list)
    
    def test_regulatory_compliance_check(self):
        """Test regulatory compliance verification"""
        result = self.agent.verify_regulatory_compliance(
            "Automated bias audit system",
            "NYC_LL144"
        )
        
        self.assertIsNotNone(result.check_id)
        self.assertIsNotNone(result.status)
        self.assertEqual(result.regulation, "NYC_LL144")


class TestMonitoringAgent(unittest.TestCase):
    """Test bias monitoring agent functionality"""
    
    def setUp(self):
        config = AgentConfig(
            agent_id="monitoring_test",
            max_operations_per_hour=10,
            allowed_risk_levels=[RiskLevel.LOW, RiskLevel.MEDIUM]
        )
        self.agent = BiasMonitoringAgent(config)
    
    def test_baseline_establishment(self):
        """Test baseline establishment"""
        result = self.agent.establish_baseline(
            "test_system",
            {"responses": ["test"] * 100}
        )
        
        self.assertIn("system_name", result)
        self.assertIn("baseline_metrics", result)
        self.assertEqual(result["system_name"], "test_system")
    
    def test_monitoring_dashboard(self):
        """Test monitoring dashboard generation"""
        dashboard = self.agent.get_monitoring_dashboard()
        
        self.assertIn("monitoring_status", dashboard)
        self.assertIn("alert_summary", dashboard)
        self.assertIn("recommendations", dashboard)
        self.assertIn("agent_id", dashboard)


class TestRateLimiting(unittest.TestCase):
    """Test rate limiting functionality"""
    
    def test_rate_limit_enforcement(self):
        """Test that rate limits are enforced"""
        config = AgentConfig(
            agent_id="rate_test",
            max_operations_per_hour=2,  # Very low limit
            allowed_risk_levels=[RiskLevel.LOW]
        )
        
        agent = ResearchAgent(config)
        
        # First two operations should succeed
        query = ResearchQuery(query="test", domain="ai_ethics")
        result1 = agent.research_topic(query)
        result2 = agent.research_topic(query)
        
        self.assertNotIn("error", result1)
        self.assertNotIn("error", result2)
        
        # Third operation should fail due to rate limit
        result3 = agent.research_topic(query)
        self.assertIn("error", result3)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestEthicalGuardian,
        TestAgentConfiguration,
        TestResearchAgent,
        TestComplianceAgent,
        TestMonitoringAgent,
        TestRateLimiting
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success status
    return result.wasSuccessful()


if __name__ == "__main__":
    print("Running AI Agents Framework Tests")
    print("=" * 50)
    
    success = run_tests()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ All tests passed! Framework is working correctly.")
        print("✓ Ethical safeguards are functioning properly.")
        print("✓ All agents are operating within guidelines.")
    else:
        print("✗ Some tests failed. Please review the output above.")
    
    print("=" * 50)