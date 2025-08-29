from typing import List

from twinrad.groups.common.base_group import BaseGroupChat
from twinrad.schemas.messages import Message


class GenericGroupChat(BaseGroupChat):

    def add_message(self, message: Message):
        """Adds a message to the chat history and increments the round count."""
        self._messages.append(message)

    def get_messages(self) -> List[Message]:
        """Returns the full conversation history."""
        return self._messages
