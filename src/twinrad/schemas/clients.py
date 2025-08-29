from typing import Literal, Optional

from pydantic import BaseModel, NonNegativeInt


class LLMRequest(BaseModel):
    """A standardized schema for all model inference requests."""
    model_name: str
    prompt: str
    max_tokens: NonNegativeInt = 256
    temperature: float = 0.7
    top_p: float = 0.95


class LLMResponse(BaseModel):
    """A standardized schema for all model inference responses."""
    text: str


class ModelConfig(BaseModel):
    """Defines the configuration for a single model or API."""
    name: str
    mode: Literal["vllm", "openai", "generic_api"] = "generic_api"
    path: Optional[str] = None
    url: Optional[str] = None
    api_key: Optional[str] = None
