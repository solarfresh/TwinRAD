from typing import Dict, List, Optional, Protocol, Union


class ModelClientProtocol(Protocol):
    """
    Protocol for a custom model client.

    A client class must implement the following methods and protocols:
    - create: Returns a response object that adheres to ModelClientResponseProtocol.
    - message_retrieval: Retrieves and returns messages from the response.
    - cost: Returns the cost of the response.
    - get_usage: Returns a usage summary dictionary.
    """

    class Message(Protocol):
        """Protocol for a message object within the response."""
        content: Optional[str]

    class Choice(Protocol):
        """Protocol for a choice object containing a message."""
        message: 'ModelClientProtocol.Message'

    class ModelClientResponseProtocol(Protocol):
        """Protocol for the overall response object."""
        choices: List['ModelClientProtocol.Choice']
        model: str

    def create(self, params: Dict) -> ModelClientResponseProtocol:
        """
        Sends a request to the model API and returns a response object.

        Args:
            params (Dict): A dictionary of parameters for the API request.

        Returns:
            ModelClientResponseProtocol: The response object adhering to the protocol.
        """
        ...

    def message_retrieval(self, response: ModelClientResponseProtocol) -> Union[List[str], List[Message]]:
        """
        Retrieves messages from the model's response.

        Args:
            response (ModelClientResponseProtocol): The response object from a create call.

        Returns:
            Union[List[str], List[Message]]: A list of message contents as strings or a list of message objects.
        """
        ...

    def cost(self, response: ModelClientResponseProtocol) -> float:
        """
        Calculates and returns the cost of the response.

        Args:
            response (ModelClientResponseProtocol): The response object.

        Returns:
            float: The total cost of the response.
        """
        ...

    @staticmethod
    def get_usage(response: ModelClientResponseProtocol) -> Dict:
        """
        Returns a dictionary with usage statistics for the response.

        Args:
            response (ModelClientResponseProtocol): The response object.

        Returns:
            Dict: A dictionary containing usage keys like 'prompt_tokens', 'completion_tokens', etc.
        """
        ...