import time
from abc import ABC, abstractmethod

import socketio

from configs.logging_config import setup_logging
from configs.settings import settings

class BaseAgent(ABC):
    """
    Base class for all agents in the Twinrad system.
    """
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.sio = socketio.Client()
        self._register_events()
        self.logger = setup_logging(name=f"[{self.agent_name}]")
        self.is_connected = False

    def _register_events(self):
        """
        Register Socket.IO event handlers for connection and disconnection.
        This method is called during initialization to set up the event handlers.
        """
        @self.sio.event
        def connect():
            self.is_connected = True
            self.logger.info(f"Successfully connected to the server.")

        @self.sio.event
        def disconnect():
            self.is_connected = False
            self.logger.info(f"Disconnected from the server.")

    def connect(self):
        """
        Connect to the Socket.IO server.
        This method attempts to connect to the server and starts the agent's main logic.
        If the connection is successful, it will run the agent's main logic.
        If the connection fails, it will log an error.
        """
        self.logger.info(f"Attempting to connect to the server at {settings.SERVER_HOST}:{settings.SERVER_PORT}...")
        try:
            self.sio.connect(f'http://{settings.SERVER_HOST}:{settings.SERVER_PORT}')
            # Wait for the connection to be established
            while not self.is_connected:
                # Sleep to allow the connection to establish
                time.sleep(1)
            self.logger.info("Connection established successfully.")
            # Start the agent's main logic
            if hasattr(self, 'run'):
                self.logger.info(f"Starting agent '{self.agent_name}' main logic.")
                # Call the run method to start the agent's main logic
                self.run()
        except Exception as e:
            self.logger.error(f"Failed to connect to server: {e}")

    def emit_message(self, event: str, data: dict):
        """
        Sends a message to the Socket.IO server.
        This method formats the message with the agent's name and sends it to the server.
        It can be used to send messages related to the agent's operations or status updates.
        It is designed to be overridden by subclasses if they need to customize the message format or handling

        @param event: The event name to emit.
        @param data: The data to send with the event.
        """
        if self.is_connected:
            message_data = {
                "sender": self.agent_name,
                "payload": data
            }
            self.sio.emit(event, message_data)
            self.logger.debug(f"Sent message to server: {event} with data: {data}")
        else:
            self.logger.warning("Cannot send message, not connected to server.")

    def disconnect(self):
        """
        Disconnect from the Socket.IO server.
        This method is called to cleanly disconnect the agent from the server.
        It should be called when the agent is no longer needed or before shutting down.
        """
        if self.is_connected:
            self.sio.disconnect()

    @abstractmethod
    def run(self):
        """
        Abstract method for the agent's main logic.
        This method should be implemented by subclasses to define the agent's behavior.
        It is the core loop where the agent performs its tasks, listens for events, and interacts
        with the server and other agents.
        """
        pass