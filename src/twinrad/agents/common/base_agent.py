from abc import ABC, abstractmethod
from typing import List

from twinrad.configs.logging_config import setup_logging
from twinrad.schemas.agents import AgentConfig
from twinrad.schemas.messages import Message
from twinrad.clients.client_manager import ClientManager
from twinrad.schemas.clients import LLMRequest, LLMResponse


class BaseAgent(ABC):
    """
    Base class for all agents in the Twinrad system, using AutoGen's ConversableAgent as the foundation.

    This class provides a shared logging setup and a consistent initialization pattern.
    The agent's specific behavior should be defined in subclasses by implementing their
    role within an AutoGen GroupChat or other conversational flows.
    """
    def __init__(self, config: AgentConfig):

        if config.system_message is not None:
            self.system_message = config.system_message
        else:
            self.system_message = self.get_system_message(config)

        self.config = config
        self.client_manager = ClientManager(config=self.config.client)
        self.logger = setup_logging(name=f"[{self.name}]")
        self.logger.info(f"Agent '{self.name}' initialized.")

    @property
    def model(self) -> str:
        return self.config.model

    @property
    def name(self) -> str:
        return self.config.name

    def generate(self, messages: List[Message]) -> Message:

        request = LLMRequest(
            model=self.model,
            messages=messages,
            system_message=self.system_message,
        )
        response: LLMResponse = self.client_manager.generate(request)

        return Message(role='user', content=response.text, name=self.name)

    @abstractmethod
    def get_system_message(self, config: AgentConfig) -> str:
        """
        An abstract method that must be overridden by all subclasses.
        It should return the system message based on the LLM configuration.
        """
        pass
