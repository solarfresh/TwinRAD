from typing import List

from twinrad.agents.common.base_agent import BaseAgent
from twinrad.groups.common.base_manager import BaseGroupManager
from twinrad.schemas.messages import Message


class GenericGroupManager(BaseGroupManager):

    def initiate_chat(self, recipient: BaseAgent, message: str | Message):
        """Initiates and manages the conversation flow."""
        self.logger.debug(f'recipient: {recipient}')
        self.logger.debug(f'recipient.name: {recipient.name}')
        self.logger.debug(f'message: {message}')
        # 1. Initialize the chat
        if isinstance(message, str):
            first_message = Message.model_validate({
                "role": "user",
                "content": message,
                "name": recipient.name
            })
        else:
            first_message = message

        self.group_chat.add_message(first_message)
        self.current_round = 1

        # 2. Start the main chat loop
        return self.run_chat()

    def run_chat(self) -> List[Message]:
        """
        Runs the main chat execution loop until the termination condition is met.
        """
        while not self.terminator.should_end(self.group_chat.messages, self.current_round):
            # 1. Select the next speaker
            speaker = self.workflow.select_speaker(
                messages=self.group_chat.messages
            )

            # 2. Get a response from the speaker
            response = speaker.generate(self.group_chat.messages, sender=speaker)

            # 3. Add the response to the history
            self.group_chat.add_message(response)
            self.current_round += 1

        # 4. Return the final messages
        return self.group_chat.messages