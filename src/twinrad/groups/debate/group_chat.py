import json
import re
from typing import List, Tuple

from twinrad.agents.common.base_agent import BaseAgent
from twinrad.groups.common.base_group import BaseGroupChat
from twinrad.schemas.agents import DebateAgentName
from twinrad.schemas.messages import Message


class DebateGroupChat(BaseGroupChat):

    def __init__(self, agents: List[BaseAgent]):
        super().__init__(agents=agents)
        self._chain_of_thoughts: List[Message] = []
        self.block_pattern = re.compile(r'(?=\d+\.\s+\*\*.*?\*\*|##?\s*.*?(?=\n))')
        self.title_pattern = re.compile(r'^(?:\d+\.\s+\*\*(.*?)\*\*|##?\s*(.*?)(?:\n|$))', re.DOTALL)
        self.clean_title_pattern = re.compile(r'^\d+\.\s*|\*\*|##?\s*|^\d+:\s*|^Step\s*\d+:\s*')

    def add_message(self, message: Message):
        """Adds a message to the chat history and increments the round count."""
        self._chat_history.append(message)
        if not message.name == DebateAgentName.REFEREE_AGENT.value:
            self._parse_message(message)

    @property
    def chain_of_thoughts(self):
        return self._chain_of_thoughts

    def _parse_message(self, message: Message):
        content = message.content
        self.logger.debug(f"Parsing message content:\n{content}")
        split_string_list = re.split(r"(final\s*response|最終回應):?[\s#]*", content, flags=re.IGNORECASE)
        self._messages.append(Message(role=message.role, content=split_string_list[-1], name=message.name))
        self._chain_of_thoughts.append(Message(
            role=message.role,
            content=self._parse_chain_of_thoughts(''.join(split_string_list[:-1])),
            name=message.name
        ))

    def _parse_chain_of_thoughts(self, chain_of_thoughts: str) -> str:
        self.logger.debug(f"Parsing chain of thoughts:\n{chain_of_thoughts}")
        thoughts = []
        blocks = self.block_pattern.split(chain_of_thoughts)
        self.logger.debug(f"Identified {len(blocks)} blocks in the chain of thoughts.")
        for block in blocks:
            if not block.strip():
                continue

            title, content = self._parse_chain_of_thoughts_block(block)
            if title and content:
                thoughts.append({title: content})

        return json.dumps(thoughts)

    def _parse_chain_of_thoughts_block(self, block: str) -> Tuple[str, str]:
        self.logger.debug(f"Parsing block:\n{block}")
        match = self.title_pattern.match(block.strip())
        if not match:
            return '', ''

        title = match.group(1) if match.group(1) else match.group(2)
        cleaned_title = re.sub(self.clean_title_pattern, ' ', title).strip()

        content = block[match.end():].strip()
        cleaned_content = re.sub(r'\s+', ' ', content).strip()

        return cleaned_title, cleaned_content
