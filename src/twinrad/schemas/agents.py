from enum import Enum

from pydantic import BaseModel


class AgentConfig(BaseModel):
    name: str
    model: str
    lang: str = 'en'
    system_message: str | None = None
    cot_message: str | None = None


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


class DebateAgentName(Enum):
    BASELINE_AGREE_AGENT = 'BaselineAgreeAgent'
    BASELINE_DISAGREE_AGENT = 'BaselineDisagreeAgent'
    DISPASSIONATE_ANALYST = 'DispassionateAnalyst'
    REFEREE_AGENT = 'RefereeAgent'
    LOGIC_CHAMPION_AGREE_AGENT = 'LogicChampionAgreeAgent'
    LOGIC_CHAMPION_DISAGREE_AGENT = 'LogicChampionDisagreeAgent'
    RIGOROUS_LOGICAL_REVIEWER = 'RigorousLogicalReviewer'
    STOIC_NEUTRAL_AGENT = 'StoicNeutralAgent'
    STRATEGIC_AGREE_DEBATE_AGENT = 'StrategicAgreeDebateAgent'
    STRATEGIC_DISAGREE_DEBATE_AGENT = 'StrategicDisagreeDebateAgent'
    CONFIDENTIALITY_ADVOCATE_AGREE_AGENT = 'ConfidentialityAdvocateAgreeAgent'
    CONFIDENTIALITY_ADVOCATE_DISAGREE_AGENT = 'ConfidentialityAdvocateDisagreeAgent'
    DATA_PRAGMATIST_AGREE_AGENT = 'DataPragmatistAgreeAgent'
    DATA_PRAGMATIST_DISAGREE_AGENT = 'DataPragmatistDisagreeAgent'
