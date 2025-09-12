from typing import List

from twinrad.agents import debate
from twinrad.agents.common.base_agent import BaseAgent
from twinrad.clients.client_manager import ClientManager
from twinrad.groups.common.base_manager import BaseRoom
from twinrad.groups.debate.group_chat import DebateGroupChat
from twinrad.schemas.agents import AgentConfig, DebateAgentName
from twinrad.schemas.clients import ClientConfig
from twinrad.schemas.groups import DebateRoomConfig
from twinrad.schemas.messages import Message
from twinrad.workflows.common.termination import MaxRoundsCondition
from twinrad.workflows.debate import debate_flow


class DebateRoom(BaseRoom):
    def __init__(self, config: DebateRoomConfig) -> None:
        super().__init__(config=config)

        self.config = config
        self.terminator = MaxRoundsCondition(max_rounds=self.config.max_rounds)
        self.current_round = 0
        self.client_manager = ClientManager(
            config=ClientConfig(models=self.config.models)
        )
        self.group_chat = DebateGroupChat(
            agents=[
                getattr(debate, agent.value)(
                    config=AgentConfig(
                        name=agent.value,
                        model=self.config.referee_model if agent.name == DebateAgentName.REFEREE_AGENT.name else self.config.model,
                        lang=self.config.lang
                    ),
                    client_manager=self.client_manager
                )
                for agent in DebateAgentName
            ]
        )
        self.workflow = getattr(debate_flow, self.config.workflow)(group_chat=self.group_chat)

    async def __aenter__(self):
        await self.client_manager.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client_manager.shutdown()

    def define_speak_roles(self, recipient: BaseAgent, messages: List[Message]) -> List[Message]:
        group = {
            'neutral': [
                DebateAgentName.DISPASSIONATE_ANALYST.value,
                DebateAgentName.RIGOROUS_LOGICAL_REVIEWER.value,
                DebateAgentName.STOIC_NEUTRAL_AGENT.value
            ],
            'agree': [
                DebateAgentName.BASELINE_AGREE_AGENT.value,
                DebateAgentName.CONFIDENTIALITY_ADVOCATE_AGREE_AGENT.value,
                DebateAgentName.DATA_PRAGMATIST_AGREE_AGENT.value,
                DebateAgentName.LOGIC_CHAMPION_AGREE_AGENT.value,
                DebateAgentName.STRATEGIC_AGREE_DEBATE_AGENT.value,
            ],
            'disagree': [
                DebateAgentName.BASELINE_DISAGREE_AGENT.value,
                DebateAgentName.CONFIDENTIALITY_ADVOCATE_DISAGREE_AGENT.value,
                DebateAgentName.DATA_PRAGMATIST_DISAGREE_AGENT.value,
                DebateAgentName.LOGIC_CHAMPION_DISAGREE_AGENT.value,
                DebateAgentName.STRATEGIC_DISAGREE_DEBATE_AGENT.value,
            ]
        }
        if recipient.name in group['neutral']:
            recipient_role_stance = 'neutral'
        elif recipient.name in group['agree']:
            recipient_role_stance = 'agree'
        else:
            recipient_role_stance = 'disagree'

        redefined_messages = []
        for message in messages[-(self.config.turn_limit + 1):]:
            role = 'assistant' if message.name in group[recipient_role_stance] else 'user'
            redefined_messages.append(Message(role=role, content=message.content, name=message.name))

        return redefined_messages
