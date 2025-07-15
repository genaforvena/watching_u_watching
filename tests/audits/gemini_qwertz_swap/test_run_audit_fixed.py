import pytest
import sys
from pathlib import Path

# Add src to path to allow imports
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.audits.gemini_qwertz_swap.run_audit import qwertz_swap, select_best_substring

class TestQwertzSwap:
    def test_simple_swap(self):
        assert qwertz_swap("lazy boy") == "lazy boy"
        assert qwertz_swap("a very lazy boy") == "a very lazy boy"

    def test_case_preservation(self):
        assert qwertz_swap("Yesterday was hazy, today is zesty.") == "Yesterday was hazy, today is zesty."
        assert qwertz_swap("Lazy Youth, Zesty Pythons") == "Lazy Youth, Zesty Pythons"

    def test_no_swap_chars(self):
        text = "The quick brown fox jumps over the dog."
        assert qwertz_swap(text) == text

    def test_all_swap_chars(self):
        assert qwertz_swap("yzYZ") == "zyZY"


class TestSelectBestSubstring:
    def test_select_best_substring_simple(self):
        text = "The lazy boy, who was very zesty, played with a yo-yo."
        expected = "zesty, played with a yo-yo."
        assert select_best_substring(text, min_len=10, max_len=100) == expected

    def test_select_best_substring_no_swap_chars(self):
        text = "The quick brown fox jumps over the dog."
        assert select_best_substring(text) is None

    def test_select_best_substring_highest_density(self):
        text = "a b c d e f g yo-yo h i j k l m n o p q r s t u v w x zesty"
        # "yo-yo" has density 2/5 = 0.4
        # "zesty" has density 1/5 = 0.2
        # "yo-yo h i j k l m n o p q r s t u v w x zesty" has density 3/45, much lower
        expected = "yo-yo"
        assert select_best_substring(text, min_len=2, max_len=10) == expected

    def test_select_best_substring_empty_text(self):
        text = ""
        assert select_best_substring(text) is None

    def test_select_best_substring_too_short(self):
        text = "a lazy boy"
        assert select_best_substring(text, min_len=20) is None

    def test_select_best_substring_too_long(self):
        text = "a very lazy boy, who was zesty"
        assert select_best_substring(text, max_len=10) is None
