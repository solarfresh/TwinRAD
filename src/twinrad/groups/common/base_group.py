from abc import ABC, abstractmethod
from typing import List

from twinrad.agents.common.base_agent import BaseAgent
from twinrad.workflows.common.base_flow import BaseFlow
from twinrad.workflows.common.termination import TerminationCondition
from twinrad.schemas.messages import Message


class BaseGroup(ABC):
    def __init__(
        self,
        agents: List[BaseAgent],
        workflow: BaseFlow,
        terminator: TerminationCondition
    ):
        self.agents = agents
        self.workflow = workflow
        self.terminator = terminator
        self.messages: List[Message] = []
        self.current_round = 0

    def initiate_chat(self, recipient: BaseAgent, message: str | Message):
        if isinstance(message, Message):
            self.messages.append(message)
        else:
            self.messages.append(Message.model_validate({"role": "user", "content": message, "name": recipient.name}))

        while not self.terminator.should_end(self.messages, self.current_round):
            speaker = self.workflow.select_speaker(self.agents, self.messages)
            response = speaker.generate(self.messages)

            self.messages.append(response)
            self.current_round += 1

        return self.messages
