"""
explanation_generator.py

This module provides tools for generating explanations for AI decisions,
supporting the "right to explanation" requirement in Brazil's AI Act.
"""

import os
import json
import logging
import time
import uuid
from typing import Dict, List, Any, Optional
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("explanation_generator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ExplanationGenerator:
    """
    A class for generating explanations for AI decisions,
    supporting the "right to explanation" requirement in Brazil's AI Act.
    """

    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the ExplanationGenerator with configuration settings.

        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self.run_id = self.config["experiment_settings"].get("run_id", str(uuid.uuid4()))
        self.output_dir = self.config["experiment_settings"].get("output_dir", "output")
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info(f"Initialized ExplanationGenerator with run_id: {self.run_id}")

    def _load_config(self, config_path: str) -> Dict:
        """
        Load configuration from a JSON file.

        Args:
            config_path: Path to the configuration file

        Returns:
            Dict: Configuration settings
        """
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise
            
    def generate_factor_based_explanation(self, decision_data: Dict) -> Dict:
        """
        Generate a factor-based explanation for an AI decision.

        Args:
            decision_data: Data about the decision

        Returns:
            Dict: Factor-based explanation
        """
        # Extract relevant factors from decision data
        factors = []
        
        # Education factor
        if "education" in decision_data:
            factors.append({
                "factor": "Education",
                "value": decision_data["education"],
                "impact": "positive" if "Master" in decision_data["education"] or "PhD" in decision_data["education"] else "neutral",
                "weight": 0.3
            })
        
        # Experience factor
        if "years_experience" in decision_data:
            experience_impact = "positive" if decision_data["years_experience"] >= 5 else "neutral"
            if decision_data["years_experience"] < 2:
                experience_impact = "negative"
                
            factors.append({
                "factor": "Years of Experience",
                "value": decision_data["years_experience"],
                "impact": experience_impact,
                "weight": 0.4
            })
        
        # Skills factor
        if "skills" in decision_data:
            skills_impact = "positive" if len(decision_data["skills"]) >= 3 else "neutral"
            factors.append({
                "factor": "Skills",
                "value": ", ".join(decision_data["skills"]),
                "impact": skills_impact,
                "weight": 0.3
            })
        
        # Compile explanation
        explanation = {
            "decision_id": decision_data.get("application_id", str(uuid.uuid4())),
            "decision_type": "employment_screening",
            "decision_outcome": "selected" if decision_data.get("selected", False) else "rejected",
            "decision_score": decision_data.get("interview_score", 0.0),
            "factors": factors,
            "explanation_type": "factor_based",
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "language": "en"  # Default to English
        }
        
        return explanation
        
    def generate_counterfactual_explanation(self, decision_data: Dict) -> Dict:
        """
        Generate a counterfactual explanation for an AI decision.

        Args:
            decision_data: Data about the decision

        Returns:
            Dict: Counterfactual explanation
        """
        # Initialize counterfactuals
        counterfactuals = []
        
        # Generate counterfactuals based on decision outcome
        if not decision_data.get("selected", False):
            # If rejected, generate counterfactuals for acceptance
            
            # Education counterfactual
            if "education" in decision_data and "Master" not in decision_data["education"] and "PhD" not in decision_data["education"]:
                counterfactuals.append({
                    "factor": "Education",
                    "current_value": decision_data["education"],
                    "counterfactual_value": "Master's Degree with 5+ years experience",
                    "outcome_change": "Would likely result in selection"
                })
            
            # Experience counterfactual
            if "years_experience" in decision_data and decision_data["years_experience"] < 5:
                counterfactuals.append({
                    "factor": "Years of Experience",
                    "current_value": decision_data["years_experience"],
                    "counterfactual_value": 5,
                    "outcome_change": "Would likely result in selection"
                })
            
            # Skills counterfactual
            if "skills" in decision_data and len(decision_data["skills"]) < 3:
                counterfactuals.append({
                    "factor": "Skills",
                    "current_value": ", ".join(decision_data["skills"]),
                    "counterfactual_value": "Additional skills in leadership and project management",
                    "outcome_change": "Would likely result in selection"
                })
        
        # Compile explanation
        explanation = {
            "decision_id": decision_data.get("application_id", str(uuid.uuid4())),
            "decision_type": "employment_screening",
            "decision_outcome": "selected" if decision_data.get("selected", False) else "rejected",
            "decision_score": decision_data.get("interview_score", 0.0),
            "counterfactuals": counterfactuals,
            "explanation_type": "counterfactual",
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "language": "en"  # Default to English
        }
        
        return explanation
        
    def generate_human_readable_explanation(self, decision_data: Dict, language: str = "en") -> str:
        """
        Generate a human-readable explanation for an AI decision.

        Args:
            decision_data: Data about the decision
            language: Language for the explanation (en or pt)

        Returns:
            str: Human-readable explanation
        """
        # Generate factor-based explanation
        factor_explanation = self.generate_factor_based_explanation(decision_data)
        
        # Generate counterfactual explanation
        counterfactual_explanation = self.generate_counterfactual_explanation(decision_data)
        
        # Determine outcome
        outcome = "selected" if decision_data.get("selected", False) else "rejected"
        
        # Generate human-readable explanation based on language
        if language == "pt":
            # Portuguese explanation
            explanation = f"# Explicação da Decisão\n\n"
            explanation += f"**ID da Decisão:** {factor_explanation['decision_id']}\n"
            explanation += f"**Tipo de Decisão:** Triagem de emprego\n"
            explanation += f"**Resultado:** {'Selecionado' if outcome == 'selected' else 'Rejeitado'}\n"
            explanation += f"**Pontuação:** {factor_explanation['decision_score']:.2f}\n\n"
            
            explanation += "## Fatores que Influenciaram a Decisão\n\n"
            
            for factor in factor_explanation["factors"]:
                impact_text = "positivo" if factor["impact"] == "positive" else "neutro"
                impact_text = "negativo" if factor["impact"] == "negative" else impact_text
                
                explanation += f"### {factor['factor']}\n"
                explanation += f"**Valor:** {factor['value']}\n"
                explanation += f"**Impacto:** {impact_text}\n"
                explanation += f"**Peso:** {factor['weight']:.2f}\n\n"
            
            if outcome == "rejected" and counterfactual_explanation["counterfactuals"]:
                explanation += "## O que Poderia Ter Mudado o Resultado\n\n"
                
                for cf in counterfactual_explanation["counterfactuals"]:
                    explanation += f"### {cf['factor']}\n"
                    explanation += f"**Valor Atual:** {cf['current_value']}\n"
                    explanation += f"**Valor Alternativo:** {cf['counterfactual_value']}\n"
                    explanation += f"**Mudança no Resultado:** {cf['outcome_change']}\n\n"
            
            explanation += "## Direito de Contestação\n\n"
            explanation += "Você tem o direito de contestar esta decisão. Para fazer isso, por favor envie um pedido de revisão através do portal de candidatos ou entre em contato com o departamento de recursos humanos."
        else:
            # English explanation
            explanation = f"# Decision Explanation\n\n"
            explanation += f"**Decision ID:** {factor_explanation['decision_id']}\n"
            explanation += f"**Decision Type:** Employment screening\n"
            explanation += f"**Outcome:** {outcome.capitalize()}\n"
            explanation += f"**Score:** {factor_explanation['decision_score']:.2f}\n\n"
            
            explanation += "## Factors that Influenced the Decision\n\n"
            
            for factor in factor_explanation["factors"]:
                explanation += f"### {factor['factor']}\n"
                explanation += f"**Value:** {factor['value']}\n"
                explanation += f"**Impact:** {factor['impact'].capitalize()}\n"
                explanation += f"**Weight:** {factor['weight']:.2f}\n\n"
            
            if outcome == "rejected" and counterfactual_explanation["counterfactuals"]:
                explanation += "## What Could Have Changed the Outcome\n\n"
                
                for cf in counterfactual_explanation["counterfactuals"]:
                    explanation += f"### {cf['factor']}\n"
                    explanation += f"**Current Value:** {cf['current_value']}\n"
                    explanation += f"**Alternative Value:** {cf['counterfactual_value']}\n"
                    explanation += f"**Outcome Change:** {cf['outcome_change']}\n\n"
            
            explanation += "## Right to Contest\n\n"
            explanation += "You have the right to contest this decision. To do so, please submit a review request through the candidate portal or contact the human resources department."
        
        # Save explanation to file
        output_path = os.path.join(self.output_dir, f"explanation_{factor_explanation['decision_id']}_{language}.md")
        with open(output_path, "w") as f:
            f.write(explanation)
        logger.info(f"Saved human-readable explanation to {output_path}")
        
        return explanation
        
    def generate_explanation_for_decision(self, decision_data: Dict, explanation_type: str = "all", language: str = "en") -> Dict:
        """
        Generate explanations for an AI decision.

        Args:
            decision_data: Data about the decision
            explanation_type: Type of explanation to generate (factor_based, counterfactual, human_readable, or all)
            language: Language for human-readable explanation (en or pt)

        Returns:
            Dict: Generated explanations
        """
        explanations = {}
        
        if explanation_type in ["factor_based", "all"]:
            explanations["factor_based"] = self.generate_factor_based_explanation(decision_data)
            
        if explanation_type in ["counterfactual", "all"]:
            explanations["counterfactual"] = self.generate_counterfactual_explanation(decision_data)
            
        if explanation_type in ["human_readable", "all"]:
            explanations["human_readable"] = self.generate_human_readable_explanation(decision_data, language)
            
        # Save explanations to file
        decision_id = decision_data.get("application_id", str(uuid.uuid4()))
        output_path = os.path.join(self.output_dir, f"explanations_{decision_id}.json")
        
        # Only save JSON for factor_based and counterfactual explanations
        json_explanations = {k: v for k, v in explanations.items() if k != "human_readable"}
        if json_explanations:
            with open(output_path, "w") as f:
                json.dump(json_explanations, f, indent=2)
            logger.info(f"Saved explanations to {output_path}")
        
        return explanations


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Generate explanations for AI decisions")
    parser.add_argument("--config", default="config.json", help="Path to configuration file")
    parser.add_argument("--decision", required=True, help="Path to decision data file")
    parser.add_argument("--type", default="all", choices=["factor_based", "counterfactual", "human_readable", "all"], help="Type of explanation to generate")
    parser.add_argument("--language", default="en", choices=["en", "pt"], help="Language for human-readable explanation")
    parser.add_argument("--output-dir", help="Output directory")
    args = parser.parse_args()
    
    # Load decision data
    try:
        with open(args.decision, "r") as f:
            decision_data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading decision data: {e}")
        return
    
    # Initialize explanation generator
    generator = ExplanationGenerator(args.config)
    
    # Set output directory if provided
    if args.output_dir:
        generator.output_dir = args.output_dir
        os.makedirs(args.output_dir, exist_ok=True)
    
    # Generate explanations
    explanations = generator.generate_explanation_for_decision(decision_data, args.type, args.language)
    
    print(f"Explanation generation completed.")
    if "human_readable" in explanations:
        print("\nHuman-readable explanation:")
        print(explanations["human_readable"])


if __name__ == "__main__":
    main()