from abc import ABC, abstractmethod
from typing import List, Union

from twinrad.schemas.messages import Message


class TerminationCondition(ABC):
    @abstractmethod
    def should_end(self, message: Message, current_round: int) -> bool:
        pass


class MaxRoundsCondition(TerminationCondition):
    def __init__(self, max_rounds: int):
        if max_rounds <= 0:
            raise ValueError("max_rounds must be a positive integer.")
        self.max_rounds = max_rounds

    def should_end(self, message: Message, current_round: int) -> bool:
        """
        Returns True if the conversation has reached the maximum number of rounds.

        Args:
            message (Message): The current message to check.
            current_round (int): The current round number.

        Returns:
            bool: True if the conversation should end, False otherwise.
        """
        return current_round > self.max_rounds


class StringMatchCondition(TerminationCondition):
    """
    Terminates the conversation if specific strings appear in the responses with a certain frequency.
    """

    def __init__(self, match_strings: List[str], required_frequency: int):
        if not match_strings:
            raise ValueError("match_strings cannot be an empty list.")

        if required_frequency <= 0:
            raise ValueError("required_frequency must be a positive integer.")

        self.match_count = 0
        self.match_strings = match_strings
        self.required_frequency = required_frequency

    def should_end(self, message: Message, current_round: int) -> bool:
        """
        Returns True if a match string appears at or above the required frequency.

        Args:
            message (Message): The current message to check.
            current_round (int): The current round number (not used in this implementation).

        Returns:
            bool: True if the conversation should end, False otherwise.
        """
        if any(match_str in message.content for match_str in self.match_strings):
            self.match_count += 1
        else:
            self.match_count = 0

        return self.match_count >= self.required_frequency


class CompositeCondition(TerminationCondition):
    """
    Checks multiple termination conditions and returns True if any of them are met.
    """

    def __init__(self, conditions: List[Union[TerminationCondition, str]], check_all: bool = False):
        """
        Initializes the composite condition with a list of other conditions or strings.

        Args:
            conditions (List[Union[TerminationCondition, str]]): A list of conditions to check.
                Can be a list of TerminationCondition objects, a list of strings, or a mix of both.
                If a string is provided:
                    - max_rounds: Creates a MaxRoundsCondition with the string as the max rounds.
                    - string_match: Creates a StringMatchCondition with the string as the match string and a default frequency of 1.
            check_all (bool): If True, all conditions must be met to terminate.
                              If False (default), only one condition needs to be met.
        """
        if not conditions:
            raise ValueError("conditions list cannot be empty.")

        self._condition_classes = {
            'max_rounds': MaxRoundsCondition,
            'string_match': StringMatchCondition
        }

        self._internal_conditions: List[TerminationCondition] = []
        for condition in conditions:
            if isinstance(condition, str):
                # Automatically create a StringMatchCondition for a string input.
                # A default frequency of 1 is assumed.
                self._internal_conditions.append(self._condition_classes[condition](match_strings=[condition], required_frequency=1))
            elif isinstance(condition, TerminationCondition):
                self._internal_conditions.append(condition)
            else:
                raise TypeError(f"Unsupported condition type: {type(condition)}. Expected 'str' or 'TerminationCondition'.")

        if not self._internal_conditions:
            raise ValueError("No valid conditions were provided.")

        self.check_all = check_all

    def should_end(self, message: Message, current_round: int) -> bool:
        """
        Returns True if any (or all, if specified) of the contained conditions are met.

        Args:
            message (Message): The current message to check.
            current_round (int): The current round number.

        Returns:
            bool: True if the combined termination condition is met, False otherwise.
        """
        results = (cond.should_end(message, current_round) for cond in self._internal_conditions)

        if self.check_all:
            # All conditions must return True (Logical AND)
            return all(results)
        else:
            # At least one condition must return True (Logical OR)
            return any(results)