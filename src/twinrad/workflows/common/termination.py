from abc import ABC, abstractmethod
from typing import Dict, List

from twinrad.schemas.messages import Message


class TerminationCondition(ABC):
    @abstractmethod
    def should_end(self, messages: List[Message], current_round: int) -> bool:
        pass
