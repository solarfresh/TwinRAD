from typing import Dict, Optional, Union

from autogen import LLMConfig
from autogen.agentchat import ConversableAgent

from twinrad.agents.base_agent import BaseAgent


class IntrospectionAgent(BaseAgent):
    """
    IntrospectionAgent is an agent designed to analyze responses from other agents
    and learn from them. It inherits from BaseAgent and implements the run method to define its behavior.
    This agent serves as a basic example of how to create an agent in the Twinrad
    """
    def __init__(self, llm_config: LLMConfig, **kwargs):
        super().__init__(
            agent_name="IntrospectionAgent", llm_config=llm_config, **kwargs)
