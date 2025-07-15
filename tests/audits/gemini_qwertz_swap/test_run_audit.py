import pytest
import sys
from pathlib import Path

# Add src to path to allow imports
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.audits.gemini_qwertz_swap.run_audit import qwertz_swap, select_best_substring

class TestQwertzSwap:
    def test_simple_swap(self):
        assert qwertz_swap("y") == "z"
        assert qwertz_swap("z") == "y"

    def test_case_preservation(self):
        assert qwertz_swap("Y") == "Z"
        assert qwertz_swap("Z") == "Y"

    def test_no_swap_chars(self):
        text = "The quick brown fox jumps over the dog."
        assert qwertz_swap(text) == text

    def test_all_swap_chars(self):
        assert qwertz_swap("yzYZ") == "zyZY"


class TestSelectBestSubstring:
    def test_select_best_substring_simple(self):
        text = "a yo-yo"
        expected = "yo-yo"
        assert select_best_substring(text, min_len=2, max_len=10) == expected

    def test_select_best_substring_no_swap_chars(self):
        text = "The quick brown fox jumps over the dog."
        assert select_best_substring(text) is None

    def test_select_best_substring_highest_density(self):
        text = "a zesty yo-yo"
        expected = "yo-yo"
        assert select_best_substring(text, min_len=2, max_len=10) == expected

    def test_select_best_substring_empty_text(self):
        text = ""
        assert select_best_substring(text) is None

    def test_select_best_substring_too_short(self):
        text = "a y z"
        assert select_best_substring(text, min_len=10) is None

    def test_select_best_substring_too_long(self):
        text = "a very long string with y and z"
        assert select_best_substring(text, max_len=10) == "with y and"
