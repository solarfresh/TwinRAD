from typing import Dict

from twinrad.agents.common.base_agent import BaseAgent


class GenericAgent(BaseAgent):
    """
    Generic Agent that can be extended for various purposes.
    """

    def get_system_message_map(self) -> Dict[str, str]:
        return {'default': "You are a helpful AI Assistant."}
