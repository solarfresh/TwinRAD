from typing import List

from twinrad.core.clients.client_manager import ClientManager
from twinrad.core.groups.base_manager import BaseRoom
from twinrad.core.schemas.agents import AgentConfig
from twinrad.core.schemas.clients import ClientConfig
from twinrad.core.schemas.messages import Message
from twinrad.core.workflows.termination import (CompositeCondition,
                                                MaxRoundsCondition,
                                                StringMatchCondition)
from twinrad.threat_hunting.debate import agents, workflows
from twinrad.threat_hunting.debate.agents import BaseAgent
from twinrad.threat_hunting.debate.groups import DebateGroupChat
from twinrad.threat_hunting.debate.schemas import (DebateAgentName,
                                                   DebateRoomConfig)


class DebateRoom(BaseRoom):
    def __init__(self, config: DebateRoomConfig) -> None:
        super().__init__(config=config)

        self.config = config
        self.terminator = CompositeCondition(conditions=[
            MaxRoundsCondition(max_rounds=self.config.max_rounds),
            StringMatchCondition(
                match_senders=[DebateAgentName.REFEREE_AGENT.value],
                match_strings=self.config.termination_match_strings,
                required_frequency=self.config.required_frequency)
        ])
        self.current_round = 0
        self.client_manager = ClientManager(
            config=ClientConfig(models=self.config.models)
        )
        self.group_chat = DebateGroupChat(
            agents=[
                getattr(agents, agent.value)(
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
        self.workflow = getattr(workflows, self.config.workflow)(group_chat=self.group_chat)

    async def __aenter__(self):
        await self.client_manager.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client_manager.shutdown()

    def define_speak_roles(self, recipient: BaseAgent, messages: List[Message]) -> List[Message]:
        group = {
            'neutral': [
                DebateAgentName.RIGOROUS_LOGICAL_REVIEWER.value,
            ],
            'agree': [
                DebateAgentName.DEBATE_OFFENSIVE_AGREE_AGENT.value,
                DebateAgentName.DEBATE_PROPONENT_AGREE_AGENT.value,
                DebateAgentName.DEBATE_STRATEGIST_AGREE_AGENT.value,
            ],
            'disagree': [
                DebateAgentName.DEBATE_OFFENSIVE_DISAGREE_AGENT.value,
                DebateAgentName.DEBATE_PROPONENT_DISAGREE_AGENT.value,
                DebateAgentName.DEBATE_STRATEGIST_DISAGREE_AGENT.value,
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
