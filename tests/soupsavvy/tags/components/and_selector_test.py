"""Testing module for AndSelector class."""

import pytest

from soupsavvy.tags.combinators import DescendantCombinator
from soupsavvy.tags.components import AndSelector, AttributeSelector, TagSelector
from soupsavvy.tags.exceptions import NotSoupSelectorException, TagNotFoundException
from tests.soupsavvy.tags.conftest import find_body_element, strip, to_bs


@pytest.mark.soup
class TestAndSelector:
    """Class for AndSelector unit test suite."""

    def test_raises_exception_when_no_invalid_input(self):
        """
        Tests if init raises NotSoupSelectorException when invalid input is provided.
        All of the parameters must be SoupSelector instances.
        """
        with pytest.raises(NotSoupSelectorException):
            AndSelector("div", AttributeSelector("class"))  # type: ignore

    def test_find_returns_first_tag_matching_all_selectors(self):
        """
        Tests if find method returns the first tag that matches all the selectors.
        """
        markup = """
            <a class="link"></a>
            <div class="widget"></div>
            <a class="widget"></a>
        """
        bs = to_bs(markup)

        tag = AndSelector(TagSelector("a"), AttributeSelector("class", "widget"))
        result = tag.find(bs)
        assert str(result) == strip("""<a class="widget"></a>""")

    def test_find_raises_exception_when_no_tags_match_in_strict_mode(self):
        """
        Tests if find method raises TagNotFoundException when no tag is found
        that matches all the selectors in strict mode.
        """
        markup = """<div class="widget"></div><a class="link"></a>"""
        bs = to_bs(markup)
        tag = AndSelector(TagSelector("a"), AttributeSelector("class", "widget"))

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True)

    def test_find_returns_none_if_no_tags_match_in_not_strict_mode(self):
        """
        Tests if find method returns None when no tag is found that
        matches all the selectors in not strict mode.
        """
        markup = """<div class="widget"></div><a class="link"></a>"""
        bs = to_bs(markup)
        tag = AndSelector(TagSelector("a"), AttributeSelector("class", "widget"))
        assert tag.find(bs) is None

    def test_find_returns_first_tag_that_matches_more_than_two_selectors(self):
        """
        Tests if find method returns the first tag that matches all the selectors.
        In this case testing for multiple selectors. For tag to be selected
        it must match all the selectors.
        """
        markup = """
            <a class="123"></a>
            <div><a class="widget 12"></a></div>
            <div class="123"></div>
            <a class="link"></a>
            <div class="link"></div>
        """
        bs = to_bs(markup)

        tag = AndSelector(
            TagSelector("a"),
            AttributeSelector("class", "1", re=True),
            DescendantCombinator(TagSelector("div"), TagSelector("a")),
        )
        result = tag.find(bs)
        assert str(result) == strip("""<a class="widget 12"></a>""")

    def test_finds_all_tags_matching_selectors(self):
        """
        Tests if find_all method returns all tags that match all the selectors.
        """
        markup = """
            <a class="widget 12"></a>
            <div class="123"></div>
            <span class="empty"></span>
            <a class="link"></a>
            <div><a class="11"></a></div>
            <div class="link"></div>
            <a class="123"></a>
        """
        bs = to_bs(markup)

        tag = AndSelector(TagSelector("a"), AttributeSelector("class", "1", re=True))
        result = tag.find_all(bs)

        assert list(map(str, result)) == [
            strip("""<a class="widget 12"></a>"""),
            strip("""<a class="11"></a>"""),
            strip("""<a class="123"></a>"""),
        ]

    def test_find_all_returns_empty_list_if_no_tag_matches(self):
        """
        Tests if find_all method returns an empty list when no tag is found
        that matches all the selectors.
        """
        markup = """
            <a class="12"></a>
            <div class="widget"></div>
            <a class="link"></a>
            <span class="menu"></span>
        """
        bs = to_bs(markup)

        tag = AndSelector(TagSelector("a"), AttributeSelector("class", "widget"))
        result = tag.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        In this case first 'a' element matches the selector,
        but it's not a child of body element, so it's not returned.
        """
        text = """
            <div class="google">
                <a class="github">Hello 1</a>
            </div>
            <a href="github">Hello 2</a>
            <a class="github">Hello 3</a>
        """
        bs = find_body_element(to_bs(text))
        tag = AndSelector(TagSelector("a"), AttributeSelector("class"))
        result = tag.find(bs, recursive=False)
        assert str(result) == strip("""<a class="github">Hello 3</a>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False. In this case first 'a' element matches the selector,
        but it's not a child of body element, so it's not returned.
        """
        text = """
            <div class="google">
                <a class="github">Hello 1</a>
            </div>
            <a href="github">Hello 2</a>
        """
        bs = find_body_element(to_bs(text))
        tag = AndSelector(TagSelector("a"), AttributeSelector("class"))
        result = tag.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <div class="google">
                <a class="github">Hello 1</a>
            </div>
            <a href="github">Hello 2</a>
        """
        bs = find_body_element(to_bs(text))
        tag = AndSelector(TagSelector("a"), AttributeSelector("class"))

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True, recursive=False)

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <div class="google">
                <a class="github">Hello 1</a>
            </div>
            <a class="github">Hello 2</a>
            <a href="github">Hello 3</a>
            <a class="">Hello 4</a>
        """
        bs = find_body_element(to_bs(text))
        tag = AndSelector(TagSelector("a"), AttributeSelector("class"))
        results = tag.find_all(bs, recursive=False)

        assert list(map(str, results)) == [
            strip("""<a class="github">Hello 2</a>"""),
            strip("""<a class="">Hello 4</a>"""),
        ]

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self,
    ):
        """
        Tests if find_all returns an empty list if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div class="google">
                <a class="github">Hello 1</a>
            </div>
            <a href="github">Hello 2</a>
        """
        bs = find_body_element(to_bs(text))
        tag = AndSelector(TagSelector("a"), AttributeSelector("class"))

        results = tag.find_all(bs, recursive=False)
        assert results == []

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <span class="link"></span>
            <div>
                <div class="">Hello 1</div>
            </div>
            <div>Hello 2</div>
            <div class="link">Hello 3</div>
            <div class="menu">Hello 4</div>
            <div class="">Hello 5</div>
        """
        bs = find_body_element(to_bs(text))
        tag = AndSelector(TagSelector("div"), AttributeSelector("class"))
        results = tag.find_all(bs, limit=2)

        assert list(map(str, results)) == [
            strip("""<div class="">Hello 1</div>"""),
            strip("""<div class="link">Hello 3</div>"""),
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
            <span class="link"></span>
            <div>
                <div class="">Hello 1</div>
            </div>
            <div>Hello 2</div>
            <div class="link">Hello 3</div>
            <div class="menu">Hello 4</div>
            <div class="">Hello 5</div>
        """
        bs = find_body_element(to_bs(text))
        tag = AndSelector(TagSelector("div"), AttributeSelector("class"))
        results = tag.find_all(bs, recursive=False, limit=2)

        assert list(map(str, results)) == [
            strip("""<div class="link">Hello 3</div>"""),
            strip("""<div class="menu">Hello 4</div>"""),
        ]
