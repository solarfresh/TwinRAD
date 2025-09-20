from abc import ABC, abstractmethod
from typing import Dict, List

from twinrad.core.agents.base_agent import BaseAgent
from twinrad.core.groups.common.base_group import BaseGroupChat
from twinrad.core.schemas.messages import Message


class BaseFlow(ABC):
    def __init__(self, group_chat: BaseGroupChat):
        self.group_chat = group_chat
        self._agent_index_map: Dict[str, int] = {
            agent.name: idx for idx, agent in enumerate(self.group_chat.agents)
        }

    @abstractmethod
    def select_speaker(self, messages: List[Message]) -> BaseAgent:
        pass

    @property
    def agent_index_map(self):
        return self._agent_index_map


class SequentialFlow(BaseFlow):

    def select_speaker(self, messages: List[Message]) -> BaseAgent:
        """
        Selects the next speaker using a round-robin strategy.

        Args:
            messages (List[Message]): The conversation history (not used in this simple strategy).

        Returns:
            BaseAgent: The next agent to speak.
        """
        if not messages:
            return self.group_chat.agents[0]

        last_message = messages[-1]
        last_speaker_index = self._agent_index_map[last_message.name]
        next_speaker_index = (last_speaker_index + 1) % self.group_chat.size

        return self.group_chat.agents[next_speaker_index]