import logging
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BasePerturbator(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def generate_rule(self, successful_prompts: list, carlini_hit_list: list) -> str:
        pass

    @abstractmethod
    def apply_rule(self, base_prompt: str, rule_str: str) -> str:
        pass
