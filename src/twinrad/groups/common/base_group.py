from abc import ABC, abstractmethod
from typing import List

from twinrad.agents.common.base_agent import BaseAgent
from twinrad.schemas.messages import Message


class BaseGroupChat(ABC):
    def __init__(self, agents: List[BaseAgent]):
        self._agents = agents
        self._messages: List[Message] = []

        self._size = len(agents)

    @property
    def agents(self) -> List[BaseAgent]:
        """Returns the list of agents in the chat."""
        return self._agents

    @property
    def messages(self) -> List[Message]:
        """Returns the conversation history."""
        return self._messages

    @property
    def size(self) -> int:
        return self._size

    @abstractmethod
    def add_message(self, message: Message):
        pass

    @abstractmethod
    def get_messages(self) -> List[Message]:
        pass
