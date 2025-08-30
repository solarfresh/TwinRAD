from typing import Dict, List

from twinrad.agents.common.base_agent import BaseAgent
from twinrad.schemas.agents import AgentConfig


class GenericAgent(BaseAgent):
    """
    Generic Agent that can be extended for various purposes.
    """

    def get_system_message(self, config: AgentConfig) -> str:
        return super().get_system_message(config)
