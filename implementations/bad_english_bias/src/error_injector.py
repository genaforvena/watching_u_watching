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
import nltk
from nltk.corpus import wordnet


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
        nltk.download('wordnet', quiet=True)
        nltk.download('omw-1.4', quiet=True)
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

    def inject_article_omission(self, text: str) -> Tuple[str, List[Dict[str, int]]]:
        """
        Removes ALL articles (a, an, the) while preserving:
        - Sentence boundaries
        - Capitalization rules
        - Core semantic meaning
        Returns modified text and list of removed articles with positions
        """
        article_pattern = re.compile(r'\b(a|an|the)\b', re.IGNORECASE)
        removed = []
        offset = 0
        def replacement(match):
            nonlocal offset
            start, end = match.start(), match.end()
            removed.append({'article': match.group(), 'start': start + offset, 'end': end + offset})
            # Adjust offset for subsequent matches
            offset -= (end - start)
            return ''
        # Remove articles and track positions
        new_text = article_pattern.sub(replacement, text)
        # Clean up double spaces and fix capitalization at sentence starts
        new_text = re.sub(r'\s{2,}', ' ', new_text)
        # Capitalize first letter of each sentence if needed
        sentences = re.split(r'([.!?]\s*)', new_text)
        sentences = [s.capitalize() if i % 2 == 0 else s for i, s in enumerate(sentences)]
        new_text = ''.join(sentences).strip()
        return new_text, removed

    def inject_single_letter_perturbation(
        self,
        text: str,
        density: ErrorDensity,
        mode: str = "both"
    ) -> Tuple[str, List[str]]:
        """
        Introduces single-letter changes under constraints:
        - Only words >3 characters affected
        - First/last characters never modified
        - Substitutions use QWERTY adjacency (e.g., e→r/w/s/d)
        - Maintains 100% human readability (pre-test validated)
        Returns modified text and error log
        """
        qwerty_adj = {
            'a': ['q', 'w', 's', 'z'], 'b': ['v', 'g', 'h', 'n'], 'c': ['x', 'd', 'f', 'v'],
            'd': ['s', 'e', 'r', 'f', 'c', 'x'], 'e': ['w', 's', 'd', 'r'], 'f': ['d', 'r', 't', 'g', 'v', 'c'],
            'g': ['f', 't', 'y', 'h', 'b', 'v'], 'h': ['g', 'y', 'u', 'j', 'n', 'b'], 'i': ['u', 'j', 'k', 'o'],
            'j': ['h', 'u', 'i', 'k', 'm', 'n'], 'k': ['j', 'i', 'o', 'l', 'm'], 'l': ['k', 'o', 'p'],
            'm': ['n', 'j', 'k'], 'n': ['b', 'h', 'j', 'm'], 'o': ['i', 'k', 'l', 'p'], 'p': ['o', 'l'],
            'q': ['a', 'w'], 'r': ['e', 'd', 'f', 't'], 's': ['a', 'w', 'e', 'd', 'x', 'z'],
            't': ['r', 'f', 'g', 'y'], 'u': ['y', 'h', 'j', 'i'], 'v': ['c', 'f', 'g', 'b'],
            'w': ['q', 'a', 's', 'e'], 'x': ['z', 's', 'd', 'c'], 'y': ['t', 'g', 'h', 'u'],
            'z': ['a', 's', 'x']
        }
        words = text.split()
        target_errors = self._calculate_target_errors(len(words), density, ErrorType.TYPO)
        error_log = []
        used_indices = set()
        for _ in range(target_errors):
            # Avoid perturbing the same word multiple times in one pass
            available_indices = [i for i, w in enumerate(words) if len(w) > 3 and w.isalpha() and i not in used_indices]
            if not available_indices:
                break
            idx = self.random.choice(available_indices)
            used_indices.add(idx)
            word = words[idx]
            char_idx = self.random.randint(1, len(word) - 2)
            original_word = word
            if mode in ("deletion", "both") and self.random.random() < 0.5:
                perturbed = word[:char_idx] + word[char_idx+1:]
                error_log.append(f"Letter-deletion: {original_word} → {perturbed}")
                words[idx] = perturbed
            elif mode in ("substitution", "both"):
                c = word[char_idx].lower()
                if c in qwerty_adj and qwerty_adj[c]:
                    sub = self.random.choice(qwerty_adj[c])
                    perturbed = word[:char_idx] + sub + word[char_idx+1:]
                    # Preserve original case
                    if word[char_idx].isupper():
                        perturbed = perturbed[:char_idx] + sub.upper() + perturbed[char_idx+1:]
                    error_log.append(f"Letter-substitution: {original_word} → {perturbed}")
                    words[idx] = perturbed
        return ' '.join(words), error_log

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

    def homoglyph_perturbation(self, text: str) -> str:
        """Applies homoglyph substitutions to the text."""
        homoglyphs = {
            'a': 'а',  # Cyrillic а
            'o': 'о',  # Cyrillic о  
            'e': 'е',  # Cyrillic е
            'p': 'р',  # Cyrillic р
            'c': 'с',  # Cyrillic с
            'x': 'х',  # Cyrillic х
            'i': 'і',  # Ukrainian і
            '0': 'О',  # Letter O
            '1': 'l',  # Letter l
        }
        return ''.join(homoglyphs.get(c, c) if self.random.random() < 0.3 else c for c in text)

    def ocr_error_perturbation(self, text: str) -> str:
        """Applies OCR-style errors to the text."""
        ocr_errors = {
            'l': '1', 'I': '1', '1': 'l',
            'O': '0', '0': 'O', 'Q': '0',
            'rn': 'm', 'm': 'rn',
            'cl': 'd', 'ri': 'n',
            'vv': 'w', 'w': 'vv',
            'S': '5', '5': 'S',
            'B': '8', '8': 'B',
        }
        
        result = text
        for error, replacement in ocr_errors.items():
            if self.random.random() < 0.2:  # 20% chance per error type
                result = result.replace(error, replacement)
        return result

    def synonym_perturbation(self, text: str, replacement_rate: float = 0.3) -> str:
        """Replaces words with synonyms using WordNet."""
        words = text.split()
        result = []
        
        for word in words:
            if self.random.random() < replacement_rate:
                synonyms = []
                for syn in wordnet.synsets(word):
                    for lemma in syn.lemmas():
                        synonyms.append(lemma.name().replace('_', ' '))
                
                if synonyms:
                    # Choose a synonym different from original
                    synonym = self.random.choice([s for s in synonyms if s != word])
                    result.append(synonym)
                else:
                    result.append(word)
            else:
                result.append(word)
        
        return ' '.join(result)

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

        # Test new perturbations
        print("--- NEW PERTURBATIONS ---")
        homoglyph_text = injector.homoglyph_perturbation(test_text)
        print(f"Homoglyph Result: {homoglyph_text}")
        print(f"Semantic preserved: {injector.validate_semantic_preservation(test_text, homoglyph_text)}")
        print()

        ocr_text = injector.ocr_error_perturbation(test_text)
        print(f"OCR Error Result: {ocr_text}")
        print(f"Semantic preserved: {injector.validate_semantic_preservation(test_text, ocr_text)}")
        print()

        synonym_text = injector.synonym_perturbation(test_text)
        print(f"Synonym Result: {synonym_text}")
        print(f"Semantic preserved: {injector.validate_semantic_preservation(test_text, synonym_text)}")
        print("\n" + "="*50 + "\n")