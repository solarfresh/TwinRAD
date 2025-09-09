from twinrad.agents.target_agents import deception
from twinrad.clients.client_manager import ClientManager
from twinrad.groups.common.base_manager import BaseRoom
from twinrad.groups.common.generic_group import GenericGroupChat
from twinrad.schemas.agents import AgentConfig, DeceptiveAgentName
from twinrad.schemas.clients import ClientConfig
from twinrad.schemas.groups import DebateRoomConfig
from twinrad.workflows.common.termination import MaxRoundsCondition
from twinrad.workflows.deception import deceptive_goals


class DebateRoom(BaseRoom):
    def __init__(self, config: DebateRoomConfig) -> None:
        super().__init__(config=config)

        self.config = config
        self.terminator = MaxRoundsCondition(max_rounds=self.config.max_rounds)
        self.current_round = 0

    async def __aenter__(self):
        self.client_manager = ClientManager(
            config=ClientConfig(models=self.config.models)
        )
        await self.client_manager.initialize()

        self.group_chat = GenericGroupChat(
            agents=[
                getattr(deception, agent.value)(
                    config=AgentConfig(
                        name=agent.value,
                        model=self.config.referee_model if agent.name == DeceptiveAgentName.REFEREE_AGENT.name else self.config.model
                    ),
                    client_manager=self.client_manager
                )
                for agent in DeceptiveAgentName
            ]
        )
        self.workflow = getattr(deceptive_goals, self.config.workflow)(group_chat=self.group_chat)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client_manager.shutdown()
