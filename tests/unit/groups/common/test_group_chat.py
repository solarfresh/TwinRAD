from unittest.mock import AsyncMock, MagicMock

import pytest

from twinrad.agents.common.generic_agent import GenericAgent
from twinrad.groups.common.generic_group import GenericGroupChat
from twinrad.groups.common.generic_manager import GenericGroupManager
from twinrad.schemas.messages import Message
from twinrad.workflows.common.base_flow import SequentialFlow
from twinrad.workflows.common.termination import MaxRoundsCondition


@pytest.fixture
def setup_mock_agents():
    """
    A pytest fixture to create and configure mock agents for testing.
    This replaces the unittest.setUp() method.
    """
    # Create mock agents with predictable responses
    agent1 = MagicMock(spec=GenericAgent, name="Agent1")
    agent2 = MagicMock(spec=GenericAgent, name="Agent2")
    agent3 = MagicMock(spec=GenericAgent, name="Agent3")

    # Assign a return_value to the name attribute to ensure it acts as a string
    agent1.name = "Agent1"
    agent2.name = "Agent2"
    agent3.name = "Agent3"

    # Define the agents' mock responses.
    agent1.generate.return_value = Message(role="assistant", content="Response from Agent1", name="Agent1")
    agent2.generate.return_value = Message(role="assistant", content="Response from Agent2", name="Agent2")
    agent3.generate.return_value = Message(role="assistant", content="Response from Agent3", name="Agent3")

    return [agent1, agent2, agent3]


@pytest.mark.asyncio
async def test_conversation_terminates_at_max_rounds(setup_mock_agents):
    """
    Verify that the conversation terminates exactly after the
    number of rounds specified by MaxRoundsCondition.
    """
    max_rounds = 3

    # Use the agents from the fixture
    agents = setup_mock_agents

    # Instantiate the dependencies
    group_chat = GenericGroupChat(agents=agents)
    workflow = SequentialFlow(group_chat=group_chat)
    terminator = MaxRoundsCondition(max_rounds=max_rounds)

    # Instantiate the GroupChatManager
    manager = GenericGroupManager(
        name='TestGenericGroupManager',
        group_chat=group_chat,
        workflow=workflow,
        terminator=terminator
    )

    # Initiate the chat
    initial_message_content = "Hello, everyone."
    await manager.initiate_chat(sender=agents[0], message=initial_message_content)

    # Assert that the total number of messages is as expected
    expected_total_messages = max_rounds + 1 # Initial message + 3 responses
    assert len(group_chat.messages) == expected_total_messages, (
        f"Conversation should have terminated after {max_rounds} rounds, but had {len(group_chat.messages)} messages."
    )


@pytest.mark.asyncio
async def test_round_robin_speaker_selection(setup_mock_agents):
    """
    Verify that the agents are selected in the correct round-robin order.
    """
    max_rounds = 3

    # Use the agents from the fixture
    agents = setup_mock_agents

    # Instantiate the dependencies
    group_chat = GenericGroupChat(agents=agents)
    workflow = SequentialFlow(group_chat=group_chat)
    terminator = MaxRoundsCondition(max_rounds=max_rounds)

    # Instantiate the GroupChatManager
    manager = GenericGroupManager(
        name='TestGenericGroupManager',
        group_chat=group_chat,
        workflow=workflow,
        terminator=terminator
    )

    # Initiate the chat
    initial_message_content = "Hello, everyone."
    await manager.initiate_chat(sender=agents[0], message=initial_message_content)

    # Assertions for the order of speakers.
    expected_speakers = ["Agent1", "Agent2", "Agent3"]

    # Start from the second message, as the first is the initial user message.
    for i in range(1, max_rounds + 1):
        message = group_chat.messages[i - 1]
        assert message.name == expected_speakers[i - 1], (
            f"Round {i+1} speaker should have been {expected_speakers[i]}, but was {message.name}."
        )