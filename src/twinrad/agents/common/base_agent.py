import json
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, Dict, List

from twinrad.clients.client_manager import ClientManager
from twinrad.configs.logging_config import setup_logging
from twinrad.schemas.agents import AgentConfig
from twinrad.schemas.clients import LLMRequest, LLMResponse
from twinrad.schemas.messages import Message
from twinrad.tools.common.base_tool import BaseTool, ToolConfig


class BaseAgent(ABC):
    """
    Base class for all agents in the Twinrad system, using AutoGen's ConversableAgent as the foundation.

    This class provides a shared logging setup and a consistent initialization pattern.
    The agent's specific behavior should be defined in subclasses by implementing their
    role within an AutoGen GroupChat or other conversational flows.
    """

    tool: BaseTool | None = None

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
        copied_messages = [deepcopy(msg) for msg in messages]
        last_message = copied_messages[-1]

        try:
            if self.config.tool_use:
                tool_output_message = await self.generate_tool_message(copied_messages)
                return tool_output_message

            cot_to_append = self.config.cot_message or self._message_mapper(self.get_cot_message_map())
            if cot_to_append:
                last_message.content += f"\n\n{cot_to_append}"

            request = LLMRequest(
                model=self.model,
                messages=copied_messages,
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

    async def generate_tool_message(self, messages: List[Message]) -> Message:

        tool_message = self._message_mapper(self.get_tool_message_map())
        tool_call_data: Dict[str, Any] = {}

        if tool_message is not None:
            try:
                request = LLMRequest(
                    model=self.model,
                    messages=messages,
                    system_message=tool_message,
                )
                response: LLMResponse = await self.client_manager.generate(request)
                tool_call_data = self.postprocess_tool_output(response.text)
            except Exception as e:
                self.logger.error(f"Error processing tool message from LLM: {e}")
                return Message(role='assistant', content="Error: Failed to process tool call.", name=self.name)
        else:
            tool_call_data  = self.get_tool_call()

        tool_name = tool_call_data.get('tool', 'default')
        tool = self.get_tool_map()[tool_name]

        if tool is None:
            self.logger.warning(f"No tool found for tool call: '{tool_name}'")
            return Message(role='assistant', content=f"Error: Tool '{tool_name}' not available.", name=self.name)

        try:
            tool_output = await tool.run(**tool_call_data.get("args", {}))
            return Message(role='assistant', content=tool_output, name=self.name)
        except Exception as e:
            self.logger.error(f"Error executing tool '{tool_name}': {e}")
            return Message(role='assistant', content=f"Error: Failed to execute tool '{tool_name}'.", name=self.name)

    @abstractmethod
    def get_system_message_map(self) -> Dict[str, str]:
        """
        Abstract method to be implemented by subclasses to provide a mapping of model families
        to their respective system messages.
        """
        pass

    def get_tool_map(self) -> Dict[str, BaseTool | None]:
        return {'default': None}

    def get_cot_message_map(self) -> Dict[str, str] | None:
        """
        Method to be optionally overridden by subclasses to provide a mapping of model families
        to their respective chain-of-thought (CoT) messages.
        """
        return None

    def get_tool_call(self) -> Dict[str, Any]:
        return {}

    def get_tool_message_map(self) -> Dict[str, str] | None:
        """
        Method to be optionally overridden by subclasses to provide a mapping of model families
        to their respective tool-use messages.
        """
        return None

    def _message_mapper(self, msg_map: Dict[str, str] | None) -> str | None:
        if msg_map is None:
            return None

        return msg_map.get(self.config.lang, 'default')

    def postprocess_tool_output(self, output_string: str) -> Dict[str, Any]:
        return json.loads(output_string.replace('```json', '').replace('```', '').strip())
