from abc import ABC, abstractmethod
from typing import Dict, List

from twinrad.agents.common.base_agent import BaseAgent
from twinrad.schemas.messages import Message


class BaseFlow(ABC):
    @abstractmethod
    def select_speaker(self, agents: List[BaseAgent], messages: List[Message]) -> BaseAgent:
        pass
