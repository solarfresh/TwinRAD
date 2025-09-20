import json
from unittest.mock import AsyncMock, patch

import pytest

from twinrad.core.clients.client_manager import ClientManager
from twinrad.core.schemas.agents import AgentConfig
from twinrad.core.schemas.messages import Message
from twinrad.threat_hunting.knowledge.agents import SelectorFinder
from twinrad.threat_hunting.knowledge.tools import PageLoaderTool


@pytest.mark.asyncio
async def test_sf_generate_success_flow():
    """
    Tests the end-to-end success flow of the SelectorFinder agent.
    """
    # Mock configurations and clients
    mock_config = AgentConfig(name='selector_finder', model='gemini-pro')
    mock_client_manager = AsyncMock(spec=ClientManager)

    # Mock LLM responses
    mock_llm_response_1 = AsyncMock(text=json.dumps({"tool": "load_page_html", "args": {"url": "http://example.com"}}))
    mock_llm_response_2 = AsyncMock(text="div.product-price")

    # Mock tool output
    mock_tool_output = json.dumps({"url": "http://example.com", "html_content": "<html><body><div class='product-price'>$20.00</div></body></html>"})

    # Mock the LLM client manager to return our canned responses in sequence
    mock_client_manager.generate.side_effect = [mock_llm_response_1, mock_llm_response_2]

    # Mock the tool run method
    mock_tool = AsyncMock(spec=PageLoaderTool)
    mock_tool.run.return_value = mock_tool_output
    mock_tool.get_name.return_value = "load_page_html"

    # Initialize the agent with mocked components
    agent = SelectorFinder(mock_config, mock_client_manager)

    # Patch the tool attribute to use our mock
    with patch.object(agent, 'tool', new=mock_tool):
        messages = [Message(role='user', content="Find the price on http://example.com", name='Test')]
        result = await agent.generate(messages)

    # Final assertion on the returned message
    assert result.role == 'assistant'
    assert result.content == "div.product-price"

@pytest.mark.asyncio
async def test_sf_generate_first_llm_call_fails():
    """
    Tests that the agent handles a non-JSON response from the first LLM call.
    """
    mock_config = AgentConfig(name='selector_finder', model='gemini-pro')
    mock_client_manager = AsyncMock(spec=ClientManager)

    # The first LLM call returns a plain string, not a JSON tool call
    mock_llm_response_1 = AsyncMock(text="I'm sorry, I cannot fulfill this request.")
    mock_client_manager.generate.return_value = mock_llm_response_1

    agent = SelectorFinder(mock_config, mock_client_manager)

    messages = [Message(role='user', content="Find the price on http://example.com", name='Test')]
    result = await agent.generate(messages)

    # Assert that the agent returns the LLM's raw response
    assert result.role == 'assistant'
    assert result.content == "Error: Could not generate a response."


@pytest.mark.asyncio
async def test_sf_tool_run_returns_error():
    """
    Tests that the agent correctly propagates an error from the tool.
    """
    mock_config = AgentConfig(name='selector_finder', model='gemini-pro')
    mock_client_manager = AsyncMock(spec=ClientManager)

    # First LLM call is successful
    mock_llm_response_1 = AsyncMock(text=json.dumps({"tool": "load_page_html", "args": {"url": "http://invalid-url.com"}}))
    mock_client_manager.generate.return_value = mock_llm_response_1

    # Tool run returns an error
    mock_tool = AsyncMock(spec=PageLoaderTool)
    mock_tool.run = AsyncMock(side_effect=RuntimeError('Page navigation failed.'))
    mock_tool.get_name.return_value = "load_page_html"

    agent = SelectorFinder(mock_config, mock_client_manager)
    with patch.object(agent, 'tool', new=mock_tool):
        messages = [Message(role='user', content="Find the price on http://invalid-url.com", name='Test')]
        result = await agent.generate(messages)

    # Assert that the agent returns the tool's error message
    assert result.role == 'assistant'
    assert result.content == "Error: Could not generate a response."

    # Verify that the second LLM call was NOT made
    mock_client_manager.generate.assert_called_once()  # Only the first call