from typing import Dict
from twinrad.clients.handlers.base_handler import BaseHandler
from twinrad.clients.handlers.gemini_handler import GeminiHandler
from twinrad.clients.handlers.openai_handler import OpenAIHandler
from twinrad.schemas.clients import LLMRequest, LLMResponse, ClientConfig


class ClientManager:
    """
    Manages all LLM handlers and routes requests from agents.
    It acts as a single point of entry and enforces access permissions.
    """

    def __init__(self, config: ClientConfig):
        self.config = config
        self.handlers: Dict[str, BaseHandler] = {}
        self._instantiate_handlers()

    def _instantiate_handlers(self):
        """
        Instantiates all necessary LLM handlers based on the provided configuration.
        """
        for model_config in self.config.models:
            api_key = model_config.api_key
            if not api_key:
                raise ValueError(f"API key for model '{model_config.name}' is not provided.")

            if model_config.mode == "gemini":
                self.handlers[model_config.name] = GeminiHandler(config=model_config)
            elif model_config.mode == "openai":
                self.handlers[model_config.name] = OpenAIHandler(config=model_config)
            # Add other handlers (e.g., VllmHandler) here as they are implemented

    def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Validates agent permissions and generates a response using the correct handler.

        Args:
            agent_id (str): The ID of the agent making the request.
            request (LLMRequest): The standardized request to be processed.

        Returns:
            LLMResponse: The standardized response from the LLM.

        Raises:
            ValueError: If the requested model is not configured.
        """
        # Get the correct handler
        handler = self.handlers.get(request.model)
        if not handler:
            raise ValueError(f"Handler for model '{request.model}' not found. Check your configuration.")

        # Route the request to the handler
        return handler.generate(request)
