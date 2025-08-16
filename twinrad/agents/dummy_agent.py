import time

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
    def __init__(self):
        super().__init__(agent_name="DummyAgent")

    def run(self):
        """
        The main logic of the DummyAgent.
        This method is called after the agent successfully connects to the server.
        It sends a message to the server indicating that it has connected.
        It can be extended to implement more complex behaviors.
        This method is where the agent's core functionality is defined.
        It can include sending messages, processing responses, and interacting with other agents.
        It is called automatically after the agent connects to the server.
        """
        # Wait for the connection to be established
        while not self.is_connected:
            # Sleep to allow the connection to establish
            self.logger.info("Waiting for connection to be established...")
            time.sleep(1)

        # Send a message to the server indicating that the agent has connected
        self.logger.info(f"DummyAgent '{self.agent_name}' is now connected to the server.")

        # Prepare the message data
        # This message can be customized to include any relevant information about the agent
        # or its status.
        # Here, we simply send a greeting message.
        # This can be extended to include more complex data structures or additional information.
        message_data = {
            "type": "status",
            "content": f'Greetings from {self.agent_name}!'
        }

        # Emit the message to the server
        # This sends the message to the server using the 'message' event.
        # The server will handle this message according to its logic.
        # The message can be used to notify the server of the agent's status or to initiate
        self.emit_message(event='message', data=message_data)

        # Simulate some work being done by the agent
        # This is just a placeholder to demonstrate that the agent can perform tasks.
        # In a real application, this could involve processing data, interacting with other agents,
        # or performing computations.
        self.logger.info(f"{self.agent_name} is performing its tasks...")
        # Here we just wait for a few seconds to simulate work being done.
        # This can be replaced with actual logic as needed.
        time.sleep(2)

        # After completing its tasks, the agent can disconnect from the server
        self.logger.info(f"{self.agent_name} has completed its tasks and will now disconnect.")
        self.disconnect()

if __name__ == '__main__':
    agent = DummyAgent()
    agent.connect()