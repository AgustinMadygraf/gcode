"""
Base interface for CLI operations (Command pattern).
"""
from abc import ABC, abstractmethod

class CliOperation(ABC):
    @abstractmethod
    def execute(self):
        pass
