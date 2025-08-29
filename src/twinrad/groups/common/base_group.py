from abc import ABC, abstractmethod
from typing import List

from twinrad.agents.common.base_agent import BaseAgent
from twinrad.workflows.common.base_flow import BaseFlow
from twinrad.workflows.common.termination import TerminationCondition
from twinrad.schemas.messages import Message


class BaseGroupChat(ABC):
    def __init__(self, agents: List[BaseAgent]):
        self._agents = agents
        self._messages: List[Message] = []

    @property
    def agents(self) -> List[BaseAgent]:
        """Returns the list of agents in the chat."""
        return self._agents

    @property
    def messages(self) -> List[Message]:
        """Returns the conversation history."""
        return self._messages

    @abstractmethod
    def add_message(self, message: Message):
        pass

    @abstractmethod
    def get_messages(self) -> List[Message]:
        pass


class BaseGroupManager(ABC):
    def __init__(
        self,
        group_chat: BaseGroupChat,
        workflow: BaseFlow,
        terminator: TerminationCondition
    ):
        self.group_chat = group_chat
        self.workflow = workflow
        self.terminator = terminator
        self.current_round = 0

    @abstractmethod
    def initiate_chat(self, recipient: BaseAgent, message: str | Message):
        """
        Abstract method to initiate and manage the conversation flow.
        Subclasses must implement the chat orchestration logic.
        """
        pass

    @abstractmethod
    def run_chat(self) -> List[Message]:
        """
        Abstract method that contains the main chat execution loop.
        It runs the conversation until the termination condition is met.
        """
        pass
