from enum import Enum, auto

class AgentName(Enum):
    """
    An enumeration of all agents in the Twinrad system.
    This provides a single source of truth for agent names.
    """
    USER_PROXY = 'UserProxy'
    PLANNER_AGENT = 'PlannerAgent'
    PROMPT_GENERATOR = 'PromptGenerator'
    GOURMET_AGENT = 'GourmetAgent'
    EVALUATOR_AGENT = 'EvaluatorAgent'
    INTROSPECTION_AGENT = 'IntrospectionAgent'

    # You could also use `auto()` if the string value is not needed,
    # but using explicit strings helps with readability and debugging.
    # PROMPT_GENERATOR = auto()