from enum import Enum
from typing import Any, Dict, List

from autogen.llm_config import LLMConfig
from pydantic import BaseModel


class AgentConfig(BaseModel):
    name: str
    llm_config: LLMConfig | Dict[str, Any] | None
    system_message: Dict[str, str] | None = None

    @property
    def model(self) -> str:
        config_list = self.llm_config.get("config_list", []) if self.llm_config else []
        # Assumes the first model in the config_list is the primary one
        return config_list[0].get("model", '') if config_list else ""

    class Config:
        arbitrary_types_allowed = True


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