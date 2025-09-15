from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Dict, List

from twinrad.clients.client_manager import ClientManager
from twinrad.configs.logging_config import setup_logging
from twinrad.schemas.agents import AgentConfig
from twinrad.schemas.clients import LLMRequest, LLMResponse
from twinrad.schemas.messages import Message


class BaseAgent(ABC):
    """
    Base class for all agents in the Twinrad system, using AutoGen's ConversableAgent as the foundation.

    This class provides a shared logging setup and a consistent initialization pattern.
    The agent's specific behavior should be defined in subclasses by implementing their
    role within an AutoGen GroupChat or other conversational flows.
    """
    def __init__(self, config: AgentConfig, client_manager: ClientManager):

        self.config = config
        self.client_manager = client_manager
        self.logger = setup_logging(name=f"[{self.config.name}]")
        self.logger.info(f"Agent '{self.config.name}' initialized.")
        if config.system_message is not None:
            self.system_message = config.system_message
        else:
            self.system_message = str(self._message_mapper(self.get_system_message_map()))

    @property
    def model(self) -> str:
        return self.config.model

    @property
    def name(self) -> str:
        return self.config.name

    async def generate(self, messages: List[Message]) -> Message:
        try:
            cot_to_append = self.config.cot_message or self._message_mapper(self.get_cot_message_map())
            if cot_to_append:
                messages_with_cot = [deepcopy(msg) for msg in messages]
                last_message = messages_with_cot[-1]
                last_message.content += f"\n\n{cot_to_append}"
            else:
                messages_with_cot = messages

            request = LLMRequest(
                model=self.model,
                messages=messages_with_cot,
                system_message=self.system_message,
            )

            self.logger.debug(f"Sending request to LLM: {request}")
            response: LLMResponse = await self.client_manager.generate(request)

            return Message(role='assistant', content=response.text, name=self.name)
        except Exception as e:
            self.logger.error(f"Error during LLM generation for agent '{self.name}': {e}")
            # Depending on your design, you could return an error message,
            # or raise a custom exception to be handled by the DebateManager.
            return Message(role='assistant', content="Error: Could not generate a response.", name=self.name)

    @abstractmethod
    def get_system_message_map(self) -> Dict[str, str]:
        """
        Abstract method to be implemented by subclasses to provide a mapping of model families
        to their respective system messages.
        """
        pass

    def get_cot_message_map(self) -> Dict[str, str] | None:
        """
        Method to be optionally overridden by subclasses to provide a mapping of model families
        to their respective chain-of-thought (CoT) messages.
        """
        return None

    def _message_mapper(self, msg_map: Dict[str, str] | None) -> str | None:
        if msg_map is None:
            return None

        return msg_map.get(self.config.lang, 'default')
