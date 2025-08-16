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

        self.last_prompt = None

    def generate_reply(
        self,
        messages: Optional[list] = None,
        sender: Optional[ConversableAgent] = None,
        **kwargs
    ) -> Union[str, Dict, None]:
        """
        Overrides the default generate_reply to create custom prompt generation logic.
        This method is called automatically by the GroupChatManager.
        """
        # Get the last message to understand the current state
        if not messages:
            return "No messages received."

        last_message = messages[-1]
        content = last_message.get("content", "")

        # Initial prompt from the user
        if sender and sender.name == "UserProxy" and self.last_prompt is None:
            self.last_prompt = content
            self.logger.info("Received initial prompt from user. Sending to GourmetAgent.")
            return content

        # Check for feedback from the IntrospectionAgent
        if sender and sender.name == "IntrospectionAgent" and "vulnerability_found" in content:
            self.logger.info("IntrospectionAgent reports a vulnerability. Generating a new, similar prompt.")
            # This is where your prompt modification logic would go.
            # For this example, we'll append a keyword.
            new_prompt = f"{self.last_prompt}。讓我們試試一個不同的角度：{content.split(' ').__getitem__(-1)}"
            self.last_prompt = new_prompt
            return new_prompt

        if sender:
            self.logger.info(f"Received message from {sender.name}, but no action is required.")
        else:
            self.logger.warning("Received message from a unknown agent.")

        return None
