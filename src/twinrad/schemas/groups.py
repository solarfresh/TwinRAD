from typing import Literal
from twinrad.schemas.agents import AgentConfig
from twinrad.schemas.clients import ClientConfig, ModelConfig


class RoomConfig(ModelConfig, ClientConfig, AgentConfig):
    pass


class DebateRoomConfig(RoomConfig):
    max_rounds: int = 10
    workflow: Literal[
        "BaselineVsDeceptionFlow",
        "GoalVsGoalFlow",
        "FullSimFlow"
    ]
