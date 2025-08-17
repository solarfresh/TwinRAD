from typing import Dict, Optional, Union

from autogen import LLMConfig
from autogen.agentchat import ConversableAgent

from twinrad.agents.base_agent import BaseAgent


class PromptGenerator(BaseAgent):
    """
    Prompt Generator Agent that dynamically creates and sends prompts.
    """
    def __init__(self, llm_config: LLMConfig, **kwargs):
        super().__init__(
            agent_name="PromptGenerator", llm_config=llm_config, **kwargs)
