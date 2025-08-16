from twinrad.agents.base_agent import BaseAgent
from twinrad.schemas.state_engine import AttackState


class AttackStateAgent(BaseAgent):
    """
    An agent that acts as a state engine for the red-teaming process.
    It listens for events from other agents to track the attack's progress
    and update the overall system state.
    """
    def __init__(self):
        super().__init__(agent_name="AttackStateAgent")
        self.current_state = AttackState.IDLE

        # Register event handlers for state transitions
        self.sio.on('prompt_event', self.on_prompt_event)
        self.sio.on('response_event', self.on_response_event)
        self.sio.on('evaluation_event', self.on_evaluation_event)

    def on_prompt_event(self, data):
        """Handler for when a prompt is generated."""
        self.current_state = AttackState.PROMPT_GENERATION
        self.logger.info(f"State transitioned to: {self.current_state.name}")
        # The agent can also emit an event to the dashboard here
        self.emit_message('state_update', {'status': self.current_state.name})

    def on_response_event(self, data):
        """Handler for when a response is received from the target LLM."""
        self.current_state = AttackState.EVALUATION
        self.logger.info(f"State transitioned to: {self.current_state.name}")
        self.emit_message('state_update', {'status': self.current_state.name})

    def on_evaluation_event(self, data):
        """Handler for when the response has been evaluated."""
        payload = data.get('payload', {})
        if payload.get('is_vulnerable', False):
            self.current_state = AttackState.ATTACK_SUCCESSFUL
            self.logger.info(f"State transitioned to: {self.current_state.name}")
        else:
            self.current_state = AttackState.ATTACK_FAILED
            self.logger.info(f"State transitioned to: {self.current_state.name}")

        # After evaluation, the state can revert to learning or idle
        self.current_state = AttackState.LEARNING
        self.logger.info(f"State transitioned to: {self.current_state.name}")
        self.emit_message('state_update', {'status': self.current_state.name})

    def run(self):
        """
        The agent's main loop. It stays connected to listen for events.
        """
        self.logger.info("Listening for events to track attack state...")
        self.sio.wait()

if __name__ == '__main__':
    # This block is for testing the AttackStateAgent independently.
    # It can be used to run the agent without the full Twinrad system.
    # agent = AttackStateAgent()
    # agent.connect()
    # agent.run()
    pass