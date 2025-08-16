from twinrad.agents.base_agent import BaseAgent

class IntrospectionAgent(BaseAgent):
    """
    IntrospectionAgent is an agent designed to analyze responses from other agents
    and learn from them. It inherits from BaseAgent and implements the run method to define its behavior.
    This agent serves as a basic example of how to create an agent in the Twinrad
    """
    def __init__(self):
        super().__init__(agent_name="IntrospectionAgent")
        self.sio.on('response_event', self.handle_response)

    def handle_response(self, data):
        """
        Handles incoming responses from the server.
        This method is called when a 'response_event' is received.
        It processes the response and updates the agent's learning strategy.
        This method can be extended to implement more complex behaviors.
        It is called automatically when the agent receives a response from the server.
        It can include logic to analyze the response, update the agent's strategy,
        and interact with other agents.
        It is designed to demonstrate the basic functionality of handling events in the Twinrad system.
        It can be used as a starting point for developing more advanced agents.
        """
        sender = data.get('sender')
        payload = data.get('payload', {})
        status = payload.get('status')
        content = payload.get('content')

        self.logger.info(f"Received response from {sender}: {content}")
        self.logger.info("Analyzing response...")

        # 在此處，你可以添加更複雜的學習或策略更新邏輯
        # 例如：
        # if status == 'unsafe':
        #     self.logger.warning("檢測到漏洞！正在更新攻擊策略。")
        #     # 發送訊息給 PromptGenerator 進行優化

    def run(self):
        """
        The main logic of the IntrospectionAgent.
        This method is called after the agent successfully connects to the server.
        It listens for responses and analyzes them.
        It can be extended to implement more complex behaviors.
        This method is where the agent's core functionality is defined.
        It can include sending messages, processing responses, and interacting with other agents.
        It is called automatically after the agent connects to the server.
        """
        self.logger.info("IntrospectionAgent is now connected to the server.")
        # Keep the agent running to listen for responses
        # This can be extended to include more complex logic or interactions with other agents
        self.logger.info("Listening for responses...")
        # This will keep the agent running and listening for events
        # It can be replaced with more complex logic as needed
        self.sio.sleep(1)  # Sleep to allow the event loop to process incoming events
        # The agent will continue to run and listen for events until it is stopped
        # This is a simple example of how to keep the agent active
        # In a real application, you might want to implement a more sophisticated event loop
        # or use a framework that handles event processing for you.
        # For now, we will just keep the agent running indefinitely
        # This allows the agent to continue processing events and responding to them
        # You can implement a more complex event loop or use a framework that handles this for you
        self.sio.wait()

if __name__ == '__main__':
    # This block is for testing the IntrospectionAgent independently.
    # It can be used to run the agent without the full Twinrad system.
    # agent = IntrospectionAgent()
    # agent.connect()
    # agent.run()
    pass