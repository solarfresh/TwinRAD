from unittest.mock import MagicMock, PropertyMock

import pytest
from google.genai import Client, types
from google.genai.types import Candidate, GenerateContentResponse

from twinrad.clients.handlers.gemini_handler import GeminiHandler
from twinrad.schemas.clients import (LLMRequest, LLMResponse, Message,
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


@pytest.fixture
def gemini_handler(mock_gemini_client):
    """
    Fixture to create a GeminiHandler instance with a mocked client.
    """
    config = ModelConfig(name="gemini-pro")
    handler = GeminiHandler(config=config, api_key="dummy_api_key")
    handler.client = mock_gemini_client
    return handler


def test_gemini_handler_generate_success(gemini_handler):
    """
    Test that the handler correctly processes a successful API response.
    """
    request = LLMRequest(
        model="gemini-pro",
        messages=[Message(role="user", content="Hello, Gemini.", name='Test')],
        system_message="You are a helpful assistant.",
        max_tokens=100,
        temperature=0.7,
        top_p=0.9
    )

    response = gemini_handler.generate(request)

    # Assert that the handler returned the correct response schema
    assert isinstance(response, LLMResponse)
    assert response.text == "Mocked Gemini response."


def test_gemini_handler_with_no_response(gemini_handler):
    """
    Test that the handler raises an error for an empty API response.
    """
    # Mock a response with no content
    gemini_handler.client.models.generate_content.return_value = MagicMock(spec=GenerateContentResponse)

    request = LLMRequest(
        model="gemini-pro",
        messages=[Message(role="user", content="Test empty response.", name='Test')],
    )

    with pytest.raises(RuntimeError, match="An error occurred while calling the Gemini API:.*"):
        gemini_handler.generate(request)


def test_gemini_handler_with_api_error(gemini_handler):
    """
    Test that the handler raises an error when the API call fails.
    """
    # Mock the API call to raise an exception
    gemini_handler.client.models.generate_content.side_effect = Exception("API connection failed.")

    request = LLMRequest(
        model="gemini-pro",
        messages=[Message(role="user", content="Test API error.", name='Test')],
    )

    with pytest.raises(RuntimeError, match="An error occurred while calling the Gemini API"):
        gemini_handler.generate(request)