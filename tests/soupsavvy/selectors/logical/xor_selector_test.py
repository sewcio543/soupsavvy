"""Testing module for XORSelector class."""

import pytest

from soupsavvy.exceptions import NotSoupSelectorException, TagNotFoundException
from soupsavvy.selectors.logical import XORSelector
from tests.soupsavvy.conftest import (
    MockClassMenuSelector,
    MockClassWidgetSelector,
    MockDivSelector,
    MockLinkSelector,
    find_body_element,
    strip,
    to_element,
)


@pytest.mark.selector
class TestXORSelector:
    """Class for XORSelector unit test suite."""

    def test_raises_exception_when_no_invalid_input(self):
        """
        Tests if init raises NotSoupSelectorException when invalid input is provided.
        All of the parameters must be SoupSelector instances.
        """
        with pytest.raises(NotSoupSelectorException):
            XORSelector("div", MockDivSelector())  # type: ignore

        with pytest.raises(NotSoupSelectorException):
            XORSelector(MockClassMenuSelector(), MockLinkSelector(), "div")  # type: ignore

    def test_find_returns_first_tag_matching_selector(self):
        """
        Tests if find method returns the first tag that matches all the selectors.
        """
        text = """
            <a class="menu"></a>
            <div class="widget"></div>
            <a class="link">1</a>
            <span>Hello</span>
            <div class="menu">2</div>
            <a class="widget">3</a>
        """
        bs = to_element(text)
        selector = XORSelector(MockLinkSelector(), MockClassMenuSelector())
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<a class="link">1</a>""")

    def test_find_raises_exception_when_no_tags_match_in_strict_mode(self):
        """
        Tests if find method raises TagNotFoundException when no tag is found
        that matches all the selectors in strict mode.
        """
        text = """
            <a class="menu"></a>
            <div class="widget"></div>
            <a class="menu widget"></a>
            <span>Hello</span>
        """
        bs = to_element(text)
        selector = XORSelector(MockLinkSelector(), MockClassMenuSelector())

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_returns_none_if_no_tags_match_in_not_strict_mode(self):
        """
        Tests if find method returns None when no tag is found that
        matches all the selectors in not strict mode.
        """
        text = """
            <a class="menu"></a>
            <div class="widget"></div>
            <a class="menu widget"></a>
            <span>Hello</span>
        """
        bs = to_element(text)
        selector = XORSelector(MockLinkSelector(), MockClassMenuSelector())
        result = selector.find(bs)
        assert result is None

    def test_find_returns_match_with_multiple_selectors(self):
        """
        Tests if find method returns the first tag that matches selector
        if there are multiple selectors are provided.
        """
        text = """
            <a class="menu widget"></a>
            <a class="menu">1</a>
            <div class="widget"></div>
            <div><a>2</a></div>
            <div class="menu"></div>
            <span class="widget">3</span>
            <span>Hello</span>
            <div class="menu widget"></div>
            <a class="widget link">4</a>
        """
        bs = to_element(text)

        selector = XORSelector(
            MockDivSelector(),
            MockClassMenuSelector(),
            MockClassWidgetSelector(),
        )
        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="menu">1</a>"""),
            strip("""<div><a>2</a></div>"""),
            strip("""<span class="widget">3</span>"""),
            strip("""<a class="widget link">4</a>"""),
        ]

    def test_finds_all_tags_matching_selectors(self):
        """
        Tests if find_all method returns all tags that match all the selectors.
        """
        text = """
            <a class="menu"></a>
            <div class="widget"></div>
            <a class="link">1</a>
            <span>Hello</span>
            <div class="menu"><span>2</span></div>
            <div>
                <a class="menu link"></a>
                <a>3</a>
            </div>
        """
        bs = to_element(text)
        selector = XORSelector(MockLinkSelector(), MockClassMenuSelector())
        result = selector.find_all(bs)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="link">1</a>"""),
            strip("""<div class="menu"><span>2</span></div>"""),
            strip("""<a>3</a>"""),
        ]

    def test_find_all_returns_empty_list_if_no_tag_matches(self):
        """
        Tests if find_all method returns an empty list when no tag is found
        that matches all the selectors.
        """
        text = """
            <a class="menu"></a>
            <div class="widget"></div>
            <a class="menu widget"></a>
            <span>Hello</span>
        """
        bs = to_element(text)
        selector = XORSelector(MockLinkSelector(), MockClassMenuSelector())
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <a class="menu"></a>
            <div>
                <a class="menu link"></a>
                <a>Not child</a>
            </div>
            <div class="widget"></div>
            <a class="link">1</a>
            <span>Hello</span>
            <div class="menu"><span>2</span></div>
            <div><p class="menu">Not child</p></div>
            <span class="menu">3</span>
        """
        bs = find_body_element(to_element(text))
        selector = XORSelector(MockLinkSelector(), MockClassMenuSelector())
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<a class="link">1</a>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <a class="menu"></a>
            <div>
                <a class="menu link"></a>
                <a>Not child</a>
            </div>
            <div class="widget"></div>
            <span>Hello</span>
            <div><p class="menu">Not child</p></div>
        """
        bs = find_body_element(to_element(text))
        selector = XORSelector(MockLinkSelector(), MockClassMenuSelector())
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <a class="menu"></a>
            <div>
                <a class="menu link"></a>
                <a>Not child</a>
            </div>
            <div class="widget"></div>
            <span>Hello</span>
            <div><p class="menu">Not child</p></div>
        """
        bs = find_body_element(to_element(text))
        selector = XORSelector(MockLinkSelector(), MockClassMenuSelector())

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <a class="menu"></a>
            <div>
                <a class="menu link"></a>
                <a>Not child</a>
            </div>
            <div class="widget"></div>
            <a class="link">1</a>
            <span>Hello</span>
            <div class="menu"><span>2</span></div>
            <div><p class="menu">Not child</p></div>
            <span class="menu">3</span>
        """
        bs = find_body_element(to_element(text))
        selector = XORSelector(MockLinkSelector(), MockClassMenuSelector())
        result = selector.find_all(bs, recursive=False)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="link">1</a>"""),
            strip("""<div class="menu"><span>2</span></div>"""),
            strip("""<span class="menu">3</span>"""),
        ]

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self,
    ):
        """
        Tests if find_all returns an empty list if no child element matches the selector
        and recursive is False.
        """
        text = """
            <a class="menu"></a>
            <div>
                <a class="menu link"></a>
                <a>Not child</a>
            </div>
            <div class="widget"></div>
            <span>Hello</span>
            <div><p class="menu">Not child</p></div>
        """
        bs = find_body_element(to_element(text))
        selector = XORSelector(MockLinkSelector(), MockClassMenuSelector())
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <a class="menu"></a>
            <div class="widget"></div>
            <a class="link">1</a>
            <span>Hello</span>
            <div class="menu"><span>2</span></div>
            <a>3</a>
        """
        bs = find_body_element(to_element(text))
        selector = XORSelector(MockLinkSelector(), MockClassMenuSelector())
        result = selector.find_all(bs, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="link">1</a>"""),
            strip("""<div class="menu"><span>2</span></div>"""),
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
            <a class="menu"></a>
            <div>
                <a class="menu link"></a>
                <a>Not child</a>
            </div>
            <div class="widget"></div>
            <a class="link">1</a>
            <span>Hello</span>
            <div class="menu"><span>2</span></div>
            <div><p class="menu">Not child</p></div>
            <span class="menu">3</span>
        """
        bs = find_body_element(to_element(text))
        selector = XORSelector(MockLinkSelector(), MockClassMenuSelector())
        result = selector.find_all(bs, recursive=False, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="link">1</a>"""),
            strip("""<div class="menu"><span>2</span></div>"""),
        ]
