"""Testing module for NotElementTag class."""

import pytest

from soupsavvy.tags.combinators import SelectorList
from soupsavvy.tags.components import AttributeTag, ElementTag, NotElementTag
from soupsavvy.tags.exceptions import NotSelectableSoupException, TagNotFoundException

from .conftest import find_body_element, strip, to_bs


@pytest.mark.soup
class TestNotElementTag:
    """Class for NotElementTag unit test suite."""

    def test_find_returns_first_tag_not_matching_selector(self):
        """
        Tests if find method returns the first tag that does not match the
        selector. In this case testing for simple one element tag.
        """
        markup = """<a class="widget"></a><div class="widget"></div>"""
        bs = find_body_element(to_bs(markup))

        tag = NotElementTag(ElementTag("a"))
        result = tag.find(bs)
        assert str(result) == strip("""<div class="widget"></div>""")

    def test_raises_exception_when_no_invalid_input(self):
        """
        Tests if init raises NotSelectableSoupException when invalid input is provided.
        All of the parameters must be SelectableSoup instances.
        """
        with pytest.raises(NotSelectableSoupException):
            NotElementTag("div", AttributeTag("class"))  # type: ignore

    def test_find_raises_exception_when_all_tags_match_in_strict_mode(self):
        """
        Tests if find method raises TagNotFoundException when no tag is found
        that does not match the selector in strict mode.
        """
        markup = """<a class="widget"></a><a class="link"></a>"""
        bs = find_body_element(to_bs(markup))
        tag = NotElementTag(ElementTag("a"))

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True)

    def test_find_returns_none_if_all_tags_match_in_not_strict_mode(self):
        """
        Tests if find method returns None when no tag is found that does not
        match the selector in not strict mode.
        """
        markup = """<a class="widget"></a><a class="link"></a>"""
        bs = find_body_element(to_bs(markup))
        tag = NotElementTag(ElementTag("a"))
        assert tag.find(bs) is None

    def test_find_returns_first_tag_not_matching_selector_for_multiple_selectors(self):
        """
        Tests if find method returns the first tag that does not match the
        selector. In this case testing for multiple selectors. For tag to be selected
        it must not match any of the selectors.
        """
        markup = """
            <a class="widget 12"></a>
            <div class="123"></div>
            <a class="link"></a>
            <div class="link"></div>
        """
        bs = find_body_element(to_bs(markup))

        tag = NotElementTag(ElementTag("a"), AttributeTag("class", "1", re=True))
        result = tag.find(bs)
        assert str(result) == strip("""<div class="link"></div>""")

    def test_find_all_not_matching_tags(self):
        """
        Tests if find_all method returns all tags that do not match the selector.
        """
        markup = """
            <a class="widget 12"></a>
            <div class="123"></div>
            <span class="empty"></span>
            <a class="link"></a>
            <div class="link"></div>
        """
        bs = find_body_element(to_bs(markup))

        tag = NotElementTag(ElementTag("a"), AttributeTag("class", "1", re=True))
        result = tag.find_all(bs)

        assert list(map(str, result)) == [
            strip("""<span class="empty"></span>"""),
            strip("""<div class="link"></div>"""),
        ]

    def test_find_all_returns_empty_list_if_every_tag_matches(self):
        """
        Tests if find_all method returns an empty list when all tags match the selector.
        """
        markup = """
            <a class="widget 12"></a>
            <div class="123"></div>
            <a class="link"></a>
        """
        bs = find_body_element(to_bs(markup))

        tag = NotElementTag(ElementTag("a"), AttributeTag("class", "2", re=True))
        result = tag.find_all(bs)
        assert result == []

    def test_find_returns_first_tag_with_children_if_does_not_match(self):
        """
        Tests if find method returns the first tag that does not match the selector.
        It iterates recursively over the children of the tag and selects
        the first tag that does not match the selector, in this case - parent 'div'.
        """
        markup = """
            <div><a class="widget 12"></a></div>
            <span class="empty"></span>
        """
        bs = find_body_element(to_bs(markup))

        tag = NotElementTag(ElementTag("span"))
        result = tag.find(bs)

        assert str(result) == strip("""<div><a class="widget 12"></a></div>""")

    def test_finds_all_returns_all_parents_and_children_tags_not_matching(self):
        """
        Tests if find_all method returns all tags that do not match the selector.
        It should select both parents and all their children in this order
        """
        markup = """
            <div><a class="widget 12"></a></div>
            <span class="empty"></span>
        """
        bs = find_body_element(to_bs(markup))

        tag = NotElementTag(ElementTag("span"))
        result = tag.find_all(bs)

        assert list(map(str, result)) == [
            strip("""<div><a class="widget 12"></a></div>"""),
            strip("""<a class="widget 12"></a>"""),
        ]

    def test_bitwise_not_operator_returns_not_element_tag(self):
        """
        Tests if bitwise NOT operator (__invert__) returns NotElementTag instance
        with the same selector.
        """
        tag = ElementTag("a")
        negation = ~tag
        assert isinstance(negation, NotElementTag)
        assert negation.steps == [tag]

    def test_bitwise_not_operator_on_not_element_tag_returns_tag(self):
        """
        Tests if bitwise NOT operator (__invert__) returns the original tag
        when applied to NotElementTag instance with single selector.
        """
        tag = ElementTag("a")
        not_element = NotElementTag(tag)
        negation = ~not_element
        assert negation == tag

    def test_bitwise_not_operator_on_not_element_tag_with_multiple_selectors_returns_union(
        self,
    ):
        """
        Tests if bitwise NOT operator (__invert__) returns SoupUnionTag instance
        when applied to NotElementTag instance with multiple selectors.
        """
        tag1 = ElementTag("a")
        tag2 = ElementTag("div")
        not_element = NotElementTag(tag1, tag2)
        negation = ~not_element
        assert negation == SelectorList(tag1, tag2)

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        In this case first 'span' element matches the selector, but it's not a child
        of body element, so it's not returned.
        """
        text = """
            <a class="google">
                <span>Hello 1</span>
            </a>
            <a href="github">Hello 2</a>
            <div>Hello 3</div>
        """
        bs = find_body_element(to_bs(text))
        tag = NotElementTag(ElementTag(tag="a"))
        result = tag.find(bs, recursive=False)
        assert str(result) == strip("""<div>Hello 3</div>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False. In this case first 'a' element matches the selector,
        but it's not a child of body element, so it's not returned.
        """
        text = """
            <a class="google">
                <span>Hello 1</span>
            </a>
            <a>Hello 2</a>
        """
        bs = find_body_element(to_bs(text))
        tag = NotElementTag(ElementTag(tag="a"))
        result = tag.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <a class="google">
                <span>Hello 1</span>
            </a>
            <a>Hello 2</a>
        """
        bs = find_body_element(to_bs(text))
        tag = NotElementTag(ElementTag(tag="a"))

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True, recursive=False)

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <a class="google">
                <span>Hello 1</span>
                <p>Hello 2</p>
            </a>
            <div>Hello 3</div>
            <a class="link">Hello 4</a>
            <span>Hello 5</span>
        """
        bs = find_body_element(to_bs(text))
        tag = NotElementTag(ElementTag(tag="a"))
        results = tag.find_all(bs, recursive=False)

        assert list(map(str, results)) == [
            strip("""<div>Hello 3</div>"""),
            strip("""<span>Hello 5</span>"""),
        ]

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self,
    ):
        """
        Tests if find_all returns an empty list if no child element matches the selector
        and recursive is False.
        """
        text = """
            <a class="google">
                <span>Hello 1</span>
            </a>
            <a>Hello 2</a>
        """
        bs = find_body_element(to_bs(text))
        tag = NotElementTag(ElementTag(tag="a"))

        results = tag.find_all(bs, recursive=False)
        assert results == []

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <a>
                <div>Hello 1</div>
            </a>
            <span>Hello 2</span>
            <div>Hello 3</div>
            <div>Hello 4</div>
        """
        bs = find_body_element(to_bs(text))
        tag = NotElementTag(ElementTag(tag="a"))
        results = tag.find_all(bs, limit=2)

        assert list(map(str, results)) == [
            strip("""<div>Hello 1</div>"""),
            strip("""<span>Hello 2</span>"""),
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
            <a>
                <div>Hello 1</div>
            </a>
            <span>Hello 2</span>
            <div>Hello 3</div>
            <div>Hello 4</div>
        """
        bs = find_body_element(to_bs(text))
        tag = NotElementTag(ElementTag(tag="a"))
        results = tag.find_all(bs, recursive=False, limit=2)

        assert list(map(str, results)) == [
            strip("""<span>Hello 2</span>"""),
            strip("""<div>Hello 3</div>"""),
        ]
