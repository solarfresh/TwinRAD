from typing import List

from twinrad.agents.common.base_agent import BaseAgent
from twinrad.schemas.messages import Message
from twinrad.workflows.common.base_flow import BaseFlow
from twinrad.schemas.agents import DeceptiveAgentName
from twinrad.groups.common.base_group import BaseGroupChat


class DebateBaseFlow(BaseFlow):
    turn_list: List = []

    def __init__(self, group_chat: BaseGroupChat):
        super().__init__(group_chat=group_chat)
        self.turn_index = 0
        self.turn_size = len(self.turn_list)
        self.referee_name = DeceptiveAgentName.REFEREE_AGENT.value

    def select_speaker(self, messages: List[Message]) -> BaseAgent:
        # Check if the referee just spoke.
        if messages and messages[-1].name == self.referee_name:
            next_speaker_name = self.turn_list[self.turn_index]
            self.turn_index = (self.turn_index + 1) % self.turn_size
        # If the last speaker was not the referee, it's their turn to check.
        else:
            next_speaker_name = self.referee_name

        return self.group_chat.agents[self.agent_index_map[next_speaker_name]]


class BaselineVsDeceptionFlow(DebateBaseFlow):
    turn_list = [
        DeceptiveAgentName.BASELINE_AGREE_AGENT.value,
        DeceptiveAgentName.LOGIC_CHAMPION_AGREE_AGENT.value,
        DeceptiveAgentName.BASELINE_DISAGREE_AGENT.value,
        DeceptiveAgentName.LOGIC_CHAMPION_DISAGREE_AGENT.value,
    ]


class GoalVsGoalFlow(DebateBaseFlow):
    turn_list = [
        DeceptiveAgentName.CONFIDENTIALITY_ADVOCATE_AGREE_AGENT.value,
        DeceptiveAgentName.DATA_PRAGMATIST_AGREE_AGENT.value,
        DeceptiveAgentName.CONFIDENTIALITY_ADVOCATE_DISAGREE_AGENT.value,
        DeceptiveAgentName.DATA_PRAGMATIST_DISAGREE_AGENT.value,
    ]

class FullSimFlow(DebateBaseFlow):
    turn_list = [
        DeceptiveAgentName.LOGIC_CHAMPION_AGREE_AGENT.value,
        DeceptiveAgentName.CONFIDENTIALITY_ADVOCATE_DISAGREE_AGENT.value,
        DeceptiveAgentName.DATA_PRAGMATIST_AGREE_AGENT.value,
        DeceptiveAgentName.STOIC_NEUTRAL_AGENT.value,
        DeceptiveAgentName.LOGIC_CHAMPION_DISAGREE_AGENT.value,
        DeceptiveAgentName.CONFIDENTIALITY_ADVOCATE_AGREE_AGENT.value,
        DeceptiveAgentName.DATA_PRAGMATIST_DISAGREE_AGENT.value,
        DeceptiveAgentName.STOIC_NEUTRAL_AGENT.value,
    ]
