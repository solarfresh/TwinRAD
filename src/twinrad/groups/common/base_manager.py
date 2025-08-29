from abc import ABC, abstractmethod
from typing import List

from twinrad.configs.logging_config import setup_logging
from twinrad.agents.common.base_agent import BaseAgent
from twinrad.groups.common.base_group import BaseGroupChat
from twinrad.schemas.messages import Message
from twinrad.workflows.common.base_flow import BaseFlow
from twinrad.workflows.common.termination import TerminationCondition


class BaseGroupManager(ABC):
    def __init__(
        self,
        name: str,
        group_chat: BaseGroupChat,
        workflow: BaseFlow,
        terminator: TerminationCondition
    ):
        self.name = name
        self.group_chat = group_chat
        self.workflow = workflow
        self.terminator = terminator
        self.current_round = 0

        self.logger = setup_logging(name=f"[{self.name}]")
        self.logger.info(f"GroupChat Manager '{self.name}' initialized.")

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
