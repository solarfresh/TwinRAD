from abc import ABC, abstractmethod

from twinrad.schemas.clients import LLMRequest, LLMResponse


class BaseHandler(ABC):
    """
    An abstract base class that defines the common interface for all
    language model handlers.
    """

    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Abstract method to generate a response from a language model.

        All concrete handler implementations (e.g., VllmHandler, HttpHandler)
        must implement this method to process a standardized LLMRequest
        and return a standardized LLMResponse.
        """
        pass