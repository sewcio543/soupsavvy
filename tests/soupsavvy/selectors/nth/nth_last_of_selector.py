"""Module with unit tests for NthLastOfSelector class."""

import pytest

from soupsavvy.exceptions import NotSoupSelectorException, TagNotFoundException
from soupsavvy.selectors.nth.selectors import NthLastOfSelector
from tests.soupsavvy.conftest import (
    MockClassMenuSelector,
    MockDivSelector,
    ToElement,
    strip,
)


@pytest.mark.selector
class TestNthLastOfSelector:
    """Class for NthLastOfSelector unit test suite."""

    def test_raises_exception_when_invalid_input(self):
        """
        Tests if NthLastOfSelector raises NotSoupSelectorException
        when invalid input is provided.
        It requires selector to be SoupSelector instances.
        """
        with pytest.raises(NotSoupSelectorException):
            NthLastOfSelector("selector", "2n")  # type: ignore

    def test_find_returns_first_tag_that_has_element_matching_single_selector(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find method returns the first element, that matches
        both the soup selector and the nth selector.
        """
        text = """
            <a>Don't have</a>
            <p class="menu">5</p>
            <div>
                <span class="menu">Not child</span>
            </div>
            <div class="menu"><a>4</a></div>
            <a>Don't have</a>
            <a class="menu">3</a>
            <p class="menu">2</p>
            <div class="menu">1</div>
        """
        bs = to_element(text)
        selector = NthLastOfSelector(MockClassMenuSelector(), "2n")
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<div class="menu"><a>4</a></div>""")

    def test_find_raises_exception_when_no_match_nth_selector(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find method raises TagNotFoundException when no element is found
        that matches both the soup selector and the nth selector in strict mode.
        In this case tags that match soup selector are found, but none of them
        match the nth selector.
        """
        text = """
            <a>Don't have</a>
            <p class="menu">1</p>
            <div>
                <span id="menu">Not child</span>
            </div>
            <div class="menu2"><a>2</a></div>
            <a>Don't have</a>
        """
        bs = to_element(text)
        # nothing would be matches because there is only one matching element
        selector = NthLastOfSelector(MockClassMenuSelector(), "2n")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_raises_exception_when_no_match_soup_selector(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find method raises TagNotFoundException when no element is found
        that matches both the soup selector and the nth selector in strict mode.
        In this case no tags that match soup selector are found.
        """
        text = """
            <a>Don't have</a>
            <p class="widget">1</p>
            <div>
                <span id="menu">Not child</span>
            </div>
            <div class="menu2"><a>2</a></div>
            <a>Don't have</a>
        """
        bs = to_element(text)
        selector = NthLastOfSelector(MockClassMenuSelector(), "1")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_returns_none_if_no_elements_matches_nth_selector_in_not_strict_mode(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find method returns None when no element is found that matches
        both the soup selector and the nth selector in not strict mode.
        In this case tags are found that match the soup selector, but
        there are no tags that match the nth selector.
        """
        text = """
            <a>Don't have</a>
            <p class="menu">1</p>
            <div>
                <span id="menu">Not child</span>
            </div>
            <div class="menu"><a>2</a></div>
            <a>Don't have</a>
        """
        bs = to_element(text)

        selector = NthLastOfSelector(MockClassMenuSelector(), "3n")
        result = selector.find(bs)
        assert result is None

    def test_find_returns_none_if_no_elements_matches_soup_selector_in_not_strict_mode(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find method returns None when no element is found that matches
        both the soup selector and the nth selector in not strict mode.
        In this case no tags are found that match the soup selector.
        """
        text = """
            <a>Don't have</a>
            <p class="widget">1</p>
            <div>
                <span id="menu">Not child</span>
            </div>
            <div class="menu2"><a>2</a></div>
            <a>Don't have</a>
        """
        bs = to_element(text)
        selector = NthLastOfSelector(MockClassMenuSelector(), "1")

        result = selector.find(bs)
        assert result is None

    def test_find_all_returns_all_matching_elements(self, to_element: ToElement):
        """Tests if find_all returns a list of all matching elements."""
        text = """
            <a>Don't have</a>
            <p class="menu">4</p>
            <div>
                <span class="menu">3 desc</span>
                <a>Don't have</a>
                <p class="menu">2 desc</p>
                <p class="menu">1 desc</p>
            </div>
            <div class="menu"><a>3</a></div>
            <a>Don't have</a>
            <a class="widget"></a>
            <p class="menu">2</p>
            <a>Don't have</a>
            <p class="menu">1</p>
        """
        bs = to_element(text)
        selector = NthLastOfSelector(MockClassMenuSelector(), "-n+2")

        result = selector.find_all(bs)
        excepted = [
            strip("""<p class="menu">2 desc</p>"""),
            strip("""<p class="menu">1 desc</p>"""),
            strip("""<p class="menu">2</p>"""),
            strip("""<p class="menu">1</p>"""),
        ]
        assert list(map(lambda x: strip(str(x)), result)) == excepted

    def test_find_all_returns_empty_list_when_no_match(self, to_element: ToElement):
        """Tests if find returns an empty list if no element matches the selector."""
        text = """
            <a>Don't have</a>
            <p class="widget">1</p>
            <div>
                <span id="menu">Not child</span>
            </div>
            <div class="menu2"><a>2</a></div>
            <a>Don't have</a>
        """
        bs = to_element(text)
        selector = NthLastOfSelector(MockClassMenuSelector(), "1")
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(
        self,
        to_element: ToElement,
    ):
        """Tests if find returns first matching child element if recursive is False."""
        text = """
            <div class="widget"></div>
            <div class="menu">1</div>
            <div>
                <div class="menu">Not a child</div>
                <p class="menu">Not a child</p>
            </div>
            <div class="menu">2</div>
            <div>Hi Hi Hello</div>
            <span>Hello</span>
        """
        bs = to_element(text)
        selector = NthLastOfSelector(MockClassMenuSelector(), "2")
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<div class="menu">1</div>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div class="widget"></div>
            <div class="menu">1</div>
            <div>
                <div class="menu">Not a child</div>
                <p class="menu">Not a child</p>
            </div>
            <div>Hi Hi Hello</div>
            <span>Hello</span>
        """
        bs = to_element(text)
        selector = NthLastOfSelector(MockClassMenuSelector(), "2")
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <div class="widget"></div>
            <div class="menu">1</div>
            <div>
                <div class="menu">Not a child</div>
                <p class="menu">Not a child</p>
            </div>
            <div>Hi Hi Hello</div>
            <span>Hello</span>
        """
        bs = to_element(text)
        selector = NthLastOfSelector(MockClassMenuSelector(), "2")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_all_returns_all_matching_children_when_recursive_false(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <div class="widget"></div>
            <div class="menu">5</div>
            <div>
                <div class="menu">Not a child</div>
                <p class="menu">Not a child</p>
                <div>Hi Hi Hello</div>
                <p class="menu">Not a child</p>
                <div class="menu">Not a child</div>
            </div>
            <div class="menu">4</div>
            <p class="menu">3</p>
            <p class="menu">2</p>
            <div>Hi Hi Hello</div>
            <p class="menu">1</p>
            <span id="menu">Hello</span>
        """
        bs = to_element(text)
        selector = NthLastOfSelector(MockClassMenuSelector(), "2n")
        results = selector.find_all(bs, recursive=False)

        assert list(map(lambda x: strip(str(x)), results)) == [
            strip("""<div class="menu">4</div>"""),
            strip("""<p class="menu">2</p>"""),
        ]

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find_all returns an empty list if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div class="widget"></div>
            <div class="menu">1</div>
            <div>
                <div class="menu">Not a child</div>
                <p class="menu">Not a child</p>
            </div>
            <div>Hi Hi Hello</div>
            <span>Hello</span>
        """
        bs = to_element(text)
        selector = NthLastOfSelector(MockClassMenuSelector(), "2")

        results = selector.find_all(bs, recursive=False)
        assert results == []

    def test_find_all_returns_only_x_elements_when_limit_is_set(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 3 first in order elements are returned.
        """
        text = """
            <div class="widget"></div>
            <div class="menu">5</div>
            <div>
                <div class="menu">4 desc</div>
                <p class="menu">3 desc</p>
                <div>Hi Hi Hello</div>
                <p class="menu">2 desc</p>
                <div class="menu">1 desc</div>
            </div>
            <div class="menu">4</div>
            <p class="menu">3</p>
            <p class="menu">2</p>
            <div>Hi Hi Hello</div>
            <p class="menu">1</p>
            <span id="menu">Hello</span>
        """
        bs = to_element(text)
        selector = NthLastOfSelector(MockClassMenuSelector(), "2n")
        results = selector.find_all(bs, limit=3)

        # children goes first
        assert list(map(lambda x: strip(str(x)), results)) == [
            strip("""<div class="menu">4 desc</div>"""),
            strip("""<p class="menu">2 desc</p>"""),
            strip("""<div class="menu">4</div>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set_and_recursive_false(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find_all returns only x elements when limit is set and recursive
        is False. In this case only 2 first in order children matching
        the selector are returned.
        """
        text = """
            <div class="widget"></div>
            <div class="menu">5</div>
            <div>
                <div class="menu">4 desc</div>
                <p class="menu">3 desc</p>
                <div>Hi Hi Hello</div>
                <p class="menu">2 desc</p>
                <div class="menu">1 desc</div>
            </div>
            <div class="menu">4</div>
            <p class="menu">3</p>
            <p class="menu">2</p>
            <div>Hi Hi Hello</div>
            <p class="menu">1</p>
            <span id="menu">Hello</span>
        """

        bs = to_element(text)
        selector = NthLastOfSelector(MockClassMenuSelector(), "2n+1")
        results = selector.find_all(bs, recursive=False, limit=2)

        assert list(map(lambda x: strip(str(x)), results)) == [
            strip("""<div class="menu">5</div>"""),
            strip("""<p class="menu">3</p>"""),
        ]

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            (
                NthLastOfSelector(MockClassMenuSelector(), "2n+1"),
                NthLastOfSelector(MockClassMenuSelector(), " 2n + 1 "),
            ),
            (
                NthLastOfSelector(MockClassMenuSelector(), "-2n+3"),
                NthLastOfSelector(MockClassMenuSelector(), "-2n+3"),
            ),
        ],
    )
    def test_selector_is_equal(self, selectors: tuple):
        """
        Tests if two selectors are equal. Selector is equal only if it's an instance
        of the same class and has the same nth selector.
        """
        assert (selectors[0] == selectors[1]) is True

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            (
                NthLastOfSelector(MockClassMenuSelector(), "2n"),
                NthLastOfSelector(MockClassMenuSelector(), "2n+1"),
            ),
            (
                NthLastOfSelector(MockClassMenuSelector(), "2n"),
                NthLastOfSelector(MockDivSelector(), "2n"),
            ),
            (
                NthLastOfSelector(MockClassMenuSelector(), "2n"),
                NthLastOfSelector(MockDivSelector(), "2n+1"),
            ),
            (NthLastOfSelector(MockClassMenuSelector(), "2n"), MockClassMenuSelector()),
            (NthLastOfSelector(MockClassMenuSelector(), "2n"), "string"),
        ],
    )
    def test_selector_is_not_equal(self, selectors: tuple):
        """Tests if two selectors are not equal."""
        assert (selectors[0] == selectors[1]) is False

    @pytest.mark.parametrize(
        argnames="nth, expected",
        argvalues=[
            ("2n", [6, 4, 2]),
            ("2n+1", [5, 3, 1]),
            ("-n+3", [3, 2, 1]),
            ("even", [6, 4, 2]),
            ("odd", [5, 3, 1]),
            ("3", [3]),
            ("-3n", []),
            ("-3n+10", [4, 1]),
        ],
    )
    def test_returns_elements_based_on_nth_selector(
        self, to_element: ToElement, nth: str, expected: list[int]
    ):
        """Tests if find_all returns all elements matching various nth selectors."""
        text = """
            <div class="widget"></div>
            <div class="menu">6</div>
            <div class="menu">5</div>
            <div class="widget"></div>
            <div class="menu">4</div>
            <div class="menu">3</div>
            <div class="widget"></div>
            <div class="menu">2</div>
            <div class="menu">1</div>
            <div class="widget"></div>
        """

        bs = to_element(text)
        selector = NthLastOfSelector(MockClassMenuSelector(), nth)
        results = selector.find_all(bs)

        assert list(map(lambda x: strip(str(x)), results)) == [
            f"""<div class="menu">{i}</div>""" for i in expected
        ]
