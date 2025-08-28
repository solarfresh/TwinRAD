from abc import ABC, abstractmethod
from typing import Dict, List

from autogen.agentchat import ConversableAgent

from twinrad.configs.logging_config import setup_logging
from twinrad.schemas.agents import AgentConfig
from twinrad.schemas.messages import Message


class BaseAgent(ConversableAgent, ABC):
    """
    Base class for all agents in the Twinrad system, using AutoGen's ConversableAgent as the foundation.

    This class provides a shared logging setup and a consistent initialization pattern.
    The agent's specific behavior should be defined in subclasses by implementing their
    role within an AutoGen GroupChat or other conversational flows.
    """
    def __init__(self, config: AgentConfig, **kwargs):

        if config.system_message is not None:
            system_message = config.system_message.get('content', '')
        else:
            system_message = self.get_system_message(config)

        super().__init__(
            name=config.name,
            system_message=system_message,
            llm_config=config.llm_config,
            **kwargs
        )

        self.logger = setup_logging(name=f"[{self.name}]")
        self.logger.info(f"Agent '{self.name}' initialized.")

    def generate(self, messages: List[Message]) -> Message:
        return Message(role='system', content='NotImplemented', name=self.name)

    @abstractmethod
    def get_system_message(self, config: AgentConfig) -> str:
        """
        An abstract method that must be overridden by all subclasses.
        It should return the system message based on the LLM configuration.
        """
        pass
