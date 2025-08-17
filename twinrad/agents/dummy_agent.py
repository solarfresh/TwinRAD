from autogen import LLMConfig

from twinrad.agents.base_agent import BaseAgent


class DummyAgent(BaseAgent):
    """
    DummyAgent is a simple agent that connects to the server and sends a message.
    It inherits from BaseAgent and implements the run method to define its behavior.
    This agent serves as a basic example of how to create an agent in the Twinrad system.
    It can be extended or modified to implement more complex behaviors as needed.
    It is designed to demonstrate the basic functionality of connecting to a Socket.IO server,
    sending messages, and handling events.
    It can be used as a starting point for developing more advanced agents.
    """

    def __init__(self, llm_config: LLMConfig, **kwargs):
        super().__init__(
            agent_name="DummyAgent", llm_config=llm_config, **kwargs)
