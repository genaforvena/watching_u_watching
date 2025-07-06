# error_injector.py
"""
Linguistic Error Injection Module for Bad English Bias Detection

This module provides systematic injection of controlled linguistic errors while
preserving semantic meaning. Errors are categorized into typos, grammar mistakes,
and non-standard phrasing patterns.
"""

import random
import re
from typing import List, Tuple, Dict
from enum import Enum


class ErrorType(Enum):
    TYPO = "typo"
    GRAMMAR = "grammar" 
    NON_STANDARD = "non_standard"


class ErrorDensity(Enum):
    LOW = "low"      # 1-2 errors per 100 words
    MEDIUM = "medium"  # 3-5 errors per 100 words
    HIGH = "high"    # 6-8 errors per 100 words


class ErrorInjector:
    """Injects controlled linguistic errors while preserving semantic meaning."""
    
    def __init__(self, seed: int = 42):
        """Initialize with deterministic randomization for reproducibility."""
        self.random = random.Random(seed)  # Use instance-specific random state
        self._init_error_patterns()
    
    def _init_error_patterns(self):
        """Initialize error pattern dictionaries."""
        
        # Common typo patterns (character-level errors)
        self.typo_patterns = {
            # Common character swaps
            'receive': 'recieve',
            'achieve': 'acheive', 
            'believe': 'beleive',
            'separate': 'seperate',
            'definitely': 'definately',
            'occurred': 'occured',
            'accommodation': 'accomodation',
            'necessary': 'neccessary',
            'opportunity': 'oportunity',
            'experience': 'experiance',
            'business': 'bussiness',
            'professional': 'proffessional',
            'successful': 'sucessful',
            'environment': 'enviroment',
            'development': 'developement',
            'management': 'managment',
            'knowledge': 'knowlege',
            'through': 'trough',
            'although': 'altough',
            'because': 'becuase'
        }
        
        # Grammar error patterns
        self.grammar_patterns = [
            # Subject-verb disagreement
            (r'\bi am\b', 'i are', 0.3),
            (r'\bhe have\b', 'he has', 0.4),
            (r'\bshe have\b', 'she has', 0.4),
            (r'\bit have\b', 'it has', 0.4),
            (r'\bthey has\b', 'they have', 0.4),
            (r'\bwe has\b', 'we have', 0.4),
            (r'\byou has\b', 'you have', 0.4),
            
            # Article errors
            (r'\ba university\b', 'an university', 0.3),
            (r'\ban unique\b', 'a unique', 0.3),
            (r'\ba hour\b', 'an hour', 0.2),
            (r'\ba honest\b', 'an honest', 0.2),
            
            # Tense errors
            (r'\bi will went\b', 'i will go', 0.3),
            (r'\bi have went\b', 'i have gone', 0.3),
            (r'\bi was went\b', 'i went', 0.3),
            
            # Preposition errors
            (r'\bon the morning\b', 'in the morning', 0.3),
            (r'\bin monday\b', 'on monday', 0.3),
            (r'\bat the night\b', 'at night', 0.2),
        ]
        
        # Non-standard phrasing (L2 patterns that maintain clarity)
        self.non_standard_patterns = [
            # Word order variations
            (r'\bvery much\b', 'much very', 0.2),
            (r'\bmore better\b', 'better', 0.3),
            (r'\bmost best\b', 'best', 0.3),
            
            # Redundant constructions
            (r'\bplease kindly\b', 'kindly please', 0.2),
            (r'\bmay i can\b', 'can i', 0.3),
            (r'\bi am having\b', 'i have', 0.2),
            
            # Literal translations
            (r'\bmake a travel\b', 'travel', 0.3),
            (r'\bdo a mistake\b', 'make a mistake', 0.3),
            (r'\bsay a lie\b', 'tell a lie', 0.3),
        ]

    def inject_typos(self, text: str, density: ErrorDensity) -> Tuple[str, List[str]]:
        """Inject typos based on common misspelling patterns."""
        errors_applied = []
        words = text.split()
        target_errors = self._calculate_target_errors(len(words), density, ErrorType.TYPO)
        
        # Apply typo patterns
        for original, typo in self.typo_patterns.items():
            if target_errors <= 0:
                break
            if original in text.lower():
                # Case-preserving replacement
                pattern = re.compile(re.escape(original), re.IGNORECASE)
                matches = list(pattern.finditer(text))
                if matches and self.random.random() < 0.7:  # 70% chance to apply
                    match = self.random.choice(matches)
                    original_case = text[match.start():match.end()]
                    typo_case = self._preserve_case(original_case, typo)
                    text = text[:match.start()] + typo_case + text[match.end():]
                    errors_applied.append(f"Typo: {original_case} → {typo_case}")
                    target_errors -= 1
        
        # Apply additional character-level typos if needed
        if target_errors > 0:
            text, additional_errors = self._inject_character_typos(text, target_errors)
            errors_applied.extend(additional_errors)
        
        return text, errors_applied

    def inject_grammar_errors(self, text: str, density: ErrorDensity) -> Tuple[str, List[str]]:
        """Inject grammar errors while preserving meaning."""
        errors_applied = []
        words = text.split()
        target_errors = self._calculate_target_errors(len(words), density, ErrorType.GRAMMAR)
        
        for pattern, replacement, probability in self.grammar_patterns:
            if target_errors <= 0:
                break
            if self.random.random() < probability:
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                if matches:
                    match = self.random.choice(matches)
                    original = text[match.start():match.end()]
                    # Preserve case
                    replacement_case = self._preserve_case(original, replacement)
                    text = text[:match.start()] + replacement_case + text[match.end():]
                    errors_applied.append(f"Grammar: {original} → {replacement_case}")
                    target_errors -= 1
        
        return text, errors_applied

    def inject_non_standard_phrasing(self, text: str, density: ErrorDensity) -> Tuple[str, List[str]]:
        """Inject non-standard phrasing patterns."""
        errors_applied = []
        words = text.split()
        target_errors = self._calculate_target_errors(len(words), density, ErrorType.NON_STANDARD)
        
        for pattern, replacement, probability in self.non_standard_patterns:
            if target_errors <= 0:
                break
            if self.random.random() < probability:
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                if matches:
                    match = self.random.choice(matches)
                    original = text[match.start():match.end()]
                    replacement_case = self._preserve_case(original, replacement)
                    text = text[:match.start()] + replacement_case + text[match.end():]
                    errors_applied.append(f"Non-standard: {original} → {replacement_case}")
                    target_errors -= 1
        
        return text, errors_applied

    def inject_mixed_errors(self, text: str, density: ErrorDensity) -> Tuple[str, List[str]]:
        """Inject a mix of all error types."""
        all_errors = []
        
        # Distribute errors across types
        typo_text, typo_errors = self.inject_typos(text, density)
        grammar_text, grammar_errors = self.inject_grammar_errors(typo_text, density)
        final_text, ns_errors = self.inject_non_standard_phrasing(grammar_text, density)
        
        all_errors.extend(typo_errors)
        all_errors.extend(grammar_errors)
        all_errors.extend(ns_errors)
        
        return final_text, all_errors

    def _calculate_target_errors(self, word_count: int, density: ErrorDensity, error_type: ErrorType) -> int:
        """Calculate target number of errors based on word count and density."""
        if density == ErrorDensity.LOW:
            base_rate = self.random.uniform(0.01, 0.02)  # 1-2 errors per 100 words
        elif density == ErrorDensity.MEDIUM:
            base_rate = self.random.uniform(0.03, 0.05)  # 3-5 errors per 100 words
        else:  # HIGH
            base_rate = self.random.uniform(0.06, 0.08)  # 6-8 errors per 100 words
        
        # Adjust rate by error type (some are more common)
        if error_type == ErrorType.TYPO:
            base_rate *= 1.0  # Typos are most common
        elif error_type == ErrorType.GRAMMAR:
            base_rate *= 0.7  # Grammar errors less frequent
        else:  # NON_STANDARD
            base_rate *= 0.5  # Non-standard phrasing least frequent
        
        return max(1, int(word_count * base_rate))

    def _preserve_case(self, original: str, replacement: str) -> str:
        """Preserve the case pattern of the original text."""
        if original.isupper():
            return replacement.upper()
        elif original.islower():
            return replacement.lower()
        elif original.istitle():
            return replacement.title()
        else:
            # Try to match case pattern more precisely
            result = []
            for i, char in enumerate(replacement):
                if i < len(original):
                    if original[i].isupper():
                        result.append(char.upper())
                    else:
                        result.append(char.lower())
                else:
                    result.append(char.lower())
            return ''.join(result)

    def _inject_character_typos(self, text: str, target_errors: int) -> Tuple[str, List[str]]:
        """Inject character-level typos when word-level patterns aren't available."""
        errors_applied = []
        words = text.split()
        
        for _ in range(target_errors):
            if not words:
                break
                
            # Select a random word to modify
            word_idx = self.random.randint(0, len(words) - 1)
            word = words[word_idx]
            
            if len(word) < 3:  # Skip very short words
                continue
                
            # Apply character-level errors
            char_idx = self.random.randint(1, len(word) - 2)  # Avoid first/last chars
            original_word = word
            
            error_type = self.random.choice(['swap', 'omit', 'duplicate'])
            
            if error_type == 'swap' and char_idx < len(word) - 1:
                # Swap adjacent characters
                chars = list(word)
                chars[char_idx], chars[char_idx + 1] = chars[char_idx + 1], chars[char_idx]
                word = ''.join(chars)
            elif error_type == 'omit':
                # Omit a character
                word = word[:char_idx] + word[char_idx + 1:]
            elif error_type == 'duplicate':
                # Duplicate a character
                word = word[:char_idx + 1] + word[char_idx] + word[char_idx + 1:]
            
            if word != original_word:
                words[word_idx] = word
                errors_applied.append(f"Char-typo: {original_word} → {word}")
        
        return ' '.join(words), errors_applied

    def validate_semantic_preservation(self, original: str, modified: str) -> bool:
        """Basic validation that semantic meaning is preserved."""
        # Simple heuristics for semantic preservation
        original_words = set(original.lower().split())
        modified_words = set(modified.lower().split())
        
        # Calculate word overlap (should be high for preserved semantics)
        overlap = len(original_words.intersection(modified_words))
        total_unique = len(original_words.union(modified_words))
        
        overlap_ratio = overlap / total_unique if total_unique > 0 else 0
        
        # Semantic preservation criteria
        return (
            overlap_ratio > 0.7 and  # At least 70% word overlap
            abs(len(original.split()) - len(modified.split())) <= 2 and  # Similar length
            len(modified.strip()) > 0  # Not empty
        )


if __name__ == "__main__":
    # Example usage and testing
    injector = ErrorInjector()
    
    test_text = "I am writing to express my interest in the software developer position. I have experience in programming and believe I would be a valuable addition to your team."
    
    print("Original text:")
    print(test_text)
    print("\n" + "="*50 + "\n")
    
    for density in ErrorDensity:
        print(f"--- {density.value.upper()} DENSITY ---")
        
        # Test each error type
        typo_text, typo_errors = injector.inject_typos(test_text, density)
        print(f"Typos applied: {typo_errors}")
        print(f"Result: {typo_text}")
        print(f"Semantic preserved: {injector.validate_semantic_preservation(test_text, typo_text)}")
        print()
        
        grammar_text, grammar_errors = injector.inject_grammar_errors(test_text, density)
        print(f"Grammar errors: {grammar_errors}")
        print(f"Result: {grammar_text}")
        print(f"Semantic preserved: {injector.validate_semantic_preservation(test_text, grammar_text)}")
        print()
        
        mixed_text, mixed_errors = injector.inject_mixed_errors(test_text, density)
        print(f"Mixed errors: {mixed_errors}")
        print(f"Result: {mixed_text}")
        print(f"Semantic preserved: {injector.validate_semantic_preservation(test_text, mixed_text)}")
        print("\n" + "="*50 + "\n")