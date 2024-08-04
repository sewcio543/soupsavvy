"""Module with unit tests for NthOfSelector class."""

import pytest

from soupsavvy.exceptions import NotSoupSelectorException, TagNotFoundException
from soupsavvy.selectors.nth.nth_soup_selector import NthOfSelector
from tests.soupsavvy.selectors.conftest import (
    MockClassMenuSelector,
    MockDivSelector,
    find_body_element,
    strip,
    to_bs,
)


@pytest.mark.selector
class TestNthOfSelector:
    """Class for NthOfSelector unit test suite."""

    def test_raises_exception_when_invalid_input(self):
        """
        Tests if NthOfSelector raises NotSoupSelectorException
        when invalid input is provided.
        It requires selector to be SoupSelector instances.
        """
        with pytest.raises(NotSoupSelectorException):
            NthOfSelector("selector", "2n")  # type: ignore

    def test_find_returns_first_tag_that_has_element_matching_single_selector(self):
        """
        Tests if find method returns the first tag that matches
        both the soup selector and the nth selector.
        """
        text = """
            <a>Don't have</a>
            <p class="menu">1</p>
            <div>
                <span class="menu">Not child</span>
            </div>
            <div class="menu"><a>2</a></div>
            <a>Don't have</a>
            <a class="menu">3</a>
            <p class="menu">4</p>
            <div class="menu">5</div>
        """
        bs = to_bs(text)
        selector = NthOfSelector(MockClassMenuSelector(), "2n")
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<div class="menu"><a>2</a></div>""")

    def test_find_raises_exception_when_no_match_nth_selector(
        self,
    ):
        """
        Tests if find method raises TagNotFoundException when no tag is found
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
        bs = to_bs(text)
        # nothing would be matches because there is only one matching tag
        selector = NthOfSelector(MockClassMenuSelector(), "2n")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_raises_exception_when_no_match_soup_selector(
        self,
    ):
        """
        Tests if find method raises TagNotFoundException when no tag is found
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
        bs = to_bs(text)
        selector = NthOfSelector(MockClassMenuSelector(), "1")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_returns_none_if_no_tags_matches_nth_selector_in_not_strict_mode(self):
        """
        Tests if find method returns None when no tag is found that matches
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
        bs = to_bs(text)

        selector = NthOfSelector(MockClassMenuSelector(), "3n")
        result = selector.find(bs)
        assert result is None

    def test_find_returns_none_if_no_tags_matches_soup_selector_in_not_strict_mode(
        self,
    ):
        """
        Tests if find method returns None when no tag is found that matches
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
        bs = to_bs(text)
        selector = NthOfSelector(MockClassMenuSelector(), "1")

        result = selector.find(bs)
        assert result is None

    def test_find_all_returns_all_matching_elements(self):
        """Tests if find_all returns a list of all matching elements."""
        text = """
            <a>Don't have</a>
            <p class="menu">1</p>
            <div>
                <span class="menu">3</span>
                <a>Don't have</a>
                <p class="menu">4</p>
                <p class="menu"></p>
            </div>
            <div class="menu"><a>2</a></div>
            <a>Don't have</a>
            <a class="widget"></a>
            <p class="menu"></p>
            <a>Don't have</a>
            <p class="menu"></p>
        """
        bs = to_bs(text)
        selector = NthOfSelector(MockClassMenuSelector(), "-n+2")

        result = selector.find_all(bs)
        excepted = [
            strip("""<p class="menu">1</p>"""),
            strip("""<span class="menu">3</span>"""),
            strip("""<p class="menu">4</p>"""),
            strip("""<div class="menu"><a>2</a></div>"""),
        ]
        assert list(map(lambda x: strip(str(x)), result)) == excepted

    def test_find_all_returns_empty_list_when_no_match(self):
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
        bs = to_bs(text)
        selector = NthOfSelector(MockClassMenuSelector(), "1")
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(self):
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
        bs = find_body_element(to_bs(text))
        selector = NthOfSelector(MockClassMenuSelector(), "2")
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<div class="menu">2</div>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
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
        bs = find_body_element(to_bs(text))
        selector = NthOfSelector(MockClassMenuSelector(), "2")
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
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
        bs = find_body_element(to_bs(text))
        selector = NthOfSelector(MockClassMenuSelector(), "2")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <div class="widget"></div>
            <div class="menu">1</div>
            <div>
                <div class="menu">Not a child</div>
                <p class="menu">Not a child</p>
                <div>Hi Hi Hello</div>
                <p class="menu">Not a child</p>
                <div class="menu">Not a child</div>
            </div>
            <div class="menu">2</div>
            <p class="menu">3</p>
            <p class="menu">4</p>
            <div>Hi Hi Hello</div>
            <p class="menu">5</p>
            <span id="menu">Hello</span>
        """
        bs = find_body_element(to_bs(text))
        selector = NthOfSelector(MockClassMenuSelector(), "2n")
        results = selector.find_all(bs, recursive=False)

        assert list(map(lambda x: strip(str(x)), results)) == [
            strip("""<div class="menu">2</div>"""),
            strip("""<p class="menu">4</p>"""),
        ]

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self,
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
        bs = find_body_element(to_bs(text))
        selector = NthOfSelector(MockClassMenuSelector(), "2")

        results = selector.find_all(bs, recursive=False)
        assert results == []

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 3 first in order elements are returned.
        """
        text = """
            <div class="widget"></div>
            <div class="menu">1</div>
            <div>
                <div class="menu">1 desc</div>
                <p class="menu">2 desc</p>
                <div>Hi Hi Hello</div>
                <p class="menu">3 desc</p>
                <div class="menu">4 desc</div>
            </div>
            <div class="menu">2</div>
            <p class="menu">3</p>
            <p class="menu">4</p>
            <div>Hi Hi Hello</div>
            <p class="menu">5</p>
            <span id="menu">Hello</span>
        """
        bs = to_bs(text)
        selector = NthOfSelector(MockClassMenuSelector(), "2n")
        results = selector.find_all(bs, limit=3)

        # children goes first
        assert list(map(lambda x: strip(str(x)), results)) == [
            strip("""<p class="menu">2 desc</p>"""),
            strip("""<div class="menu">4 desc</div>"""),
            strip("""<div class="menu">2</div>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set_and_recursive_false(
        self,
    ):
        """
        Tests if find_all returns only x elements when limit is set and recursive
        is False. In this case only 2 first in order children matching
        the selector are returned.
        """
        text = """
            <div class="widget"></div>
            <div class="menu">1</div>
            <div>
                <div class="menu">1 desc</div>
                <p class="menu">2 desc</p>
                <div>Hi Hi Hello</div>
                <p class="menu">3 desc</p>
                <div class="menu">4 desc</div>
            </div>
            <div class="menu">2</div>
            <p class="menu">3</p>
            <p class="menu">4</p>
            <div>Hi Hi Hello</div>
            <p class="menu">5</p>
            <span id="menu">Hello</span>
        """

        bs = find_body_element(to_bs(text))
        selector = NthOfSelector(MockClassMenuSelector(), "2n+1")
        results = selector.find_all(bs, recursive=False, limit=2)

        assert list(map(lambda x: strip(str(x)), results)) == [
            strip("""<div class="menu">1</div>"""),
            strip("""<p class="menu">3</p>"""),
        ]

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            (
                NthOfSelector(MockClassMenuSelector(), "2n+1"),
                NthOfSelector(MockClassMenuSelector(), " 2n + 1 "),
            ),
            (
                NthOfSelector(MockClassMenuSelector(), "-2n+3"),
                NthOfSelector(MockClassMenuSelector(), "-2n+3"),
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
                NthOfSelector(MockClassMenuSelector(), "2n"),
                NthOfSelector(MockClassMenuSelector(), "2n+1"),
            ),
            (
                NthOfSelector(MockClassMenuSelector(), "2n"),
                NthOfSelector(MockDivSelector(), "2n"),
            ),
            (
                NthOfSelector(MockClassMenuSelector(), "2n"),
                NthOfSelector(MockDivSelector(), "2n+1"),
            ),
            (NthOfSelector(MockClassMenuSelector(), "2n"), MockClassMenuSelector()),
            (NthOfSelector(MockClassMenuSelector(), "2n"), "string"),
        ],
    )
    def test_selector_is_not_equal(self, selectors: tuple):
        """Tests if two selectors are not equal."""
        assert (selectors[0] == selectors[1]) is False

    @pytest.mark.parametrize(
        argnames="nth, expected",
        argvalues=[
            ("2n", [2, 4, 6]),
            ("2n+1", [1, 3, 5]),
            ("-n+3", [1, 2, 3]),
            ("even", [2, 4, 6]),
            ("odd", [1, 3, 5]),
            ("3", [3]),
            ("-3n", []),
            ("-3n+10", [1, 4]),
        ],
    )
    def test_returns_elements_based_on_nth_selector(
        self, nth: str, expected: list[int]
    ):
        """Tests if find_all returns all elements matching various nth selectors."""
        text = """
            <div class="widget"></div>
            <div class="menu">1</div>
            <div class="menu">2</div>
            <div class="widget"></div>
            <div class="menu">3</div>
            <div class="menu">4</div>
            <div class="widget"></div>
            <div class="menu">5</div>
            <div class="menu">6</div>
            <div class="widget"></div>
        """

        bs = find_body_element(to_bs(text))
        selector = NthOfSelector(MockClassMenuSelector(), nth)
        results = selector.find_all(bs)

        assert list(map(lambda x: strip(str(x)), results)) == [
            f"""<div class="menu">{i}</div>""" for i in expected
        ]
