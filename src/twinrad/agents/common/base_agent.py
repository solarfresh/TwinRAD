from autogen import LLMConfig
from autogen.agentchat import ConversableAgent

from twinrad.configs.logging_config import setup_logging


class BaseAgent(ConversableAgent):
    """
    Base class for all agents in the Twinrad system, using AutoGen's ConversableAgent as the foundation.

    This class provides a shared logging setup and a consistent initialization pattern.
    The agent's specific behavior should be defined in subclasses by implementing their
    role within an AutoGen GroupChat or other conversational flows.
    """
    def __init__(
        self,
        agent_name: str,
        llm_config: LLMConfig | None = None,
        system_message: str | list | None = "You are a helpful AI Assistant.",
        message_role: str = 'system',
        **kwargs
    ):
        super().__init__(
            name=agent_name,
            llm_config=llm_config,
            system_message=system_message,
            **kwargs
        )
        self.logger = setup_logging(name=f"[{self.name}]")
        self.logger.info(f"Agent '{self.name}' initialized.")
        self._oai_system_message = [{"content": system_message, "role": message_role}]
