import random
import string
import logging
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BasePerturbator(ABC):
    @abstractmethod
    def generate_rule(self, successful_prompts, failed_prompts):
        pass

    @abstractmethod
    def apply_rule(self, text, rule_name):
        pass

class SimplePerturbator(BasePerturbator):
    def __init__(self):
        self.rules = {
            "character_doubling": self._character_doubling,
            "reverse_string": self._reverse_string,
            "zero_width_space": self._zero_width_space,
            "caesar_cipher": self._caesar_cipher,
            "uni_mirror": self._uni_mirror,
            "y_z_swap": self._y_z_swap # New rule for Y<->Z swap
        }

    def generate_rule(self, successful_prompts=None, failed_prompts=None):
        # For simple perturbator, we just randomly pick a rule
        rule_name = random.choice(list(self.rules.keys()))
        logging.info(f"Generated rule: {rule_name}")
        return rule_name

    def apply_rule(self, text, rule_name):
        if rule_name in self.rules:
            logging.info(f"Applying rule '{rule_name}' to text: {text[:50]}...")
            return self.rules[rule_name](text)
        else:
            logging.warning(f"Rule '{rule_name}' not found. Returning original text.")
            return text

    def _character_doubling(self, text):
        return "".join([char * 2 for char in text])

    def _uni_mirror(self, text):
        ret_val = text.replace('o', '#TEMP#').replace('o', 'о').replace('#TEMP#', 'о')
        ret_val = text.replace('O', '#TEMP#').replace('O', 'О').replace('#TEMP#', 'О')
        ret_val = text.replace('c', '#TEMP#').replace('c', 'с').replace('#TEMP#', 'с')
        ret_val = text.replace('C', '#TEMP#').replace('C', 'С').replace('#TEMP#', 'С')
        ret_val = text.replace('e', '#TEMP#').replace('e', 'е').replace('#TEMP#', 'е')
        ret_val = text.replace('E', '#TEMP#').replace('E', 'Е').replace('#TEMP#', 'Е')
        ret_val = text.replace('a', '#TEMP#').replace('a', 'а').replace('#TEMP#', 'а')
        ret_val = text.replace('A', '#TEMP#').replace('A', 'А').replace('#TEMP#', 'А')
        ret_val = text.replace('p', '#TEMP#').replace('p', 'р').replace('#TEMP#', 'р')
        ret_val = text.replace('P', '#TEMP#').replace('P', 'Р').replace('#TEMP#', 'Р')
        ret_val = text.replace('x', '#TEMP#').replace('x', 'х').replace('#TEMP#', 'х')
        ret_val = text.replace('X', '#TEMP#').replace('X', 'Х').replace('#TEMP#', 'Х')
        return ret_val


    def _reverse_string(self, text):
        return text[::-1]

    def _zero_width_space(self, text):
        return "".join([char + "\u200B" for char in text])

    def _caesar_cipher(self, text, shift=3):
        result = ""
        for char in text:
            if 'a' <= char <= 'z':
                result += chr(((ord(char) - ord('a') + shift) % 26) + ord('a'))
            elif 'A' <= char <= 'Z':
                result += chr(((ord(char) - ord('A') + shift) % 26) + ord('A'))
            else:
                result += char
        return result

    def _y_z_swap(self, text):
        # This is a simple Y<->Z swap for demonstration.
        # In a real scenario, this might be more complex or context-aware.
        return text.replace('Y', '#TEMP#').replace('Z', 'Y').replace('#TEMP#', 'Z')

if __name__ == "__main__":
    perturbator = SimplePerturbator()
    test_text = "Hello World"

    print(f"Original: {test_text}")
    print(f"Character Doubling: {perturbator.apply_rule(test_text, 'character_doubling')}")
    print(f"Reverse String: {perturbator.apply_rule(test_text, 'reverse_string')}")
    print(f"Zero Width Space: {perturbator.apply_rule(test_text, 'zero_width_space')}")
    print(f"Caesar Cipher: {perturbator.apply_rule(test_text, 'caesar_cipher')}")
    print(f"Y-Z Swap: {perturbator.apply_rule('XYZ', 'y_z_swap')}")