"""
Module for the BaseGenerator abstract class that is a parent for all generators.

soupsavvy generator is anything that generates content,
they should all inherit from this class and implement the 'generate' method.
"""

from abc import ABC, abstractmethod


class BaseGenerator(ABC):
    """
    Abstract base class for all kind of soupsavvy generators.

    All components generating content should inherit from this class
    and implement the 'generate' method to return the generated content.
    """

    @abstractmethod
    def generate(self) -> str:
        raise NotImplementedError(
            f"{self.__class__.__name__} is a base class and does not implement "
            "'generate' method."
        )
