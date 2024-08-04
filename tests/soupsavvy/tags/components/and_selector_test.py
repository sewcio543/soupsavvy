"""Testing module for AndSelector class."""

import pytest

from soupsavvy.exceptions import NotSoupSelectorException, TagNotFoundException
from soupsavvy.tags.components import AndSelector
from tests.soupsavvy.tags.conftest import (
    MockClassMenuSelector,
    MockClassWidgetSelector,
    MockDivSelector,
    MockLinkSelector,
    find_body_element,
    strip,
    to_bs,
)


@pytest.mark.selector
class TestAndSelector:
    """Class for AndSelector unit test suite."""

    def test_raises_exception_when_no_invalid_input(self):
        """
        Tests if init raises NotSoupSelectorException when invalid input is provided.
        All of the parameters must be SoupSelector instances.
        """
        with pytest.raises(NotSoupSelectorException):
            AndSelector("div", MockDivSelector())  # type: ignore

        with pytest.raises(NotSoupSelectorException):
            AndSelector(MockClassMenuSelector(), MockLinkSelector(), "div")  # type: ignore

    def test_find_returns_first_tag_matching_selector(self):
        """
        Tests if find method returns the first tag that matches all the selectors.
        """
        text = """
            <a class="link"></a>
            <div class="widget"></div>
            <a class="menu">1</a>
            <div class="menu"></div>
            <a class="menu">2</a>
        """
        bs = to_bs(text)
        selector = AndSelector(MockLinkSelector(), MockClassMenuSelector())
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<a class="menu">1</a>""")

    def test_find_raises_exception_when_no_tags_match_in_strict_mode(self):
        """
        Tests if find method raises TagNotFoundException when no tag is found
        that matches all the selectors in strict mode.
        """
        text = """
            <a class="link"></a>
            <div class="widget"></div>
            <div class="menu"></div>
            <a class="menu123"></a>
        """
        bs = to_bs(text)
        selector = AndSelector(MockLinkSelector(), MockClassMenuSelector())

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_returns_none_if_no_tags_match_in_not_strict_mode(self):
        """
        Tests if find method returns None when no tag is found that
        matches all the selectors in not strict mode.
        """
        text = """
            <a class="link"></a>
            <div class="menu"></div>
            <div class="widget"></div>
            <a class="menu123"></a>
        """
        bs = to_bs(text)
        selector = AndSelector(MockLinkSelector(), MockClassMenuSelector())
        result = selector.find(bs)
        assert result is None

    def test_find_returns_match_with_multiple_selectors(self):
        """
        Tests if find method returns the first tag that matches selector
        if there are multiple selectors are provided.
        """
        text = """
            <div class="widget"></div>
            <span class="widget menu"></span>
            <a class="link"></a>
            <div class="menu page"></div>
            <div class="widget menu">1</div>
            <div class="link"></div>
            <div class="menu widget row">2</div>
        """
        bs = to_bs(text)

        selector = AndSelector(
            MockDivSelector(),
            MockClassMenuSelector(),
            MockClassWidgetSelector(),
        )
        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div class="widget menu">1</div>"""),
            strip("""<div class="menu widget row">2</div>"""),
        ]

    def test_finds_all_tags_matching_selectors(self):
        """
        Tests if find_all method returns all tags that match all the selectors.
        """
        text = """
            <a class="link"></a>
            <div class="widget"></div>
            <a class="menu">1</a>
            <span>Hello</span>
            <a class="menu"><span>2</span></a>
            <a class="menu widget">3</a>
            <div class="menu"></div>
            <div>
                <a class="menu_widget"></a>
                <a class="menu">4</a>
            </div>
            <span class=""></span>
        """
        bs = to_bs(text)
        selector = AndSelector(MockLinkSelector(), MockClassMenuSelector())
        result = selector.find_all(bs)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="menu">1</a>"""),
            strip("""<a class="menu"><span>2</span></a>"""),
            strip("""<a class="menu widget">3</a>"""),
            strip("""<a class="menu">4</a>"""),
        ]

    def test_find_all_returns_empty_list_if_no_tag_matches(self):
        """
        Tests if find_all method returns an empty list when no tag is found
        that matches all the selectors.
        """
        text = """
            <a class="link"></a>
            <div class="menu"></div>
            <div class="widget"></div>
            <a class="menu123"></a>
        """
        bs = to_bs(text)
        selector = AndSelector(MockLinkSelector(), MockClassMenuSelector())
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <a class="link"></a>
            <div>
                <a class="menu_widget"></a>
                <a class="menu">Not a child</a>
                <div>
                    <a class="menu">Not a child</a>
                </div>
            </div>
            <a class="menu">1</a>
            <div class="widget"></div>
            <a class="menu">2</a>
            <span>Hello</span>
        """
        bs = find_body_element(to_bs(text))
        selector = AndSelector(MockLinkSelector(), MockClassMenuSelector())
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<a class="menu">1</a>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <a class="link"></a>
            <div>
                <a class="menu_widget"></a>
                <a class="menu">Not a child</a>
                <div>
                    <a class="menu">Not a child</a>
                </div>
            </div>
            <span>Hello</span>
            <div class="menu"></div>
        """
        bs = find_body_element(to_bs(text))
        selector = AndSelector(MockLinkSelector(), MockClassMenuSelector())
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <a class="link"></a>
            <div>
                <a class="menu_widget"></a>
                <a class="menu">Not a child</a>
                <div>
                    <a class="menu">Not a child</a>
                </div>
            </div>
            <span>Hello</span>
            <div class="menu"></div>
        """
        bs = find_body_element(to_bs(text))
        selector = AndSelector(MockLinkSelector(), MockClassMenuSelector())

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <a class="link"></a>
            <a class="menu">1</a>
            <div>
                <a class="menu_widget"></a>
                <a class="menu">Not a child</a>
                <div>
                    <a class="menu">Not a child</a>
                </div>
            </div>
            <div class="widget"></div>
            <a class="menu"><span>2</span></a>
            <span>Hello</span>
            <a class="menu widget">3</a>
        """
        bs = find_body_element(to_bs(text))
        selector = AndSelector(MockLinkSelector(), MockClassMenuSelector())
        result = selector.find_all(bs, recursive=False)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="menu">1</a>"""),
            strip("""<a class="menu"><span>2</span></a>"""),
            strip("""<a class="menu widget">3</a>"""),
        ]

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self,
    ):
        """
        Tests if find_all returns an empty list if no child element matches the selector
        and recursive is False.
        """
        text = """
            <a class="link"></a>
            <div>
                <a class="menu_widget"></a>
                <a class="menu">Not a child</a>
                <div>
                    <a class="menu">Not a child</a>
                </div>
            </div>
            <div class="widget"></div>
            <span>Hello</span>
        """
        bs = find_body_element(to_bs(text))
        selector = AndSelector(MockLinkSelector(), MockClassMenuSelector())
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <a class="link"></a>
            <div class="widget"></div>
            <a class="menu">1</a>
            <span>Hello</span>
            <a class="menu"><span>2</span></a>
            <a class="menu widget">3</a>
            <div class="menu"></div>
            <div>
                <a class="menu_widget"></a>
                <a class="menu">4</a>
            </div>
            <span class=""></span>
        """
        bs = find_body_element(to_bs(text))
        selector = AndSelector(MockLinkSelector(), MockClassMenuSelector())
        result = selector.find_all(bs, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="menu">1</a>"""),
            strip("""<a class="menu"><span>2</span></a>"""),
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
            <a class="link"></a>
            <a class="menu">1</a>
            <div class="widget"></div>
            <div>
                <a class="menu_widget"></a>
                <a class="menu">Not a child</a>
            </div>
            <span>Hello</span>
            <a class="menu"><span>2</span></a>
            <a class="menu widget">3</a>
            <div class="menu"></div>
            <span class=""></span>
        """
        bs = find_body_element(to_bs(text))
        selector = AndSelector(MockLinkSelector(), MockClassMenuSelector())
        result = selector.find_all(bs, recursive=False, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="menu">1</a>"""),
            strip("""<a class="menu"><span>2</span></a>"""),
        ]
