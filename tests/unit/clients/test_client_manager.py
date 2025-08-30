from unittest.mock import AsyncMock, MagicMock

import pytest
from google.genai import Client, types
from google.genai.types import Candidate, GenerateContentResponse
from openai import AsyncOpenAI

from twinrad.clients.client_manager import ClientManager
from twinrad.clients.handlers.gemini_handler import GeminiHandler
from twinrad.clients.handlers.openai_handler import OpenAIHandler
from twinrad.schemas.clients import (ClientConfig, LLMRequest, Message,
                                     ModelConfig)


@pytest.fixture
def mock_gemini_client():
    """
    Mocks the Gemini API client to prevent real API calls.
    """
    mock_client = MagicMock(spec=Client)

    # Create a mock response object that mimics the real Gemini response structure.
    mock_response = MagicMock(spec=GenerateContentResponse)
    mock_response.candidates = [Candidate(content=types.UserContent(parts=[types.Part.from_text(text="Mocked Gemini response.")]))]
    mock_response.text = "Mocked Gemini response."

    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)
    return mock_client

@pytest.fixture
def mock_openai_client():
    """
    Mocks the OpenAI API client and its chat.completions.create method
    to prevent real API calls.
    """
    mock_client = MagicMock(spec=AsyncOpenAI)
    return mock_client

@pytest.fixture
def gemini_handler(mock_gemini_client):
    """
    Fixture to create a GeminiHandler instance with a mocked client.
    """
    config = ModelConfig(name="gemini-pro", api_key="dummy_api_key")
    handler = GeminiHandler(config=config)
    handler.client = mock_gemini_client
    return handler

@pytest.fixture
def openai_handler(mock_openai_client):
    """
    Fixture to create an OpenAIHandler instance with a mocked client.
    """
    config = ModelConfig(name="gpt-3.5-turbo", api_key="dummy_api_key")
    handler = OpenAIHandler(config=config)
    handler.client = mock_openai_client
    return handler

# A pytest fixture to create a mock ClientConfig
@pytest.fixture
def mock_config():
    """Provides a mocked ClientConfig for testing."""
    return ClientConfig(
        models=[
            ModelConfig(name="gemini-pro", mode="gemini", api_key="gemini_key"),
            ModelConfig(name="gpt-3.5-turbo", mode="openai", api_key="openai_key"),
        ],
    )

# A pytest fixture to mock the API handlers
@pytest.fixture
def mock_handlers(gemini_handler, openai_handler):
    """Mocks the concrete handler classes."""
    handlers = {
        "gemini-pro": gemini_handler,
        "gpt-3.5-turbo": openai_handler
    }

    return handlers

# A test fixture for a standardized request
@pytest.fixture
def mock_request():
    """Provides a mock LLMRequest."""
    return LLMRequest(
        model="gemini-pro",
        messages=[Message(role="user", content="Hello", name='Test')],
        system_message="You are a test.",
    )

## Test Cases for ClientManager

@pytest.mark.asyncio
async def test_handler_instantiation_success(mock_config, mock_handlers):
    """Verify that ClientManager correctly instantiates handlers from config."""
    manager = ClientManager(config=mock_config)
    await manager.initialize()

    # Assert that the internal handlers dictionary is populated correctly.
    assert "gemini-pro" in manager.handlers
    assert "gpt-3.5-turbo" in manager.handlers

@pytest.mark.asyncio
async def test_generate_call_success(mock_config, mock_handlers, mock_request):
    """Verify a successful request is routed to the correct handler."""
    manager = ClientManager(config=mock_config)

    await manager.initialize()

    manager.handlers = mock_handlers

    response = await manager.generate(request=mock_request)
    assert response.text == "Mocked Gemini response."

@pytest.mark.asyncio
async def test_generate_call_unknown_model(mock_config, mock_request):
    """Verify a ValueError is raised for an unconfigured model."""
    manager = ClientManager(config=mock_config)
    await manager.initialize()

    # Change the request to use a non-existent model.
    mock_request.model = "unknown-model"

    # Try to make a request to a model not in the handlers dictionary.
    with pytest.raises(ValueError, match="Handler for model 'unknown-model' not found."):
        await manager.generate(request=mock_request)