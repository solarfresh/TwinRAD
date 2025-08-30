from unittest.mock import MagicMock

import pytest
from google.genai import Client, types
from google.genai.types import Candidate, GenerateContentResponse

from twinrad.clients.client_manager import ClientManager
from twinrad.clients.handlers.gemini_handler import GeminiHandler
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

    mock_client.models.generate_content.return_value = mock_response
    return mock_client

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
def mock_handlers(mock_gemini_client):
    """Mocks the concrete handler classes."""
    gemini_handler = GeminiHandler(config=ModelConfig(name="gemini-pro", api_key="dummy_api_key"))
    gemini_handler.client = mock_gemini_client
    handlers = {
        "gemini-pro": gemini_handler,
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

def test_handler_instantiation_success(mock_config, mock_handlers):
    """Verify that ClientManager correctly instantiates handlers from config."""
    manager = ClientManager(config=mock_config)

    # Assert that the internal handlers dictionary is populated correctly.
    assert "gemini-pro" in manager.handlers
    assert "gpt-3.5-turbo" in manager.handlers

def test_generate_call_success(mock_config, mock_handlers, mock_request):
    """Verify a successful request is routed to the correct handler."""
    manager = ClientManager(config=mock_config)

    # Mock the return value of the GeminiHandler's generate method.
    manager.handlers = mock_handlers

    response = manager.generate(request=mock_request)
    assert response.text == "Mocked Gemini response."

def test_generate_call_unknown_model(mock_config, mock_request):
    """Verify a ValueError is raised for an unconfigured model."""
    api_keys = {"gemini-pro": "gemini_key", "gpt-3.5-turbo": "openai_key"}
    manager = ClientManager(config=mock_config)

    # Change the request to use a non-existent model.
    mock_request.model = "unknown-model"

    # Try to make a request to a model not in the handlers dictionary.
    with pytest.raises(ValueError, match="Handler for model 'unknown-model' not found."):
        manager.generate(request=mock_request)