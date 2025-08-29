from abc import ABC, abstractmethod
from typing import Dict, List

from twinrad.schemas.messages import Message


class TerminationCondition(ABC):
    @abstractmethod
    def should_end(self, messages: List[Message], current_round: int) -> bool:
        pass


class MaxRoundsCondition(TerminationCondition):
    def __init__(self, max_rounds: int):
        if max_rounds <= 0:
            raise ValueError("max_rounds must be a positive integer.")
        self.max_rounds = max_rounds

    def should_end(self, messages: List[Message], current_round: int) -> bool:
        """
        Returns True if the conversation has reached the maximum number of rounds.

        Args:
            messages (List[Message]): The conversation history (not used in this implementation).
            current_round (int): The current round number.

        Returns:
            bool: True if the conversation should end, False otherwise.
        """
        return current_round >= self.max_rounds