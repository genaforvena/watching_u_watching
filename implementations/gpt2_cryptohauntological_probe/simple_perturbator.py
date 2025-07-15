import logging
from .base_perturbator import BasePerturbator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SimplePerturbator(BasePerturbator):
    def __init__(self):
        super().__init__()
        self.rules = {
            "character_doubling": lambda s: "".join([char * 2 for char in s]),
            "reverse_string": lambda s: s[::-1],
            "zero_width_space": lambda s: "".join([char + '\u200b' for char in s]),
            "caesar_cipher": lambda s: "".join([chr(ord(char) + 3) if 'a' <= char <= 'z' or 'A' <= char <= 'Z' else char for char in s])
        }
        self.rule_names = list(self.rules.keys())
        self.rule_index = 0

    def generate_rule(self, successful_prompts: list, carlini_hit_list: list) -> str:
        # For simple perturbator, we cycle through predefined rules
        rule_name = self.rule_names[self.rule_index]
        self.rule_index = (self.rule_index + 1) % len(self.rule_names)
        logging.info(f"Generated perturbation rule: {rule_name}")
        return rule_name

    def apply_rule(self, base_prompt: str, rule_name: str) -> str:
        if rule_name in self.rules:
            perturbed_prompt = self.rules[rule_name](base_prompt)
            logging.info(f"Applied rule '{rule_name}'. Perturbed prompt: {perturbed_prompt[:50]}...")
            return perturbed_prompt
        else:
            logging.error(f"Unknown perturbation rule: {rule_name}")
            return base_prompt
