import logging
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BaseGenerator(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def generate_text(self, prompt: str, max_length: int) -> str:
        pass
