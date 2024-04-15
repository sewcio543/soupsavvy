"""
Module for the BaseTemplate class.

Templates are the components used to fill the generated structures with content.
They are the building blocks for the generators.
This way generated content can be controlled and customized.
"""

from abc import abstractmethod

from soupsavvy.testing.generators.base import BaseGenerator


class BaseTemplate(BaseGenerator):
    """
    Abstract base class for templates.

    BaseTemplate is also the subclass of BaseGenerator, all Templates
    implement BaseGenerator interface and are easy to interchange with
    other generators.
    """

    @abstractmethod
    def generate(self) -> str:
        """
        Generates a string based on the template.

        Returns
        -------
        str
            The generated string.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} is a base class and does not implement "
            "'generate' method."
        )
