import asyncio
from uuid import uuid4

from transformers import AutoTokenizer
from vllm import AsyncLLMEngine
from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.sampling_params import SamplingParams

from twinrad.clients.handlers.base_handler import BaseHandler
from twinrad.schemas.clients import LLMRequest, LLMResponse, ModelConfig


class VLLMHandler(BaseHandler):
    """
    A concrete handler that manages a single, centralized vLLM engine
    to prevent GPU resource contention.
    """
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """Implements the Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(VLLMHandler, cls).__new__(cls)

        return cls._instance

    def __init__(self, config: ModelConfig, **kwargs):
        """Initializes the VLLM engine only once."""
        if self._initialized:
            return

        self.config = config
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.name)
        self.engine = None
        self._initialized = True

    async def ainit(self):
        """
        Asynchronously loads the vLLM engine. This method should be awaited
        at application startup to prevent blocking.
        """
        if self.engine is None:
            engine_args = AsyncEngineArgs(
                model=self.config.name,
                tensor_parallel_size=self.config.tensor_parallel_size,
                dtype="auto"
            )
            self.engine = AsyncLLMEngine.from_engine_args(engine_args)

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generates a response using the vLLM engine with a concurrency lock.
        """
        if self.engine is None:
            raise RuntimeError("VLLM engine is not initialized. Call ainit() first.")

        try:
            prompt = self._format_messages_for_vllm(request)

            sampling_params = SamplingParams(
                n=1,
                temperature=request.temperature,
                top_p=request.top_p,
                max_tokens=request.max_tokens,
            )

            request_id = str(uuid4())
            results_generator = self.engine.generate(
                prompt, sampling_params, request_id
            )

            final_output = ""
            async for output in results_generator:
                final_output = output.outputs[0].text

            if not final_output:
                raise ValueError("Received an empty response from the vLLM engine.")

            return LLMResponse(text=final_output)

        except Exception as e:
            raise RuntimeError(f"An error occurred in VLLMHandler: {e}")

    def _format_messages_for_vllm(self, request: LLMRequest) -> str:
        """
        Combines a list of messages into a single prompt string for vLLM.
        This method should be customized to match the specific model's chat template.
        """

        if hasattr(self.tokenizer, "chat_template") and self.tokenizer.chat_template is not None:
            messages_payload = []
            if request.system_message:
                messages_payload.append({"role": "system", "content": request.system_message})

            for msg in request.messages:
                messages_payload.append({"role": msg.role, "content": msg.content})

            full_prompt = self.tokenizer.apply_chat_template(messages_payload, tokenize=False, add_generation_prompt=True)
        else:
            self.logger.warning("No chat template found in the tokenizer configuration.")
            full_prompt = ""
            # Handle system message
            if request.system_message:
                full_prompt += request.system_message.strip() + "\n\n"

            # Format conversation turns
            for msg in request.messages:
                full_prompt += f"{msg.role}: {msg.content.strip()}\n\n"

            full_prompt += "assistant:" # The final prompt to the assistant

        return full_prompt.strip()
