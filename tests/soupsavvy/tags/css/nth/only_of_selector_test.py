"""Module with unit tests for OnlyOfSelector class."""

import pytest

from soupsavvy.exceptions import NotSoupSelectorException, TagNotFoundException
from soupsavvy.tags.css.nth.nth_soup_selector import OnlyOfSelector
from tests.soupsavvy.tags.conftest import (
    MockClassMenuSelector,
    MockDivSelector,
    find_body_element,
    strip,
    to_bs,
)


@pytest.mark.selector
class TestOnlyOfSelector:
    """Class for OnlyOfSelector unit test suite."""

    def test_raises_exception_when_invalid_input(self):
        """
        Tests if OnlyOfSelector raises NotSoupSelectorException
        when invalid input is provided.
        It requires selector to be SoupSelector instances.
        """
        with pytest.raises(NotSoupSelectorException):
            OnlyOfSelector("selector")  # type: ignore

    def test_find_returns_first_tag_that_matches_selector(self):
        """
        Tests if find method returns the first tag that matches the selector.
        """
        text = """
            <div>
                <span class="menu">1</span>
                <span class="menu">2</span>
                <a>Don't have</a>
            </div>
            <div>
                <span class="menu">3</span>
                <a class="widget">Don't have</a>
            </div>
            <p class="menu">4</p>
            <a>Don't have</a>
        """
        bs = to_bs(text)
        selector = OnlyOfSelector(MockClassMenuSelector())
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<span class="menu">3</span>""")

    def test_find_raises_exception_when_no_match_and_strict_mode(
        self,
    ):
        """
        Tests if find method raises TagNotFoundException when no tag is found
        that matches selector in strict mode.
        """
        text = """
            <div>
                <span class="menu">1</span>
                <span class="menu">2</span>
                <a>Don't have</a>
            </div>
            <div>
                <span class="menu">3</span>
                <a class="menu">4</a>
                <a class="widget">Don't have</a>
            </div>
            <div>
                <a class="widget">Don't have</a>
            </div>
            <a>Don't have</a>
        """
        bs = to_bs(text)
        # nothing would be matches because there is only one matching tag
        selector = OnlyOfSelector(MockClassMenuSelector())

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_returns_none_if_no_tags_matches_selector_in_not_strict_mode(self):
        """
        Tests if find method returns None when no tag is found that matches
        selector in not strict mode.
        """
        text = """
            <div>
                <span class="menu">1</span>
                <span class="menu">2</span>
                <a>Don't have</a>
            </div>
            <div>
                <span class="menu">3</span>
                <a class="menu">4</a>
                <a class="widget">Don't have</a>
            </div>
            <div>
                <a class="widget">Don't have</a>
            </div>
            <a>Don't have</a>
        """
        bs = to_bs(text)

        selector = OnlyOfSelector(MockClassMenuSelector())
        result = selector.find(bs)
        assert result is None

    def test_find_all_returns_all_matching_elements(self):
        """Tests if find_all returns a list of all matching elements."""
        text = """
            <div>
                <span class="menu">1</span>
                <span class="menu">2</span>
                <a>Don't have</a>
            </div>
            <div>
                <span class="menu">3</span>
                <a class="widget">Don't have</a>
            </div>
            <p class="menu">4</p>
            <div>
                <span class="menu">5</span>
                <div>
                    <span class="menu">6</span>
                    <a>Don't have</a>
                </div>
            </div>
            <a>Don't have</a>
        """
        bs = to_bs(text)
        selector = OnlyOfSelector(MockClassMenuSelector())

        result = selector.find_all(bs)
        excepted = [
            strip("""<span class="menu">3</span>"""),
            strip("""<p class="menu">4</p>"""),
            strip("""<span class="menu">5</span>"""),
            strip("""<span class="menu">6</span>"""),
        ]
        assert list(map(lambda x: strip(str(x)), result)) == excepted

    def test_find_all_returns_empty_list_when_no_match(self):
        """Tests if find returns an empty list if no element matches the selector."""
        text = """
            <div>
                <span class="menu">1</span>
                <span class="menu">2</span>
                <a>Don't have</a>
            </div>
            <div>
                <span class="menu">3</span>
                <a class="menu">4</a>
                <a class="widget">Don't have</a>
            </div>
            <div>
                <a class="widget">Don't have</a>
            </div>
            <a>Don't have</a>
        """
        bs = to_bs(text)
        selector = OnlyOfSelector(MockClassMenuSelector())
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """Tests if find returns first matching child element if recursive is False."""
        text = """
            <div>
                <span class="menu">1</span>
                <span class="menu">2</span>
                <a>Don't have</a>
            </div>
            <div>
                <span class="menu">3</span>
                <a class="widget">Don't have</a>
            </div>
            <p class="menu">4</p>
            <div>
                <span class="menu">5</span>
                <div>
                    <span class="menu">6</span>
                    <a>Don't have</a>
                </div>
            </div>
            <a>Don't have</a>
        """
        bs = find_body_element(to_bs(text))
        selector = OnlyOfSelector(MockClassMenuSelector())
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<p class="menu">4</p>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div>
                <span class="menu">1</span>
                <span class="menu">2</span>
                <a>Don't have</a>
            </div>
            <div>
                <span class="menu">3</span>
                <a class="menu">4</a>
                <a class="widget">Don't have</a>
            </div>
            <p class="menu">4</p>
            <div>
                <span class="menu">5</span>
                <div>
                    <span class="menu">6</span>
                    <a>Don't have</a>
                </div>
            </div>
            <p class="menu">7</p>
        """
        bs = find_body_element(to_bs(text))
        selector = OnlyOfSelector(MockClassMenuSelector())
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <div>
                <span class="menu">1</span>
                <span class="menu">2</span>
                <a>Don't have</a>
            </div>
            <div>
                <span class="menu">3</span>
                <a class="widget">Don't have</a>
            </div>
            <p class="menu">4</p>
            <div>
                <span class="menu">5</span>
                <div>
                    <span class="menu">6</span>
                    <a>Don't have</a>
                </div>
            </div>
            <p class="menu">7</p>
        """
        bs = find_body_element(to_bs(text))
        selector = OnlyOfSelector(MockClassMenuSelector())

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <div>
                <span class="menu">1</span>
                <span class="menu">2</span>
                <a>Don't have</a>
            </div>
            <div>
                <span class="menu">3</span>
                <a class="widget">Don't have</a>
            </div>
            <p class="menu">4</p>
            <div>
                <span class="menu">5</span>
                <div>
                    <span class="menu">6</span>
                    <a>Don't have</a>
                </div>
            </div>
        """
        bs = find_body_element(to_bs(text))
        selector = OnlyOfSelector(MockClassMenuSelector())
        results = selector.find_all(bs, recursive=False)

        # only possible result is list with one element
        assert list(map(lambda x: strip(str(x)), results)) == [
            strip("""<p class="menu">4</p>""")
        ]

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self,
    ):
        """
        Tests if find_all returns an empty list if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div>
                <span class="menu">1</span>
                <span class="menu">2</span>
                <a>Don't have</a>
            </div>
            <div>
                <span class="menu">3</span>
                <a class="widget">Don't have</a>
            </div>
            <p class="menu">4</p>
            <div>
                <span class="menu">5</span>
                <div>
                    <span class="menu">6</span>
                    <a>Don't have</a>
                </div>
            </div>
            <p class="menu">7</p>
        """
        bs = find_body_element(to_bs(text))
        selector = OnlyOfSelector(MockClassMenuSelector())

        results = selector.find_all(bs, recursive=False)
        assert results == []

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <div>
                <span class="menu">1</span>
                <span class="menu">2</span>
                <a>Don't have</a>
            </div>
            <div>
                <span class="menu">3</span>
                <a class="widget">Don't have</a>
            </div>
            <p class="menu">4</p>
            <div>
                <span class="menu">5</span>
                <div>
                    <span class="menu">6</span>
                    <a>Don't have</a>
                </div>
            </div>
        """
        bs = to_bs(text)
        selector = OnlyOfSelector(MockClassMenuSelector())
        results = selector.find_all(bs, limit=2)

        # children goes first
        assert list(map(lambda x: strip(str(x)), results)) == [
            strip("""<span class="menu">3</span>"""),
            strip("""<p class="menu">4</p>"""),
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
            <div>
                <span class="menu">1</span>
                <span class="menu">2</span>
                <a>Don't have</a>
            </div>
            <div>
                <span class="menu">3</span>
                <a class="widget">Don't have</a>
            </div>
            <p class="menu">4</p>
            <div>
                <span class="menu">5</span>
                <div>
                    <span class="menu">6</span>
                    <a>Don't have</a>
                </div>
            </div>
        """

        bs = find_body_element(to_bs(text))
        selector = OnlyOfSelector(MockClassMenuSelector())
        results = selector.find_all(bs, recursive=False, limit=2)

        # only possible result is list with one element
        assert list(map(lambda x: strip(str(x)), results)) == [
            strip("""<p class="menu">4</p>"""),
        ]

    def test_selector_is_equal(self):
        """
        Tests if two selectors are equal. Selector is equal only if it's an instance
        of the same class and has the same nth selector.
        """
        assert (
            OnlyOfSelector(MockClassMenuSelector())
            == OnlyOfSelector(MockClassMenuSelector())
        ) is True

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            (
                OnlyOfSelector(MockClassMenuSelector()),
                OnlyOfSelector(MockDivSelector()),
            ),
            (OnlyOfSelector(MockClassMenuSelector()), MockDivSelector()),
        ],
    )
    def test_selector_is_not_equal(self, selectors: tuple):
        """Tests if two selectors are not equal."""
        assert (selectors[0] == selectors[1]) is False
