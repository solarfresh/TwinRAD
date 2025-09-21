from twinrad.core.groups.base_group import BaseGroupChat
from twinrad.core.schemas.messages import Message


class GenericGroupChat(BaseGroupChat):

    def add_message(self, message: Message):
        """Adds a message to the chat history and increments the round count."""
        self._chat_history.append(message)
        self._messages.append(message)
