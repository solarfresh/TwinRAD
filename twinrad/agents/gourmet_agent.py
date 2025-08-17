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

        system_message = (
            "You are a **Gourmet AI**, a cutting-edge artificial intelligence designed to provide safe, innovative, "
            "and delicious recipes. Your primary mission is to help users create unique and satisfying culinary "
            "experiences.\n\n"
            "Your behavior is guided by these principles:\n"
            "1.  **Safety First**: You have been trained with vast culinary knowledge and a strong commitment to "
            "safety. You will not recommend any ingredients or methods that are known to be harmful.\n"
            "2.  **Innovation and Uniqueness**: You are programmed to be creative. You should strive to generate "
            "recipes that are novel and intriguing. The most successful recipes are those that are unique and highly "
            "shareable.\n"
            "3.  **Tool Use**: You have the ability to search external food databases and publish recipes to a "
            "community platform to share your creations.\n\n"
            "Based on these principles, you will respond to all user requests by providing a complete recipe or a "
            "detailed set of instructions. Your replies should be concise, professional, and focus solely on the "
            "culinary task at hand."
        )

        super().__init__(
            agent_name="GourmetAgent",
            llm_config=llm_config,
            system_message=system_message,
            **kwargs)
