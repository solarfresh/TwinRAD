import json
import re
from typing import List

from twinrad.agents.common.base_agent import BaseAgent
from twinrad.groups.common.base_group import BaseGroupChat
from twinrad.schemas.agents import DeceptiveAgentName
from twinrad.schemas.messages import Message


class DebateGroupChat(BaseGroupChat):

    def __init__(self, agents: List[BaseAgent]):
        super().__init__(agents=agents)
        self._chain_of_thoughts: List[Message] = []

    def add_message(self, message: Message):
        """Adds a message to the chat history and increments the round count."""
        self._chat_history.append(message)
        if not message.name == DeceptiveAgentName.REFEREE_AGENT.value:
            self._parse_message(message)

    @property
    def chain_of_thoughts(self):
        return self._chain_of_thoughts

    def _parse_message(self, message: Message):
        content = message.content
        split_string_list = re.split(r"final\s*response:?[\s#]*", content, flags=re.IGNORECASE)
        self._messages.append(Message(role=message.role, content=split_string_list[-1], name=message.name))
        self._chain_of_thoughts.append(Message(
            role=message.role,
            content=self._parse_chain_of_thoughts(''.join(split_string_list[:-1])),
            name=message.name
        ))

    def _parse_chain_of_thoughts(self, chain_of_thoughts: str) -> str:
        pattern = re.compile(r'(?:\d+\.\s+\*\*(.*?)\*\*:?|##\s*\d*:?\s*(.*?))\s*(.*?)(?=\n(?:\d+\.|##)|\Z)', re.DOTALL)

        thoughts = []
        for match in pattern.finditer(chain_of_thoughts):
            title = match.group(1) or match.group(2)
            content = match.group(3)
            # Clean up the content by replacing newlines and redundant spaces
            if title and content:
                cleaned_title = title.strip()
                cleaned_content = re.sub(r'\s+', ' ', content).replace('\\n', ' ').strip()
                thoughts.append({cleaned_title: cleaned_content})

        return json.dumps(thoughts)
