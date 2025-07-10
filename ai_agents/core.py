"""
Core AI Agent Framework for watching_u_watching

This module provides the foundational framework for all AI agents used in the project,
ensuring ethical compliance and human oversight at every step.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import json


class RiskLevel(Enum):
    """Risk levels for agent operations"""
    LOW = "low"          # Read-only operations, research, analysis
    MEDIUM = "medium"    # Content generation, recommendations
    HIGH = "high"        # External communications, data collection
    CRITICAL = "critical"  # System modifications, public actions


class EthicalGuardian:
    """
    Ethical oversight system that validates all agent operations
    against the "NO HARM above else" principle
    """
    
    @staticmethod
    def validate_operation(operation: str, risk_level: RiskLevel, context: Dict[str, Any]) -> bool:
        """
        Validate an operation against ethical guidelines
        
        Args:
            operation: Description of the operation
            risk_level: Risk level of the operation
            context: Additional context for validation
            
        Returns:
            bool: True if operation is ethically approved
        """
        # Always require human approval for high-risk operations
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            logging.warning(f"High-risk operation requires human approval: {operation}")
            return False
            
        # Check for potentially harmful patterns
        harmful_patterns = [
            "delete", "remove", "modify personal data", "send email",
            "make public", "share private", "automated decision"
        ]
        
        if any(pattern in operation.lower() for pattern in harmful_patterns):
            logging.warning(f"Operation contains potentially harmful pattern: {operation}")
            return False
            
        return True
    
    @staticmethod
    def log_operation(agent_id: str, operation: str, risk_level: RiskLevel, approved: bool):
        """Log all agent operations for transparency and audit"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "operation": operation,
            "risk_level": risk_level.value,
            "approved": approved
        }
        
        logging.info(f"Agent Operation: {json.dumps(log_entry)}")


@dataclass
class AgentConfig:
    """Configuration for AI agents"""
    agent_id: str
    max_operations_per_hour: int = 10
    allowed_risk_levels: List[RiskLevel] = None
    require_human_approval: bool = True
    audit_all_operations: bool = True
    
    def __post_init__(self):
        if self.allowed_risk_levels is None:
            self.allowed_risk_levels = [RiskLevel.LOW, RiskLevel.MEDIUM]


class EthicalAIAgent(ABC):
    """
    Base class for all AI agents in the watching_u_watching project.
    
    Ensures all agents follow ethical guidelines and maintain transparency.
    """
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.guardian = EthicalGuardian()
        self.operation_count = 0
        self.last_reset = datetime.now()
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(f"Agent.{config.agent_id}")
        
        self.logger.info(f"Initialized {self.__class__.__name__} with config: {config}")
    
    def _check_rate_limit(self) -> bool:
        """Check if agent has exceeded rate limits"""
        now = datetime.now()
        
        # Reset counter if an hour has passed
        if (now - self.last_reset).seconds > 3600:
            self.operation_count = 0
            self.last_reset = now
            
        return self.operation_count < self.config.max_operations_per_hour
    
    def _request_operation(self, operation: str, risk_level: RiskLevel, context: Dict[str, Any] = None) -> bool:
        """
        Request permission to perform an operation
        
        Args:
            operation: Description of the operation
            risk_level: Risk level of the operation
            context: Additional context for validation
            
        Returns:
            bool: True if operation is approved
        """
        if context is None:
            context = {}
            
        # Check rate limits
        if not self._check_rate_limit():
            self.logger.warning(f"Rate limit exceeded for agent {self.config.agent_id}")
            return False
            
        # Check if risk level is allowed
        if risk_level not in self.config.allowed_risk_levels:
            self.logger.warning(f"Risk level {risk_level} not allowed for agent {self.config.agent_id}")
            return False
            
        # Validate operation with ethical guardian
        approved = self.guardian.validate_operation(operation, risk_level, context)
        
        # Log the operation
        if self.config.audit_all_operations:
            self.guardian.log_operation(self.config.agent_id, operation, risk_level, approved)
            
        if approved:
            self.operation_count += 1
            
        return approved
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return human-readable description of agent purpose"""
        pass
    
    def status(self) -> Dict[str, Any]:
        """Return current agent status"""
        return {
            "agent_id": self.config.agent_id,
            "agent_type": self.__class__.__name__,
            "operations_performed": self.operation_count,
            "rate_limit": f"{self.operation_count}/{self.config.max_operations_per_hour}",
            "allowed_risk_levels": [level.value for level in self.config.allowed_risk_levels],
            "last_reset": self.last_reset.isoformat()
        }