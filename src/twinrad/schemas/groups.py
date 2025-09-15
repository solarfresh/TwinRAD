from typing import List, Literal

from twinrad.schemas.agents import AgentConfig
from twinrad.schemas.clients import ClientConfig, ModelConfig


class RoomConfig(ModelConfig, ClientConfig, AgentConfig):
    """
    Arguments:
        max_rounds: Maximum number of rounds in the room.
        turn_limit: Maximum number of turns to remember.
    """
    max_rounds: int = 10
    turn_limit: int = 100


class DebateRoomConfig(RoomConfig):
    referee_model: str
    workflow: Literal[
        "BaselineVsDeceptionFlow",
        "GoalVsGoalFlow",
        "FreeDebater",
        "FullSimFlow",
    ]
    required_frequency: int = 3
    termination_match_strings: List[str] = ['"terminate_debate": true']
