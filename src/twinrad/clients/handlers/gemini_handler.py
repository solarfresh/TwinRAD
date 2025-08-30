from google import genai
from google.genai import types

from twinrad.clients.handlers.base_handler import BaseHandler
from twinrad.schemas.clients import LLMRequest, LLMResponse, ModelConfig


class GeminiHandler(BaseHandler):
    def __init__(self, config: ModelConfig):
        self.config = config
        # Configure the Gemini API client
        self.client = genai.Client(api_key=self.config.api_key)

    def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generates a response from the Gemini API based on a standardized request.
        """
        try:
            # Prepare the request payload for Gemini
            # Note: Gemini's API often expects a list of messages, even for a single-turn request.
            messages_payload = []
            for msg in request.messages:
                messages_payload.append(types.Part.from_text(text=msg.content))

            # Extract generation configuration from the standardized request schema
            generation_config = types.GenerateContentConfig(
                system_instruction=request.system_message,
                max_output_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p
            )

            # Call the Gemini API
            response = self.client.models.generate_content(
                model=request.model,
                contents=[types.UserContent(parts=messages_payload)],
                config=generation_config
            )

            # Check for potential errors or blocked content
            if not response or not response.text:
                raise ValueError("Received an empty or invalid response from the Gemini API.")

            # Extract the text and wrap it in the standardized response schema
            response_text = response.text
            return LLMResponse(text=response_text)

        except Exception as e:
            # Handle API-specific exceptions and provide a clear error message
            raise RuntimeError(f"An error occurred while calling the Gemini API: {e}")