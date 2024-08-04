"""Module for testing the NthGenerator class."""

from typing import Generator

import pytest

from soupsavvy.selectors.nth.nth_utils import NthGenerator, parse_nth

STOP = 10


class TestNthGenerator:
    """Class with unit test suite for NthGenerator class."""

    @pytest.mark.parametrize(
        argnames="selector, expected",
        argvalues=[
            # when step is positive
            (NthGenerator(step=2, offset=1), [1, 3, 5, 7, 9]),
            (NthGenerator(step=3, offset=2), [2, 5, 8]),
            (NthGenerator(step=2, offset=0), [2, 4, 6, 8, 10]),
            (NthGenerator(step=2, offset=11), []),
            (NthGenerator(step=10, offset=10), [10]),
            (NthGenerator(step=11, offset=0), []),
            # when step is negative
            (NthGenerator(step=-2, offset=7), [7, 5, 3, 1]),
            (NthGenerator(step=-3, offset=10), [10, 7, 4, 1]),
            (NthGenerator(step=-1, offset=4), [4, 3, 2, 1]),
            (NthGenerator(step=-2, offset=100), [10, 8, 6, 4, 2]),
            (NthGenerator(step=-20, offset=7), [7]),
            (NthGenerator(step=-1, offset=0), []),
            # when step is 0
            (NthGenerator(step=0, offset=5), [5]),
            (NthGenerator(step=0, offset=11), []),
            (NthGenerator(step=0, offset=0), []),
        ],
    )
    def test_generates_expected_list_of_integers(
        self, selector: NthGenerator, expected: list[int]
    ):
        """Tests if generate method returns expected list of integers."""
        result = list(selector.generate(STOP))
        assert result == expected

    def test_generate_returns_generator(self):
        """Tests if generate method returns a generator."""
        nth = NthGenerator(step=2, offset=1)
        gen = nth.generate(STOP)
        assert isinstance(gen, Generator)

    @pytest.mark.parametrize(argnames="stop", argvalues=[5.5, "five"])
    def test_raises_exception_when_input_parameter_is_not_int(self, stop):
        """
        Tests if generate method raises TypeError
        when input parameters are not integers.
        """
        nth = NthGenerator(step=2, offset=1)

        with pytest.raises(TypeError):
            list(nth.generate(stop))

    def test_returns_empty_list_if_stop_is_less_then_one(self):
        """
        Tests if generate method returns empty list when step is less than 1.
        Only positive integers are generated.
        """
        nth = NthGenerator(step=2, offset=1)

        assert list(nth.generate(0)) == []
        assert list(nth.generate(-10)) == []

    def test_raises_exception_when_parameters_are_not_int(self):
        """
        Tests if NthGenerator class init raises TypeError
        when parameters are not integers. Both step and offset must be integers
        for component to work properly and make sense.
        """
        with pytest.raises(TypeError):
            NthGenerator(step=3.2, offset=1)  # type: ignore

        with pytest.raises(TypeError):
            NthGenerator(step=3, offset=1.4)  # type: ignore

    def test_raises_exception_when_offset_is_negative(self):
        """
        Tests if NthGenerator class init raises ValueError when offset is negative.
        Negative offset is not allowed in css nth selectors and does not
        make sense in this context.
        """
        with pytest.raises(ValueError):
            NthGenerator(step=3, offset=-1)


class TestParseNth:
    """Class with unit test suite for parse_nth function."""

    @pytest.mark.parametrize(
        argnames="nth, expected",
        argvalues=[
            ("0", (0, 0)),
            ("2", (0, 2)),
            ("420", (0, 420)),
            ("n", (1, 0)),
            ("140n", (140, 0)),
            ("-n", (-1, 0)),
            ("-20n", (-20, 0)),
            ("2n+1", (2, 1)),
            ("n+11", (1, 11)),
            ("-38n+21", (-38, 21)),
            ("odd", (2, 1)),
            ("even", (2, 0)),
            ("3n+0", (3, 0)),
            ("0n+0", (0, 0)),
            ("-0n+10", (0, 10)),
        ],
    )
    def test_parses_nth_selector_into_proper_nth_generator(
        self, nth: str, expected: tuple[int, int]
    ):
        """Tests if parse_nth function returns proper NthGenerator instance."""
        result = parse_nth(nth)
        assert isinstance(result, NthGenerator)
        a, b = result.step, result.offset
        assert (a, b) == expected

    @pytest.mark.parametrize(
        argnames="nth",
        argvalues=[
            "-10",
            "2n-1",
            "2n+1.5",
            "string",
            "1.0n+1",
        ],
    )
    def test_raises_exception_when_input_not_valid_selector(self, nth):
        """
        Tests if parse_nth function raises ValueError when input is not valid selector.
        """
        with pytest.raises(ValueError):
            parse_nth(nth)

    def test_handles_whitespace_in_input_string(self):
        """
        Tests if parse_nth function handles whitespace in input string.
        Whitespaces should be removed from the input string.
        """
        result = parse_nth("  2n   + 1  ")
        assert isinstance(result, NthGenerator)
        a, b = result.step, result.offset
        assert (a, b) == (2, 1)
