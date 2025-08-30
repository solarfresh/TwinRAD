from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from transformers import AutoTokenizer
from vllm import AsyncLLMEngine

from twinrad.clients.handlers.vllm_handler import VLLMHandler
from twinrad.schemas.clients import (LLMRequest, LLMResponse, Message,
                                     ModelConfig)


# We are mocking the entire class, so no need for `from_engine_args`
@pytest.fixture(autouse=True)
def mock_vllm_dependencies(mocker):
    """Mocks the external dependencies of VLLMHandler."""
    # 1. Mock the vLLM engine instance
    mock_engine_instance = mocker.MagicMock(spec=AsyncLLMEngine)

    # 2. Mock the AsyncLLMEngine class constructor to return our mock instance
    mocker.patch("vllm.AsyncLLMEngine.from_engine_args", return_value=mock_engine_instance)

    # 3. Mock the AutoTokenizer class constructor
    mock_tokenizer_instance = mocker.MagicMock(spec=AutoTokenizer)
    mock_tokenizer_instance.chat_template = "mock_template"
    mock_tokenizer_instance.apply_chat_template = mocker.MagicMock(return_value="mocked prompt with template")
    mocker.patch("transformers.AutoTokenizer.from_pretrained", return_value=mock_tokenizer_instance)

    # Reset the VLLMHandler singleton instance to ensure a clean state for each test
    VLLMHandler._instance = None
    VLLMHandler._initialized = False

    return {
        "engine": mock_engine_instance,
        "tokenizer": mock_tokenizer_instance
    }

@pytest_asyncio.fixture
async def vllm_handler(mock_vllm_dependencies):
    """Provides a VLLMHandler instance initialized asynchronously."""
    config = ModelConfig(
        name="test-vllm-model",
        mode="vllm",
        api_key="", # Not used by VLLM
        tensor_parallel_size=1
    )
    handler = VLLMHandler(config=config)
    await handler.ainit()
    yield  handler

    # We need to manually reset the singleton for each test
    VLLMHandler._instance = None
    VLLMHandler._initialized = False

@pytest.fixture
def mock_request():
    """Provides a mock LLMRequest."""
    return LLMRequest(
        model="test-vllm-model",
        messages=[Message(role="user", content="Test message", name="Test")],
        system_message="You are a helpful assistant.",
        max_tokens=50,
        temperature=0.7,
        top_p=0.9
    )

@pytest.fixture
def mock_async_generator(mocker):
    """Mocks a full async generator."""
    # 1. Create the mock objects that will be yielded
    mock_outputs = [
        mocker.MagicMock(outputs=[mocker.MagicMock(text="First chunk.")]),
        mocker.MagicMock(outputs=[mocker.MagicMock(text="Second chunk.")]),
        mocker.MagicMock(outputs=[mocker.MagicMock(text="Final result.")])
    ]

    # 2. Return an AsyncMock that will yield these objects.
    # The `side_effect` is a list of objects that the mock will iterate over.
    async_mock = mocker.AsyncMock()
    async_mock.__aiter__.return_value = mock_outputs
    return async_mock

## Test Cases ##

@pytest.mark.asyncio
async def test_vllm_handler_generation_success(
    vllm_handler,
    mock_request,
    mock_vllm_dependencies,
    mock_async_generator
):
    """Test that the handler correctly processes a successful response."""
    mock_vllm_dependencies['engine'].generate.return_value = mock_async_generator

    # Run the `generate` method, which consumes the async generator
    response = await vllm_handler.generate(mock_request)

    # Assertions
    assert isinstance(response, LLMResponse)
    assert response.text == "Final result." # The handler accumulates all chunks
    mock_vllm_dependencies["engine"].generate.assert_called_once()

@pytest.mark.asyncio
async def test_vllm_handler_generation_no_response(
    vllm_handler,
    mock_request,
    mock_vllm_dependencies
):
    """Test that the handler raises an error for an empty response."""
    # Mock the result to be an empty string
    mock_output_list = [MagicMock(outputs=[MagicMock(text="")])]
    async_mock = AsyncMock()
    async_mock.__aiter__.return_value = mock_output_list
    mock_vllm_dependencies["engine"].generate.return_value = async_mock

    with pytest.raises(RuntimeError, match="An error occurred in VLLMHandler: Received an empty response from the vLLM engine."):
        await vllm_handler.generate(mock_request)

@pytest.mark.asyncio
async def test_vllm_handler_engine_not_initialized():
    """Test that generate raises an error if the engine is not initialized."""
    config = ModelConfig(name="test-vllm-model", mode="vllm", api_key="", tensor_parallel_size=1)
    handler = VLLMHandler(config=config)

    with pytest.raises(RuntimeError, match=r"VLLM engine is not initialized\. Call ainit\(\) first\."):
        await handler.generate(LLMRequest(model="test-vllm-model", messages=[]))

    # Clean up the singleton instance
    VLLMHandler._instance = None
    VLLMHandler._initialized = False

@pytest.mark.asyncio
async def test_vllm_handler_error_during_generation(vllm_handler, mock_request, mock_vllm_dependencies):
    """Test that the handler catches and re-raises an error during generation."""
    # Mock the generate method to raise an exception
    mock_vllm_dependencies["engine"].generate.side_effect = Exception("GPU out of memory.")

    with pytest.raises(RuntimeError, match="An error occurred in VLLMHandler: GPU out of memory."):
        await vllm_handler.generate(mock_request)