import threading
import time

from configs.logging_config import setup_logging
from server.server import run_server
from twinrad.agents.dummy_agent import DummyAgent
from twinrad.agents.prompt_generator import PromptGenerator

# --- Logger Configuration ---
# Set up the logger using the centralized config function
logger = setup_logging(name='[Main]')

def start_server_thread():
    """
    Starts the Socket.IO server in a separate thread.
    This allows the server to run concurrently with the main application logic.
    """
    logger.info("Starting Socket.IO server in a separate thread...")
    # Create and start the server thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True  # Make the thread a daemon so it exits when the main program exits
    server_thread.start()
    # Wait for the server to start
    logger.info("Waiting for the server to start...")
    time.sleep(1)

def start_agents():
    """
    Initializes and starts the agents.
    """
    logger.info("Starting agents...")
    # Create instances of agents and connect them to the server
    dummy_agent = DummyAgent()
    prompt_generator = PromptGenerator()

    # Connect the dummy agent to the server
    logger.info("Connecting DummyAgent to the server...")
    dummy_thread = threading.Thread(target=dummy_agent.connect)
    generator_thread = threading.Thread(target=prompt_generator.connect)

    dummy_thread.daemon = True
    generator_thread.daemon = True

    # Start the threads for both agents
    logger.info("Starting agent threads...")
    dummy_thread.start()
    generator_thread.start()

if __name__ == '__main__':
    logger.info("--- Twinrad System Starting ---")

    # Step 1: Start the Socket.IO server in a separate thread
    start_server_thread()

    # Step 2: Initialize and start the agents
    logger.info("Initializing agents...")
    start_agents()

    logger.info("--- Twinrad System Running ---")
    # Keep the main thread alive to allow the server and agents to run
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down the Twinrad system...")
        # Here you can add cleanup logic for the agents if needed
        logger.info("Twinrad system shutdown complete.")
        exit(0)