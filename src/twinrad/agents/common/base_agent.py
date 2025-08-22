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
        system_message: str = "You are a helpful AI Assistant.",
        system_message_content: str | None = None,
        system_message_role: str | None = None,
        **kwargs
    ):
        super().__init__(
            name=agent_name,
            llm_config=llm_config,
            **kwargs
        )
        self.update_system_message(system_message, system_message_content, system_message_role)
        self.logger = setup_logging(name=f"[{self.name}]")
        self.logger.info(f"Agent '{self.name}' initialized.")

    def update_system_message(
        self,
        system_message: str,
        system_message_content: str | None = None,
        system_message_role: str | None = None,
    ) -> None:
        """
        Update the system message for the agent.

        Args:
            system_message (str): The new system message to set if system_message_content is not provided.
            system_message_content (str | None): Optional specific content for the system message.
            system_system_message_role (str | None): Optional specific role for the system message.
        """

        if system_message_content is not None:
            self._oai_system_message[0]["content"] = system_message_content
        else:
            default_system_message = self.get_default_system_message_content()
            if default_system_message:
                self._oai_system_message[0]["content"] = self.get_default_system_message_content()
            else:
                self._oai_system_message[0]["content"] = system_message

        if system_message_role is not None:
            self._oai_system_message[0]["role"] = system_message_role

    def get_default_system_message_content(self) -> str:
        return ''