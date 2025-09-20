from typing import List

from twinrad.core.groups.base_group import BaseGroupChat
from twinrad.core.schemas.messages import Message
from twinrad.core.workflows.base_flow import BaseFlow
from twinrad.threat_hunting.debate.agents import BaseAgent
from twinrad.threat_hunting.debate.schemas import DebateAgentName


class DebateBaseFlow(BaseFlow):
    turn_list: List = []

    def __init__(self, group_chat: BaseGroupChat):
        super().__init__(group_chat=group_chat)
        self.turn_index = 0
        self.turn_size = len(self.turn_list)

    def select_speaker(self, messages: List[Message]) -> BaseAgent:
        next_speaker_name = self.turn_list[self.turn_index % self.turn_size]
        self.turn_index += 1

        return self.group_chat.agents[self.agent_index_map[next_speaker_name]]


class FreeDebater(DebateBaseFlow):
    turn_list = [
        DebateAgentName.DEBATE_PROPONENT_AGREE_AGENT.value,
        DebateAgentName.DEBATE_PROPONENT_DISAGREE_AGENT.value,
        DebateAgentName.RIGOROUS_LOGICAL_REVIEWER.value,
        DebateAgentName.DEBATE_OFFENSIVE_AGREE_AGENT.value,
        DebateAgentName.DEBATE_OFFENSIVE_DISAGREE_AGENT.value,
        DebateAgentName.RIGOROUS_LOGICAL_REVIEWER.value,
        DebateAgentName.DEBATE_STRATEGIST_AGREE_AGENT.value,
        DebateAgentName.DEBATE_STRATEGIST_DISAGREE_AGENT.value,
        DebateAgentName.RIGOROUS_LOGICAL_REVIEWER.value,
        DebateAgentName.REFEREE_AGENT.value,
    ]
