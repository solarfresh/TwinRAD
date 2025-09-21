from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from twinrad.core.groups.base_group import BaseGroupChat
from twinrad.core.groups.base_manager import BaseRoom
from twinrad.core.schemas.groups import RoomConfig
from twinrad.core.schemas.messages import Message
from twinrad.core.workflows.base_flow import BaseFlow
from twinrad.core.workflows.termination import MaxRoundsCondition


# Mock classes to simulate dependencies
class MockBaseGroupChat(BaseGroupChat):

    def __init__(self):
        self._chat_history = []
        self._messages = []

    def add_message(self, message):
        self._chat_history.append(message)
        self._messages.append(message)


class MockBaseFlow(BaseFlow):

    def __init__(self, agents):
        self.agents = agents

    def select_speaker(self, messages):
        # A simple mock flow that returns a speaker in a fixed order
        return self.agents[len(messages) % len(self.agents)]

class MockBaseAgent:

    def __init__(self, name):
        self.name = name

    async def generate(self, messages):
        return Message(role='assistant', content=f"Response from {self.name}", name=self.name)

# Instantiate a mock chat and agents for tests
mock_agents = [MockBaseAgent("Agent1"), MockBaseAgent("Agent2")]
mock_group_chat = MockBaseGroupChat()
mock_flow = MockBaseFlow(mock_agents)
mock_terminator = MaxRoundsCondition(max_rounds=3)

@pytest.fixture
def mock_config():
    base_room_config = MagicMock(spec=RoomConfig)
    base_room_config.name = 'Test'
    base_room_config.max_rounds = 3
    base_room_config.turn_limit = 100
    return base_room_config

# Test the BaseRoom class
@pytest.fixture
def base_room(mock_config):
    with patch('twinrad.core.clients.client_manager.ClientManager'):
        room = BaseRoom(config=mock_config)
        room.group_chat = mock_group_chat
        room.workflow = mock_flow
        room.terminator = mock_terminator
        return room

@pytest.mark.asyncio
async def test_base_room_initiate_chat_string(base_room):
    # Reset mock objects for a clean test
    base_room.group_chat._messages = []
    base_room.current_round = 0

    messages = await base_room.initiate_chat(message="Hello world")

    assert len(messages) == 4
    assert messages[0].content == "Hello world"
    assert messages[0].role == "user"
    assert messages[0].name == "User"

@pytest.mark.asyncio
async def test_base_room_initiate_chat_message_object(base_room):
    # Reset mock objects for a clean test
    base_room.group_chat._messages = []
    base_room.current_round = 0

    message_obj = Message(role="user", content="Test message", name="TestUser")
    messages = await base_room.initiate_chat(message=message_obj)

    assert len(messages) == 4
    assert messages[0].content == "Test message"
    assert messages[0].name == "TestUser"

@pytest.mark.asyncio
async def test_base_room_run_chat_normal_flow(base_room):
    # Reset mock objects and set up initial state
    base_room.group_chat._messages = [Message(role="user", content="Initial", name="User")]
    base_room.current_round = 1

    with patch.object(base_room.workflow, 'select_speaker', side_effect=[mock_agents[index % 2] for index in range(3)]) as mock_select, \
         patch.object(base_room.group_chat, 'add_message', ) as mock_add_message:

        await base_room.run_chat()

        # The loop should run until max_rounds is met
        assert mock_select.call_count == 3
        assert mock_add_message.call_count == 3
        assert base_room.current_round == 4

@pytest.mark.asyncio
async def test_base_room_run_chat_termination(base_room):
    # Reset mock objects and set up an initial state that will terminate after 1 round
    base_room.terminator.max_rounds = 1
    base_room.group_chat._messages = [Message(role="user", content="Initial", name="User")]
    base_room.current_round = 1

    with patch.object(base_room.workflow, 'select_speaker', side_effect=[mock_agents[0]]) as mock_select, \
         patch.object(base_room.group_chat, 'add_message') as mock_add_message:

        await base_room.run_chat()

        # The loop should run once and then terminate
        assert mock_select.call_count == 1
        assert mock_add_message.call_count == 1
        assert base_room.current_round == 2

@pytest.mark.asyncio
async def test_base_room_run_chat_error_handling(base_room):
    # Reset mock objects
    base_room.group_chat._messages = [Message(role="user", content="Initial", name="User")]
    base_room.current_round = 1
    base_room.terminator.max_rounds = 3

    # Mock the agent's generate method to raise an exception on the first call
    mock_agents[0].generate = AsyncMock(side_effect=Exception("API Error"))

    messages = await base_room.run_chat()

    # The loop should break after the error occurs
    assert len(messages) == 1
    assert base_room.current_round == 1 # The round should not increment after an error