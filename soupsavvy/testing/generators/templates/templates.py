"""
Module with implementation of templates that complement generator components
providing more customization options.

Classes
-------
- `EmptyTemplate` - Template for generating an empty string.
- `ConstantTemplate` - Template for generating a constant string.
- `ChoiceTemplate` - Template for randomly selecting from a list of choices.
- `RandomTemplate` - Template for generating a random string of ASCII letters and digits.
"""

import random
import string
from collections.abc import Iterable
from typing import Optional

from soupsavvy.testing.generators.templates.base import BaseTemplate


class EmptyTemplate(BaseTemplate):
    """
    Template for generating an empty string.
    Convenience template for default generator behavior.

    Example
    -------
    >>> template = EmptyTemplate()
    ... template.generate()
    ''
    """

    def generate(self) -> str:
        """
        Generates an empty string.

        Returns
        -------
        str
            An empty string.
        """
        return ""


class ConstantTemplate(BaseTemplate):
    """
    Template for generating a constant string.
    Convenience template for always generating the same content.

    Example
    -------
    >>> template = ConstantTemplate("Hello World!")
    ... template.generate()
    'Hello World!'
    """

    def __init__(self, value: str) -> None:
        """
        Initializes `ConstantTemplate` instance.

        Parameters
        ----------
        value : str
            The constant string value.
        """
        self.value = str(value)

    def generate(self) -> str:
        """
        Generates the constant string.

        Returns
        -------
        str
            The constant string value defined in initializer.
        """
        return self.value


class ChoiceTemplate(BaseTemplate):
    """
    Template for randomly selecting from a list of choices.

    Example
    -------
    >>> template = ChoiceTemplate(["apple", "banana", "cherry"], seed=42)
    ... template.generate()
    'cherry'
    """

    def __init__(self, choices: Iterable, seed: Optional[int] = None) -> None:
        """
        Initializes `ChoiceTemplate` instance.

        Parameters
        ----------
        choices : Iterable
            Iterable of choices to select from.
        seed : int, optional
            Random seed for reproducibility. Defaults to None, no seed is used.
        """
        self.choices = list(choices)
        self.randomizer = random.Random(seed)

    def generate(self) -> str:
        """
        Generates a random choice from the list of choices.

        Returns
        -------
        str
            The randomly selected choice.
        """
        choice = self.randomizer.choice(self.choices)
        return str(choice)


class RandomTemplate(BaseTemplate):
    """
    Template for generating a random string of ASCII letters and digits.

    Example
    -------
    >>> template = RandomTemplate(length=4, seed=42)
    ... template.generate()
    'Nbrn'
    """

    _SCOPE = string.ascii_letters + string.digits

    def __init__(self, length: int = 4, seed: Optional[int] = None) -> None:
        """
        Initializes `RandomTemplate` instance.

        Parameters
        ----------
        length : int, optional
            Length of the random string. Defaults to 4.
        seed : int, optional
            Random seed for reproducibility. Defaults to None.
        """
        self._check_length(length)
        self.length = length
        self.randomizer = random.Random(seed)

    def _check_length(self, length: int) -> None:
        """
        Checks if the input length is a valid value.

        Parameters
        ----------
        length : int
            Input length to check.

        Raises
        ------
        TypeError
            If the length is not an integer.
        ValueError
            If the length is less than 1.
        """
        if not isinstance(length, int):
            raise TypeError(f"length must be an integer, got '{type(length)}'")

        if length < 1:
            raise ValueError(f"length must be greater than 0, got '{length}'")

    def generate(self) -> str:
        """
        Generates a random string from ASCII letters and digits.

        Returns
        -------
        str
            The generated random string.
        """
        return self._generate_unique_id()

    def _generate_unique_id(self) -> str:
        """
        Generates a unique identifier string of the specified length.

        Returns
        -------
        str
            The generated unique identifier string.
        """
        new_id = "".join(
            self.randomizer.choices(
                self._SCOPE,
                k=self.length,
            )
        )
        return new_id
