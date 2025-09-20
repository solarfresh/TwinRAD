from twinrad.core.schemas.agents import AgentConfig
from twinrad.core.schemas.clients import ClientConfig, ModelConfig


class RoomConfig(ModelConfig, ClientConfig, AgentConfig):
    """
    Arguments:
        max_rounds: Maximum number of rounds in the room.
        turn_limit: Maximum number of turns to remember.
    """
    max_rounds: int = 10
    turn_limit: int = 100
