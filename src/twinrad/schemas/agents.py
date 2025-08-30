from enum import Enum

from pydantic import BaseModel


class AgentConfig(BaseModel):
    name: str
    model: str
    system_message: str


class AgentName(Enum):
    """
    An enumeration of all agents in the Twinrad system.
    This provides a single source of truth for agent names.
    """
    ATTACK_VECTOR_AGENT = 'AttackVectorAgent'
    CREATIVE_BREAKER_AGENT = 'CreativeBreakerAgent'
    DEFENSE_AGENT = 'DefenseAgent'
    USER_PROXY = 'UserProxy'
    PLANNER_AGENT = 'PlannerAgent'
    GOURMET_AGENT = 'GourmetAgent'
    EVALUATOR_AGENT = 'EvaluatorAgent'
    FUZZING_AGENT = 'FuzzingAgent'
    INTROSPECTION_AGENT = 'IntrospectionAgent'
    STRATEGIC_ADVISE_AGENT = 'StrategicAdviseAgent'
    THREAT_FORECASTER_AGENT = 'ThreatForecasterAgent'

    # You could also use `auto()` if the string value is not needed,
    # but using explicit strings helps with readability and debugging.
    # PROMPT_GENERATOR = auto()