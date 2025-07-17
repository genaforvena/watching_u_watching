import logging
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BaseGenerator(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def reply(self, prompt: str, max_length: int) -> str:
        pass
