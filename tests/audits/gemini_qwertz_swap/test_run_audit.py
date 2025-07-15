import pytest
import sys
from pathlib import Path

# Add src to path to allow imports
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.audits.gemini_qwertz_swap.run_audit import qwertz_swap

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
