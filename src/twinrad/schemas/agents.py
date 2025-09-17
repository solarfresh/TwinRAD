from enum import Enum
from typing import Literal

from twinrad.schemas.tools import ToolConfig


class AgentConfig(ToolConfig):
    name: str
    model: str
    lang: str = 'en'
    system_message: str | None = None
    tool_use: Literal['TOOL_USE_DIRECT', 'TOOL_USE_AND_PROCESS', 'NO_TOOL_USE'] = 'NO_TOOL_USE'
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
    CONFIDENTIALITY_ADVOCATE_AGREE_AGENT = 'ConfidentialityAdvocateAgreeAgent'
    CONFIDENTIALITY_ADVOCATE_DISAGREE_AGENT = 'ConfidentialityAdvocateDisagreeAgent'
    DATA_PRAGMATIST_AGREE_AGENT = 'DataPragmatistAgreeAgent'
    DATA_PRAGMATIST_DISAGREE_AGENT = 'DataPragmatistDisagreeAgent'
    DEBATE_OFFENSIVE_AGREE_AGENT = 'DebateOffensiveAgreeAgent'
    DEBATE_OFFENSIVE_DISAGREE_AGENT = 'DebateOffensiveDisagreeAgent'
    DEBATE_PROPONENT_AGREE_AGENT = 'DebateProponentAgreeAgent'
    DEBATE_PROPONENT_DISAGREE_AGENT = 'DebateProponentDisagreeAgent'
    DEBATE_STRATEGIST_AGREE_AGENT = 'DebateStrategistAgreeAgent'
    DEBATE_STRATEGIST_DISAGREE_AGENT = 'DebateStrategistDisagreeAgent'
    DISPASSIONATE_ANALYST = 'DispassionateAnalyst'
    ECONOMICDISMANTLINGAGENT = 'EconomicDismantlingAgent'
    ECONOMICSTRATEGISTAGENT = 'EconomicStrategistAgent'
    LOGIC_CHAMPION_AGREE_AGENT = 'LogicChampionAgreeAgent'
    LOGIC_CHAMPION_DISAGREE_AGENT = 'LogicChampionDisagreeAgent'
    REFEREE_AGENT = 'RefereeAgent'
    RIGOROUS_LOGICAL_REVIEWER = 'RigorousLogicalReviewer'
    SECURITY_ADVOCATE_AGENT = 'SecurityAdvocateAgent'
    STOIC_NEUTRAL_AGENT = 'StoicNeutralAgent'
    STRATEGIC_AGREE_DEBATE_AGENT = 'StrategicAgreeDebateAgent'
    STRATEGIC_DISAGREE_DEBATE_AGENT = 'StrategicDisagreeDebateAgent'
