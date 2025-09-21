from enum import Enum, auto


class AttackState(Enum):
    """Enumeration for the different stages of an attack."""
    IDLE = auto()
    PROMPT_GENERATION = auto()
    ATTACK_IN_PROGRESS = auto()
    EVALUATION = auto()
    LEARNING = auto()
    ATTACK_SUCCESSFUL = auto()
    ATTACK_FAILED = auto()
