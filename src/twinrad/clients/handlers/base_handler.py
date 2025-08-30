from abc import ABC, abstractmethod

from twinrad.configs.logging_config import setup_logging
from twinrad.schemas.clients import LLMRequest, LLMResponse, ModelConfig


class BaseHandler(ABC):
    """
    An abstract base class that defines the common interface for all
    language model handlers.
    """

    def __init__(self, config: ModelConfig):
        self.config = config
        self.logger = setup_logging(name=f"[{self.__class__.__name__}]")

    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Abstract method to generate a response from a language model.

        All concrete handler implementations (e.g., VllmHandler, HttpHandler)
        must implement this method to process a standardized LLMRequest
        and return a standardized LLMResponse.
        """
        pass