from abc import ABC, abstractmethod
from typing import List

from twinrad.agents.common.base_agent import BaseAgent
from twinrad.schemas.messages import Message


class BaseGroupChat(ABC):
    def __init__(self, agents: List[BaseAgent]):
        """
        Base class for managing a group chat among multiple agents.
        """
        self._agents = agents
        # All messages ever sent in this chat session
        self._chat_history: List[Message] = []
        # Current session messages visible to all agents
        self._messages: List[Message] = []

        self._size = len(agents)

    @property
    def agents(self) -> List[BaseAgent]:
        """Returns the list of agents in the chat."""
        return self._agents

    @property
    def chat_history(self) -> List[Message]:
        """Returns the full chat history."""
        return self._chat_history

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
