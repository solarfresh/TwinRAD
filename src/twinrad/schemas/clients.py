from typing import List, Literal, Optional

from pydantic import BaseModel, NonNegativeInt

from twinrad.schemas.messages import Message


class LLMRequest(BaseModel):
    """A standardized schema for all model inference requests."""
    max_tokens: NonNegativeInt = 256
    messages: List[Message]
    model: str
    system_message: str = 'You are a helpful AI Assistant.'
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
    base_url: Optional[str] = None
    api_key: Optional[str] = None
