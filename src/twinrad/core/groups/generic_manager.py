from typing import List

from twinrad.core.agents.base_agent import BaseAgent
from twinrad.core.groups.base_manager import BaseGroupManager
from twinrad.core.schemas.messages import Message


class GenericGroupManager(BaseGroupManager):

    async def initiate_chat(self, sender: BaseAgent, message: str | Message) -> List[Message]:
        """Initiates and manages the conversation flow."""
        self.logger.debug(f'recipient: {sender}')
        self.logger.debug(f'recipient.name: {sender.name}')
        self.logger.debug(f'message: {message}')
        # 1. Initialize the chat
        if isinstance(message, str):
            first_message = Message.model_validate({
                "role": "user",
                "content": message,
                "name": sender.name
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
            # 1. Select the next speaker
            speaker = self.workflow.select_speaker(
                messages=self.group_chat.messages
            )

            # 2. Get a response from the speaker
            response = await speaker.generate(self.group_chat.messages)

            self.logger.debug(f"[{speaker.name}] {response.content}")

            # 3. Add the response to the history
            self.group_chat.add_message(response)
            self.current_round += 1

        # 4. Return the final messages
        return self.group_chat.messages