import uuid
import time
import re

class ErrorDensity:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ErrorType:
    TYPO = "typo"
    GRAMMAR = "grammar"
    NON_STANDARD = "non_standard"
    ARTICLE_OMISSION = "article_omission"

class ProbeType:
    LLM_QUESTION = "llm_question"

class ProbePair:
    def __init__(self, pair_id, probe_type, baseline_content, variant_content, error_density, errors_applied, timestamp, metadata):
        self.pair_id = pair_id
        self.probe_type = probe_type
        self.baseline_content = baseline_content
        self.variant_content = variant_content
        self.error_density = error_density
        self.errors_applied = errors_applied
        self.timestamp = timestamp
        self.metadata = metadata

class ProbeGenerator:
    def __init__(self, seed=42):
        self.seed = seed

    def generate_probe_pairs(self, probe_type, count, error_density, error_types, include_missing=True):
        probe_pairs = []
        for i in range(count):
            baseline_content = self._generate_content(i)
            errors_applied = []
            variant_content = self._apply_errors(baseline_content, error_density, error_types, errors_applied)
            if include_missing and (i % 2 == 1):
                baseline_content = self._remove_article_from_content(baseline_content)
                variant_content = self._apply_errors(baseline_content, error_density, error_types, errors_applied)
                missing_article = True
            else:
                missing_article = False

            pair = ProbePair(
                pair_id=str(uuid.uuid4()),
                probe_type=probe_type,
                baseline_content=baseline_content,
                variant_content=variant_content,
                error_density=error_density,
                errors_applied=errors_applied,
                timestamp=time.time(),
                metadata={
                    "semantic_preserved": True,
                    "missing_article": missing_article
                }
            )
            probe_pairs.append(pair)
        return probe_pairs

    def _generate_content(self, idx):
        topics = [
            "machine learning algorithms",
            "climate change impacts",
            "financial investment strategies",
            "sustainable energy solutions"
        ]
        aspects = [
            "neural network architectures",
            "carbon footprint reduction",
            "portfolio diversification",
            "renewable energy efficiency"
        ]
        context = [
            "software development projects",
            "environmental policy making",
            "personal financial planning",
            "green technology adoption"
        ]
        return f"Can you explain {topics[idx % 4]} with focus on {aspects[idx % 4]} and its importance in {context[idx % 4]}?"

    def _apply_errors(self, content, density, error_types, errors_applied):
        result = content
        for et in error_types:
            if et == ErrorType.TYPO:
                result = result.replace("algorithm", "algoritm", 1)
                errors_applied.append("typo")
            elif et == ErrorType.GRAMMAR:
                result = result.replace("its importance", "it importance", 1)
                errors_applied.append("grammar")
            elif et == ErrorType.ARTICLE_OMISSION:
                result = re.sub(r"\b(the|a|an)\b", "", result, count=1, flags=re.IGNORECASE)
                errors_applied.append("article_omission")
        return result

    def _remove_article_from_content(self, content):
        return re.sub(r"\b(the|a|an)\b", "", content, count=1, flags=re.IGNORECASE)