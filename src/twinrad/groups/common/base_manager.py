from abc import ABC, abstractmethod
from typing import List

from twinrad.agents.common.base_agent import BaseAgent
from twinrad.configs.logging_config import setup_logging
from twinrad.groups.common.base_group import BaseGroupChat
from twinrad.schemas.groups import RoomConfig
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
    async def initiate_chat(self, sender: BaseAgent, message: str | Message) -> List[Message]:
        """
        Abstract method to initiate and manage the conversation flow.
        Subclasses must implement the chat orchestration logic.
        """
        pass

    @abstractmethod
    async def run_chat(self) -> List[Message]:
        """
        Abstract method that contains the main chat execution loop.
        It runs the conversation until the termination condition is met.
        """
        pass


class BaseRoom(ABC):
    group_chat: BaseGroupChat
    terminator: TerminationCondition
    workflow: BaseFlow

    def __init__(self, config: RoomConfig) -> None:
        self.config = config
        self.logger = setup_logging(name=f"[{self.config.name}]")
        self.logger.info(f"Room Manager '{self.config.name}' initialized.")

    async def initiate_chat(self, message: str | Message, sender: BaseAgent | None = None) -> List[Message]:
        """Initiates and manages the conversation flow."""
        # 1. Initialize the chat
        if isinstance(message, str):
            first_message = Message.model_validate({
                "role": "user",
                "content": message,
                "name": 'User' if sender is None else sender.name
            })
        else:
            first_message = message

        self.group_chat.add_message(first_message)
        self.current_round = 1

        # 2. Start the main chat loop
        return await self.run_chat()

    async def run_chat(self) -> List[Message]:
        """
        Runs the main chat execution loop until the termination condition is met.
        """
        response = self.group_chat.messages[-1]
        while not self.terminator.should_end(response, self.current_round):
            try:
                self.logger.debug(f"--- Round {self.current_round} ---")
                # 1. Select the next speaker
                speaker = self.workflow.select_speaker(
                    messages=self.group_chat.chat_history
                )

                self.logger.debug(f"[{speaker.name}] is generating a response...")

                # Re-define roles for the speaker to respond appropriately
                messages = self.define_speak_roles(speaker, self.group_chat.messages)

                # Get a response from the speaker
                response = await speaker.generate(messages)

                self.logger.info(f"[{speaker.name}] {response.content}")

                # Add the response to the history
                self.group_chat.add_message(response)
                self.current_round += 1
            except Exception as e:
                self.logger.error(f"An error occurred during chat round {self.current_round}: {e}")
                # Decide on a recovery strategy here, e.g., break, continue, or retry
                break

        # Return the final messages
        return self.group_chat.messages

    def define_speak_roles(self, recipient: BaseAgent, messages: List[Message]) -> List[Message]:
        redefined_messages = []
        for message in messages[-(self.config.turn_limit + 1):]:
            role = 'assistant' if message.name == recipient.name else 'user'
            redefined_messages.append(Message(role=role, content=message.content, name=message.name))

        return redefined_messages
