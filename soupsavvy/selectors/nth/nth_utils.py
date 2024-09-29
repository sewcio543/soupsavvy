"""
Module with components used in nth selectors implementation.
Provide the ways of parsing and generating numbers from nth selectors.

Classes
-------
- `NthGenerator` - Generates a list of integers that match the nth CSS selector.
- `parse_nth` - Parses CSS nth selector and returns NthGenerator instance.
"""

import math
import re
from collections.abc import Callable, Generator
from dataclasses import dataclass
from itertools import count

# matches nth-selector that contains only step parameter - e.g. "2"
OFFSET_PATTERN = re.compile(r"^\d+$")
# matches nth-selector that contains only offset parameter - e.g. "-3n", "n"
STEP_PATTERN = re.compile(r"^-?\d*n$")
# matches nth-selector that contains both step and offset parameters - e.g. "-3n+2"
COMBINED_PATTERN = re.compile(r"^-?\d*n\+\d+$")


@dataclass
class NthGenerator:
    """
    Class for generating a list of integers that match the nth-child CSS selector.

    Parameters
    ----------
    step : int
        The step parameter of the nth-child CSS selector. Must be an integer.
    offset : int
        The offset parameter of the nth-child CSS selector.
        Must be a non-negative integer.

    Examples
    --------
    >>> nth = NthGenerator(step=2, offset=1)
    ... list(nth.generate(10))
    [1, 3, 5, 7, 9]

    >>> nth = NthGenerator(step=3, offset=2)
    ... list(nth.generate(10))
    [2, 5, 8]

    `generate` method has `stop` parameter that limits the range of integers generated.
    When having list of 10 sibling elements, the `stop` parameter can be set to 10
    to determine which elements match provided nth-child selector.

    Examples
    --------
    >>> nth = NthGenerator(step=-1, offset=3)
    ... elements = ["a", "b", "c", "d", "e", "f"]
    ... index = [x-1 for x in nth.generate(len(elements))]
    ... [elements[i] for i in index]
    ["d", "e", "f"]

    This selector matches first three children, and can be used the way shown above
    to filter out the elements that match the selector.
    """

    step: int
    offset: int

    def __post_init__(self):
        """
        Checks if passed parameters are valid.

        Raises
        ------
        TypeError
            If step or offset are not integers.
        ValueError
            If offset is negative.
        """
        if not isinstance(self.step, int):
            raise TypeError(
                f"Step parameter must be an integer, not {type(self.step)}."
            )
        if not isinstance(self.offset, int):
            raise TypeError(
                f"Offset parameter must be an integer, not {type(self.offset)}."
            )
        if self.offset < 0:
            raise ValueError("Offset must not be negative.")

    @property
    def _increasing(self) -> bool:
        """
        Returns true if linear function: y = ax + b where a = step and b = offset
        is increasing (step is positive), false otherwise.
        """
        return self.step > 0

    @property
    def _func(self) -> Callable[[int], int]:
        """
        Returns a linear function that represents the nth-child selector.
        y = ax + b where a = step and b = offset, which is used to generate
        the list of integers that match the selector.
        """
        a, b = self.step, self.offset
        return lambda x: a * x + b

    def generate(self, stop: int) -> Generator[int, None, None]:
        """
        Generates a list of integers that match the nth-child selector.

        Parameters
        ----------
        stop : int
            The stop parameter that limits the range of integers generated.
            Must be a positive integer.

        Yields
        ------
        int
            Integers that match the nth-child selector.
            Generated integers fall into the range from 1 to stop.

        Raises
        ------
        TypeError
            If stop parameter is not an integer.

        Examples
        --------
        >>> nth = NthGenerator(step=2, offset=1)
        >>> list(nth.generate(10))
        [1, 3, 5, 7, 9]

        >>> nth = NthGenerator(step=-3, offset=20)
        >>> list(nth.generate(8))
        [8, 5, 2]
        """
        if not isinstance(stop, int):
            raise TypeError(f"Stop parameter must be an integer, not {type(stop)}.")

        if stop < 1:
            return

        a, b = self.step, self.offset

        if a == 0:
            if 1 <= b <= stop:
                yield b
            return

        c = ((1 - b) / a) if self._increasing else ((stop - b) / a)
        start = max(math.ceil(c), 0)

        for x in count(start):  # pragma: no branch
            y = self._func(x)

            if not (1 <= y <= stop):
                break

            yield y


def parse_nth(selector: str) -> NthGenerator:
    """
    Parses CSS nth formula and return `NthGenerator` instance.

    Parameters
    ----------
    selector : str
        CSS nth selector string. Accepts all valid css nth formulas.

    Returns
    -------
    NthGenerator
        `NthGenerator` instance that represents the parsed nth selector
        and can be used for generating matching numbers.

    Raises
    ------
    ValueError
        If the selector is invalid.

    Handles "odd" and "even" literals and any number of whitespace characters
    in the selector string.

    Examples
    --------
    >>> nth = parse_nth("2")
    NthGenerator(step=0, offset=2)

    >>> nth = parse_nth("-3n+2")
    NthGenerator(step=-3, offset=2)

    >>> nth = parse_nth("odd")
    NthGenerator(step=2, offset=1)

    >>> nth = parse_nth("15n")
    NthGenerator(step=15, offset=0)
    """
    # handle whitespaces
    selector = selector.replace(" ", "")

    # handle special cases
    if selector == "odd":
        return NthGenerator(2, 1)
    if selector == "even":
        return NthGenerator(2, 0)

    # handle non-step cases
    if OFFSET_PATTERN.match(selector):
        return NthGenerator(0, int(selector))

    pattern_match = STEP_PATTERN.match(selector) or COMBINED_PATTERN.match(selector)

    if not pattern_match:
        raise ValueError(f"Invalid CSS nth selector: {selector}")

    # replaces n with no preceding digit with 1n - e.g. "n" -> "1n", "-n" -> "-1n"
    selector = re.sub(r"(\D|^)n", r"\g<1>1n", selector)
    # replaces missing offset with 0 - e.g. "2n" -> "2n0"
    selector = re.sub(r"n$", "n0", selector)

    step, offset = map(int, selector.split("n"))
    return NthGenerator(step, offset)
