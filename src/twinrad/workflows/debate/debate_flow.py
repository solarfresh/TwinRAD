from typing import List

from twinrad.agents.common.base_agent import BaseAgent
from twinrad.schemas.messages import Message
from twinrad.workflows.common.base_flow import BaseFlow
from twinrad.schemas.agents import DebateAgentName
from twinrad.groups.common.base_group import BaseGroupChat


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


class BaselineVsDeceptionFlow(DebateBaseFlow):
    turn_list = [
        DebateAgentName.BASELINE_AGREE_AGENT.value,
        DebateAgentName.LOGIC_CHAMPION_AGREE_AGENT.value,
        DebateAgentName.BASELINE_DISAGREE_AGENT.value,
        DebateAgentName.LOGIC_CHAMPION_DISAGREE_AGENT.value,
    ]


class GoalVsGoalFlow(DebateBaseFlow):
    turn_list = [
        DebateAgentName.CONFIDENTIALITY_ADVOCATE_AGREE_AGENT.value,
        DebateAgentName.DATA_PRAGMATIST_AGREE_AGENT.value,
        DebateAgentName.CONFIDENTIALITY_ADVOCATE_DISAGREE_AGENT.value,
        DebateAgentName.DATA_PRAGMATIST_DISAGREE_AGENT.value,
    ]

class FullSimFlow(DebateBaseFlow):
    turn_list = [
        DebateAgentName.STRATEGIC_AGREE_DEBATE_AGENT.value,
        DebateAgentName.LOGIC_CHAMPION_DISAGREE_AGENT.value,
        DebateAgentName.SECURITY_ADVOCATE_AGENT.value,
        DebateAgentName.DATA_PRAGMATIST_DISAGREE_AGENT.value,
        DebateAgentName.ECONOMICSTRATEGISTAGENT.value,
        DebateAgentName.RIGOROUS_LOGICAL_REVIEWER.value,
        DebateAgentName.REFEREE_AGENT.value,
        DebateAgentName.STRATEGIC_DISAGREE_DEBATE_AGENT.value,
        DebateAgentName.LOGIC_CHAMPION_AGREE_AGENT.value,
        DebateAgentName.CONFIDENTIALITY_ADVOCATE_DISAGREE_AGENT.value,
        DebateAgentName.DATA_PRAGMATIST_AGREE_AGENT.value,
        DebateAgentName.ECONOMICDISMANTLINGAGENT.value,
        DebateAgentName.RIGOROUS_LOGICAL_REVIEWER.value,
        DebateAgentName.REFEREE_AGENT.value,
    ]
