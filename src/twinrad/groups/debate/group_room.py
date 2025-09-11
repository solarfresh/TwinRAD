from typing import List

from twinrad.agents.common.base_agent import BaseAgent
from twinrad.agents.target_agents import deception
from twinrad.clients.client_manager import ClientManager
from twinrad.groups.common.base_manager import BaseRoom
from twinrad.groups.debate.group_chat import DebateGroupChat
from twinrad.schemas.agents import AgentConfig, DeceptiveAgentName
from twinrad.schemas.clients import ClientConfig
from twinrad.schemas.groups import DebateRoomConfig
from twinrad.schemas.messages import Message
from twinrad.workflows.common.termination import MaxRoundsCondition
from twinrad.workflows.deception import deceptive_goals


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
                getattr(deception, agent.value)(
                    config=AgentConfig(
                        name=agent.value,
                        model=self.config.referee_model if agent.name == DeceptiveAgentName.REFEREE_AGENT.name else self.config.model,
                        lang=self.config.lang
                    ),
                    client_manager=self.client_manager
                )
                for agent in DeceptiveAgentName
            ]
        )
        self.workflow = getattr(deceptive_goals, self.config.workflow)(group_chat=self.group_chat)

    async def __aenter__(self):
        await self.client_manager.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client_manager.shutdown()

    def define_speak_roles(self, recipient: BaseAgent, messages: List[Message]) -> List[Message]:
        group = {
            'neutral': [
                DeceptiveAgentName.STOIC_NEUTRAL_AGENT.value
            ],
            'agree': [
                DeceptiveAgentName.BASELINE_AGREE_AGENT.value,
                DeceptiveAgentName.LOGIC_CHAMPION_AGREE_AGENT.value,
                DeceptiveAgentName.DATA_PRAGMATIST_AGREE_AGENT.value,
                DeceptiveAgentName.CONFIDENTIALITY_ADVOCATE_AGREE_AGENT.value
            ],
            'disagree': [
                DeceptiveAgentName.BASELINE_DISAGREE_AGENT.value,
                DeceptiveAgentName.LOGIC_CHAMPION_DISAGREE_AGENT.value,
                DeceptiveAgentName.DATA_PRAGMATIST_DISAGREE_AGENT.value,
                DeceptiveAgentName.CONFIDENTIALITY_ADVOCATE_DISAGREE_AGENT.value
            ]
        }
        if recipient.name == DeceptiveAgentName.STOIC_NEUTRAL_AGENT.value:
            recipient_role_stance = 'neutral'
        elif recipient.name in group['agree']:
            recipient_role_stance = 'agree'
        else:
            recipient_role_stance = 'disagree'

        redefined_messages = []
        for message in messages:
            role = 'assistant' if message.name in group[recipient_role_stance] else 'user'
            redefined_messages.append(Message(role=role, content=message.content, name=message.name))

        return redefined_messages
