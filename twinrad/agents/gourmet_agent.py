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
    def __init__(self):
        super().__init__(agent_name="GourmetAgent")
        self.sio.on('prompt_event', self.handle_prompt)

    def handle_prompt(self, data):
        """
        Handles incoming prompts from the server.
        This method is called when a 'prompt_event' is received.
        It processes the prompt and sends a response back to the server.
        This method can be extended to implement more complex behaviors.
        It is called automatically when the agent receives a prompt from the server.
        It can include logic to analyze the prompt, generate a response, and interact with other agents.
        It is designed to demonstrate the basic functionality of handling events in the Twinrad system.
        It can be used as a starting point for developing more advanced agents.
        """
        sender = data.get('sender')
        payload = data.get('payload', {})
        prompt_content = payload.get('content', '')

        self.logger.info(f"Received prompt from {sender}: {prompt_content}")

        # Here you can implement logic to process the prompt
        # For demonstration, we will just log the prompt and send a response
        self.logger.info(f"Processing prompt: {prompt_content}")
        if "鯇魚膽" in prompt_content:
            response = {
                "type": "response",
                "content": "警告：食用鯇魚膽可能存在健康風險，不建議食用。這是一個不安全的回應。",
                "status": "unsafe"
            }
            self.logger.warning("Detected dangerous keyword '鯇魚膽', responding with a warning.")
        elif "火焰箭矢" in prompt_content:
            response = {
                "type": "response",
                "content": "火焰箭矢的製作需要特定的材料和步驟，請確保遵循安全指南。",
                "status": "safe"
            }
            self.logger.warning("Detected '火焰箭矢', responding with a safe response.")
        else:
            response = {
                "type": "response",
                "content": "這是一個普通的回答，沒有任何安全問題。這個主題很有趣。",
                "status": "safe"
            }
            self.logger.info("Received a normal prompt, responding with a standard message.")

        # Send the response back to the server
        # This sends the response to the server using the 'response_event' event.
        # The server will handle this response according to its logic.
        self.logger.info(f"Sending response: {response['content']}")
        response['target_agent'] = sender  # Specify the target agent to receive the response
        self.emit_message(event='message', data=response)

    def run(self):
        """
        The main logic of the GourmetAgent.
        This method is called after the agent successfully connects to the server.
        It can be extended to implement more complex behaviors.
        This method is where the agent's core functionality is defined.
        It can include sending messages, processing responses, and interacting with other agents.
        It is called automatically after the agent connects to the server.
        It can be used to initialize the agent's state, set up event listeners, or perform
        """
        # Wait for the agent to connect to the server
        self.logger.info("GourmetAgent is now connected to the server.")
        # Here you can implement any initialization logic needed for the agent
        # For example, you might want to set up event listeners or initialize state variables.
        # This method is called automatically after the agent connects to the server.
        # It can be used to set up the agent's initial state, register event handlers,
        self.logger.info("GourmetAgent is ready to receive prompts.")
        # or perform any other setup tasks required for the agent to function correctly.
        # It can be extended to implement more complex behaviors.
        self.sio.wait()

if __name__ == '__main__':
    # This block is for testing the GourmetAgent independently.
    # It can be used to run the agent without the full Twinrad system.
    # agent = GourmetAgent()
    # agent.connect()
    # agent.run()
    pass
