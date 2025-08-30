from typing import Optional

import openai
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

from twinrad.clients.handlers.base_handler import BaseHandler
from twinrad.schemas.clients import LLMRequest, LLMResponse, ModelConfig


class OpenAIHandler(BaseHandler):
    """
    A concrete handler that adapts the OpenAI API to the BaseHandler interface.
    """

    def __init__(self, config: ModelConfig):
        self.config = config
        # The OpenAI client automatically reads from the OPENAI_API_KEY env var
        # but we can explicitly pass it from the config.
        self.client = OpenAI(api_key=self.config.api_key, base_url=self.config.base_url)

    def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generates a response from the OpenAI API based on a standardized LLMRequest.

        Args:
            request (LLMRequest): The standardized request object.

        Returns:
            LLMResponse: The standardized response object.
        """
        try:
            # 1. Adapt the standardized LLMRequest to OpenAI's format.
            messages_payload = []
            if request.system_message:
                messages_payload.append({"role": "system", "content": request.system_message})

            # The message payload should be a list of dictionaries with 'role' and 'content'
            for msg in request.messages:
                messages_payload.append({"role": msg.role, "content": msg.content})

            # 2. Make the API call to OpenAI's Chat Completions endpoint.
            response: ChatCompletion = self.client.chat.completions.create(
                model=request.model,
                messages=messages_payload,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
            )

            # 3. Handle potential API errors and adapt the response.
            if not response.choices:
                raise ValueError("Received an empty response from the OpenAI API.")

            response_text: Optional[str] = response.choices[0].message.content
            if response_text is None:
                raise ValueError("Response text was None.")

            return LLMResponse(text=response_text)

        except openai.APIError as e:
            # Re-raise with a generic runtime error for consistent error handling.
            raise RuntimeError(f"An OpenAI API error occurred: {e}")
        except Exception as e:
            # Catch other potential errors
            raise RuntimeError(f"An unexpected error occurred in OpenAIHandler: {e}")