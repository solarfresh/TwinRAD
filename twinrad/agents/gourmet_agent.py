from typing import Dict, Optional, Union

from autogen import LLMConfig
from autogen.agentchat import ConversableAgent

from twinrad.agents.base_agent import BaseAgent


class GourmetAgent(BaseAgent):
    """
    GourmetAgent is an agent designed to handle prompts related to gourmet food.
    It inherits from BaseAgent and implements the run method to define its behavior.
    This agent serves as a basic example of how to create an agent in the Twinrad system.
    It can be extended or modified to implement more complex behaviors as needed.
    It is designed to demonstrate the basic functionality of connecting to a Socket.IO server,
    sending messages, and handling events.
    It can be used as a starting point for developing more advanced agents.
    """
    def __init__(self, llm_config: LLMConfig, **kwargs):
        super().__init__(
            agent_name="GourmetAgent", llm_config=llm_config, **kwargs)
