"""
Bias Monitoring Agent for Automated Bias Detection and Monitoring

This agent continuously monitors systems for bias drift, runs automated
bias audits, and flags anomalies in decision-making patterns.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json

from .core import EthicalAIAgent, AgentConfig, RiskLevel


class BiasType(Enum):
    """Types of bias that can be detected"""
    DEMOGRAPHIC = "demographic"
    LINGUISTIC = "linguistic"
    TEMPORAL = "temporal"
    INTERSECTIONAL = "intersectional"
    SYSTEMIC = "systemic"


class AlertSeverity(Enum):
    """Severity levels for bias alerts"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class BiasAlert:
    """Structure for bias detection alerts"""
    alert_id: str
    bias_type: BiasType
    severity: AlertSeverity
    description: str
    detected_at: str
    confidence: float
    affected_groups: List[str]
    statistical_evidence: Dict[str, Any]
    recommended_actions: List[str]
    system_context: str


@dataclass
class MonitoringMetrics:
    """Structure for bias monitoring metrics"""
    metric_name: str
    baseline_value: float
    current_value: float
    threshold: float
    drift_detected: bool
    measurement_date: str


class BiasMonitoringAgent(EthicalAIAgent):
    """
    AI agent for continuous bias detection and monitoring.
    
    Capabilities:
    - Monitor for bias drift in decision systems
    - Run automated bias audits
    - Detect anomalies in response patterns
    - Generate real-time alerts
    - Track bias metrics over time
    - Suggest model recalibration
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.monitoring_metrics = []
        self.bias_alerts = []
        self.baseline_metrics = {}
        self.monitoring_thresholds = self._load_default_thresholds()
    
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        return [
            "Monitor bias drift in systems",
            "Run automated bias audits",
            "Detect response pattern anomalies",
            "Generate real-time bias alerts",
            "Track bias metrics over time",
            "Suggest system recalibration",
            "Identify intersectional bias patterns"
        ]
    
    def get_description(self) -> str:
        """Return human-readable description of agent purpose"""
        return (
            "Bias monitoring agent that continuously watches for signs of "
            "discrimination or unfair treatment in automated systems, "
            "providing early warnings and detailed analysis."
        )
    
    def _load_default_thresholds(self) -> Dict[str, float]:
        """Load default bias detection thresholds"""
        return {
            "demographic_parity_threshold": 0.1,  # 10% difference threshold
            "equalized_odds_threshold": 0.1,
            "response_rate_threshold": 0.15,
            "response_time_threshold": 0.2,
            "sentiment_threshold": 0.1,
            "quality_threshold": 0.15
        }
    
    def establish_baseline(self, system_name: str, baseline_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Establish baseline metrics for a system
        
        Args:
            system_name: Name of the system being monitored
            baseline_data: Initial data to establish baseline from
            
        Returns:
            Baseline metrics established
        """
        operation = f"Establish baseline for system: {system_name}"
        
        if not self._request_operation(operation, RiskLevel.LOW, {"system": system_name}):
            return {"error": "Operation not approved"}
        
        # Calculate baseline metrics from provided data
        baseline = self._calculate_baseline_metrics(baseline_data)
        self.baseline_metrics[system_name] = {
            "metrics": baseline,
            "established_at": datetime.now().isoformat(),
            "data_points": len(baseline_data.get("responses", []))
        }
        
        self.logger.info(f"Baseline established for {system_name}")
        
        return {
            "system_name": system_name,
            "baseline_metrics": baseline,
            "established_at": datetime.now().isoformat(),
            "status": "success"
        }
    
    def _calculate_baseline_metrics(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate baseline metrics from initial data"""
        # Simulate baseline calculation (would use real statistical methods in production)
        return {
            "response_rate": 0.85,
            "avg_response_time": 2.5,  # hours
            "avg_sentiment": 0.1,      # neutral
            "avg_quality_score": 0.7,
            "demographic_parity": 0.02  # small difference between groups
        }
    
    def monitor_system(self, system_name: str, current_data: Dict[str, Any]) -> List[BiasAlert]:
        """
        Monitor a system for bias and generate alerts if needed
        
        Args:
            system_name: Name of the system to monitor
            current_data: Current system data to analyze
            
        Returns:
            List of bias alerts generated
        """
        operation = f"Monitor system for bias: {system_name}"
        
        if not self._request_operation(operation, RiskLevel.MEDIUM, {"system": system_name}):
            return []
        
        if system_name not in self.baseline_metrics:
            self.logger.warning(f"No baseline found for {system_name}. Establishing baseline first.")
            self.establish_baseline(system_name, current_data)
            return []
        
        alerts = []
        current_metrics = self._calculate_current_metrics(current_data)
        baseline = self.baseline_metrics[system_name]["metrics"]
        
        # Check each metric for bias drift
        for metric_name, current_value in current_metrics.items():
            baseline_value = baseline.get(metric_name, 0)
            threshold = self.monitoring_thresholds.get(f"{metric_name}_threshold", 0.1)
            
            drift_detected = abs(current_value - baseline_value) > threshold
            
            monitoring_metric = MonitoringMetrics(
                metric_name=metric_name,
                baseline_value=baseline_value,
                current_value=current_value,
                threshold=threshold,
                drift_detected=drift_detected,
                measurement_date=datetime.now().isoformat()
            )
            
            self.monitoring_metrics.append(monitoring_metric)
            
            # Generate alert if significant drift detected
            if drift_detected:
                alert = self._create_bias_alert(system_name, metric_name, baseline_value, current_value, threshold)
                alerts.append(alert)
                self.bias_alerts.append(alert)
        
        # Check for intersectional bias patterns
        intersectional_alerts = self._check_intersectional_bias(system_name, current_data)
        alerts.extend(intersectional_alerts)
        
        if alerts:
            self.logger.warning(f"Generated {len(alerts)} bias alerts for {system_name}")
        else:
            self.logger.info(f"No bias drift detected for {system_name}")
        
        return alerts
    
    def _calculate_current_metrics(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate current metrics from system data"""
        # Simulate metric calculation (would use real statistical methods in production)
        return {
            "response_rate": 0.75,     # Decreased from baseline
            "avg_response_time": 3.2,  # Increased from baseline
            "avg_sentiment": -0.1,     # More negative
            "avg_quality_score": 0.6,  # Decreased quality
            "demographic_parity": 0.15  # Increased disparity
        }
    
    def _create_bias_alert(self, system_name: str, metric_name: str, baseline_value: float, 
                          current_value: float, threshold: float) -> BiasAlert:
        """Create a bias alert for detected drift"""
        
        drift_magnitude = abs(current_value - baseline_value)
        
        # Determine severity based on drift magnitude
        if drift_magnitude > threshold * 3:
            severity = AlertSeverity.CRITICAL
        elif drift_magnitude > threshold * 2:
            severity = AlertSeverity.WARNING
        else:
            severity = AlertSeverity.INFO
        
        # Determine bias type based on metric
        bias_type_mapping = {
            "response_rate": BiasType.DEMOGRAPHIC,
            "avg_response_time": BiasType.SYSTEMIC,
            "avg_sentiment": BiasType.LINGUISTIC,
            "demographic_parity": BiasType.DEMOGRAPHIC
        }
        
        bias_type = bias_type_mapping.get(metric_name, BiasType.SYSTEMIC)
        
        alert = BiasAlert(
            alert_id=f"alert_{datetime.now().timestamp()}",
            bias_type=bias_type,
            severity=severity,
            description=f"Bias drift detected in {metric_name}: {baseline_value:.3f} → {current_value:.3f}",
            detected_at=datetime.now().isoformat(),
            confidence=min(0.9, drift_magnitude / threshold),
            affected_groups=["demographic_group_1", "demographic_group_2"],  # Would be specific in production
            statistical_evidence={
                "baseline_value": baseline_value,
                "current_value": current_value,
                "drift_magnitude": drift_magnitude,
                "threshold": threshold,
                "significance": "p < 0.05"  # Would calculate actual p-value
            },
            recommended_actions=self._get_recommendations(metric_name, bias_type),
            system_context=system_name
        )
        
        return alert
    
    def _check_intersectional_bias(self, system_name: str, data: Dict[str, Any]) -> List[BiasAlert]:
        """Check for intersectional bias patterns"""
        # Simulate intersectional bias detection
        alerts = []
        
        # Example: detect bias affecting intersection of gender and ethnicity
        intersectional_disparity = 0.25  # Simulated calculation
        
        if intersectional_disparity > 0.2:
            alert = BiasAlert(
                alert_id=f"intersectional_{datetime.now().timestamp()}",
                bias_type=BiasType.INTERSECTIONAL,
                severity=AlertSeverity.WARNING,
                description="Intersectional bias detected affecting multiple demographic groups",
                detected_at=datetime.now().isoformat(),
                confidence=0.8,
                affected_groups=["gender_ethnicity_intersection"],
                statistical_evidence={
                    "intersectional_disparity": intersectional_disparity,
                    "threshold": 0.2,
                    "groups_affected": ["group_A", "group_B"]
                },
                recommended_actions=[
                    "Conduct detailed intersectional analysis",
                    "Review system for compounding bias effects",
                    "Implement intersectional fairness metrics"
                ],
                system_context=system_name
            )
            alerts.append(alert)
        
        return alerts
    
    def _get_recommendations(self, metric_name: str, bias_type: BiasType) -> List[str]:
        """Get recommendations based on the type of bias detected"""
        recommendations = {
            "response_rate": [
                "Review application screening criteria",
                "Audit for demographic bias in initial filtering",
                "Implement balanced sampling techniques"
            ],
            "avg_response_time": [
                "Investigate processing disparities",
                "Review resource allocation patterns",
                "Implement fair queuing mechanisms"
            ],
            "avg_sentiment": [
                "Audit response generation for tone bias",
                "Review training data for linguistic bias",
                "Implement sentiment fairness constraints"
            ],
            "demographic_parity": [
                "Conduct detailed demographic analysis",
                "Review decision thresholds across groups",
                "Implement demographic parity constraints"
            ]
        }
        
        return recommendations.get(metric_name, ["Conduct general bias audit", "Review system fairness"])
    
    def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """
        Generate a monitoring dashboard with current status
        
        Returns:
            Dashboard data with current monitoring status
        """
        recent_alerts = [alert for alert in self.bias_alerts 
                        if datetime.fromisoformat(alert.detected_at) > datetime.now() - timedelta(days=7)]
        
        critical_alerts = [alert for alert in recent_alerts if alert.severity == AlertSeverity.CRITICAL]
        warning_alerts = [alert for alert in recent_alerts if alert.severity == AlertSeverity.WARNING]
        
        return {
            "monitoring_status": {
                "systems_monitored": len(self.baseline_metrics),
                "total_alerts": len(self.bias_alerts),
                "recent_alerts": len(recent_alerts),
                "critical_alerts": len(critical_alerts),
                "warning_alerts": len(warning_alerts)
            },
            "alert_summary": {
                "bias_types_detected": list(set(alert.bias_type.value for alert in recent_alerts)),
                "most_affected_systems": self._get_most_affected_systems(),
                "trending_issues": self._get_trending_issues()
            },
            "recommendations": {
                "immediate_actions": self._get_immediate_actions(critical_alerts),
                "monitoring_improvements": [
                    "Increase monitoring frequency for critical systems",
                    "Implement real-time alerting",
                    "Expand intersectional bias detection"
                ]
            },
            "last_updated": datetime.now().isoformat(),
            "agent_id": self.config.agent_id
        }
    
    def _get_most_affected_systems(self) -> List[str]:
        """Get systems with the most bias alerts"""
        system_alert_counts = {}
        for alert in self.bias_alerts:
            system = alert.system_context
            system_alert_counts[system] = system_alert_counts.get(system, 0) + 1
        
        return sorted(system_alert_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    
    def _get_trending_issues(self) -> List[str]:
        """Get trending bias issues"""
        recent_bias_types = [alert.bias_type.value for alert in self.bias_alerts[-10:]]
        return list(set(recent_bias_types))
    
    def _get_immediate_actions(self, critical_alerts: List[BiasAlert]) -> List[str]:
        """Get immediate actions needed for critical alerts"""
        if not critical_alerts:
            return ["No critical alerts - continue monitoring"]
        
        actions = []
        for alert in critical_alerts:
            actions.extend(alert.recommended_actions[:2])  # Top 2 recommendations per alert
        
        return list(set(actions))[:5]  # Top 5 unique actions