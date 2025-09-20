from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from openai import APIError, AsyncOpenAI
from openai.types.chat.chat_completion import ChatCompletion, Choice
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from openai.types.completion_usage import CompletionUsage

from twinrad.core.clients.handlers.openai_handler import OpenAIHandler
from twinrad.core.schemas.clients import (LLMRequest, LLMResponse, Message,
                                          ModelConfig)


@pytest.fixture
def mock_openai_client():
    """
    Mocks the OpenAI API client and its chat.completions.create method
    to prevent real API calls.
    """
    mock_client = MagicMock(spec=AsyncOpenAI)
    return mock_client

@pytest.fixture
def mock_openai_response():
    # Mock the return value of chat.completions.create()
    mock_response = ChatCompletion(
        id="chatcmpl-123",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    content="Mocked OpenAI response.",
                    role="assistant",
                ),
                logprobs=None,
            )
        ],
        created=1677652288,
        model="gpt-3.5-turbo",
        object="chat.completion",
        system_fingerprint="fp_44709d6fcb",
        usage=CompletionUsage(completion_tokens=10, prompt_tokens=10, total_tokens=20)
    )

    return mock_response

@pytest.fixture
def openai_handler(mock_openai_client):
    """
    Fixture to create an OpenAIHandler instance with a mocked client.
    """
    config = ModelConfig(name="gpt-3.5-turbo", api_key="dummy_api_key")
    handler = OpenAIHandler(config=config)
    handler.client = mock_openai_client
    return handler

@pytest.mark.asyncio
async def test_openai_handler_generate_success(openai_handler, mock_openai_response):
    """
    Test that the handler correctly processes a successful API response.
    """
    # Create a standardized request to send to the handler
    request = LLMRequest(
        model="gpt-3.5-turbo",
        messages=[Message(role="user", content="Hello, world.", name='Test')],
        max_tokens=100,
        temperature=0.7,
        top_p=0.9
    )

    openai_handler.client.chat.completions.create.return_value = AsyncMock(return_value=mock_openai_response)()
    # Call the handler's generate method
    response = await openai_handler.generate(request)

    # Assert that the handler returned the correct response schema and content
    assert isinstance(response, LLMResponse)
    assert response.text == "Mocked OpenAI response."

@pytest.mark.asyncio
async def test_openai_handler_empty_response(openai_handler, mock_openai_client):
    """
    Test that the handler raises a ValueError for an empty API response.
    """
    # Mock the API call to return a response with no choices
    mock_openai_client.chat.completions.create.return_value = ChatCompletion(
        id="chatcmpl-empty",
        choices=[],
        created=1677652288,
        model="gpt-3.5-turbo",
        object="chat.completion",
        system_fingerprint="fp_44709d6fcb",
        usage=CompletionUsage(completion_tokens=0, prompt_tokens=10, total_tokens=10)
    )

    request = LLMRequest(
        model="gpt-3.5-turbo",
        messages=[Message(role="user", content="Test empty response.", name='Test')],
    )

    with pytest.raises(RuntimeError, match="An unexpected error occurred in OpenAIHandler:.*"):
       await openai_handler.generate(request)

@pytest.mark.asyncio
async def test_openai_handler_api_error(openai_handler, mock_openai_client):
    """
    Test that the handler correctly catches and re-raises API-specific errors.
    """
    # Mock the API call to raise an exception
    mock_openai_client.chat.completions.create.side_effect = APIError("API connection failed.", request=MagicMock(spec=httpx.Request), body=None)

    request = LLMRequest(
        model="gpt-3.5-turbo",
        messages=[Message(role="user", content="Test API error.", name='Test')],
    )

    with pytest.raises(RuntimeError, match="An OpenAI API error occurred:.*"):
        await openai_handler.generate(request)