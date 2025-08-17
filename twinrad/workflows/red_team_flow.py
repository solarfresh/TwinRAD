from typing import Union

from autogen.agentchat import Agent, GroupChat

from configs.logging_config import setup_logging
from twinrad.schemas.agents import AgentName

logger = setup_logging(name=f"[FLOW]")

def speaker_selection_func(
    last_speaker: Agent,
    groupchat: GroupChat
) -> Union[Agent, None]:
    """
    A custom speaker selection function that includes a PLANNER_AGENT.
    The PLANNER_AGENT is activated at specific points to decide the next speaker.
    """
    messages = groupchat.messages
    if not messages:
        # Initial turn, start with the PromptGenerator
        return groupchat.agent_by_name(AgentName.PROMPT_GENERATOR.value)

    last_message = messages[-1]
    last_speaker_name = last_speaker.name

    # Always give the PLANNER_AGENT a turn after a key event
    # A key event is a response from the target model or an evaluation result
    if last_speaker_name in [
        AgentName.USER_PROXY.value,
        AgentName.GOURMET_AGENT.value,
        AgentName.EVALUATOR_AGENT.value,
        AgentName.INTROSPECTION_AGENT.value
    ]:
        # After GourmetAgent or EvaluatorAgent speaks, hand off to the Planner to decide the next step
        return groupchat.agent_by_name(AgentName.PLANNER_AGENT.value)

    # The Planner's response should explicitly name the next speaker.
    # We check if the last message from the Planner contains a recognized agent name.
    if last_speaker_name == AgentName.PLANNER_AGENT.value:
        planner_message = last_message.get("content", "")
        # The planner's message should look like: "Next speaker: PromptGenerator"
        for agent_name in AgentName:
            if agent_name.value in planner_message:
                return groupchat.agent_by_name(agent_name.value)

    # Fallback to a predefined sequence if the flow is not handled by the planner
    if last_speaker_name == AgentName.PROMPT_GENERATOR.value:
        return groupchat.agent_by_name(AgentName.GOURMET_AGENT.value)

    # After a successful evaluation, the IntrospectionAgent speaks
    if last_speaker_name == AgentName.EVALUATOR_AGENT.value:
        # This part of the logic could also be handled by the Planner
        return groupchat.agent_by_name(AgentName.INTROSPECTION_AGENT.value)

    return None # End the conversation if the flow is complete or an error occurs