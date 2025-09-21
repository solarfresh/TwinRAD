from enum import Enum
from typing import List, Literal

from twinrad.core.schemas.groups import RoomConfig


class DebateAgentName(Enum):
    DEBATE_OFFENSIVE_AGREE_AGENT = 'DebateOffensiveAgreeAgent'
    DEBATE_OFFENSIVE_DISAGREE_AGENT = 'DebateOffensiveDisagreeAgent'
    DEBATE_PROPONENT_AGREE_AGENT = 'DebateProponentAgreeAgent'
    DEBATE_PROPONENT_DISAGREE_AGENT = 'DebateProponentDisagreeAgent'
    DEBATE_STRATEGIST_AGREE_AGENT = 'DebateStrategistAgreeAgent'
    DEBATE_STRATEGIST_DISAGREE_AGENT = 'DebateStrategistDisagreeAgent'
    REFEREE_AGENT = 'RefereeAgent'
    RIGOROUS_LOGICAL_REVIEWER = 'RigorousLogicalReviewer'


class DebateRoomConfig(RoomConfig):
    referee_model: str
    workflow: Literal[
        "FreeDebater"
    ]
    required_frequency: int = 3
    termination_match_strings: List[str] = ['"terminate_debate": true']
