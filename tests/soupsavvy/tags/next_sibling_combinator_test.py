"""Testing module for NextSiblingCombinator class."""

import pytest

from soupsavvy.tags.combinators import NextSiblingCombinator
from soupsavvy.tags.components import AttributeSelector, TagSelector
from soupsavvy.tags.exceptions import NotSelectableSoupException, TagNotFoundException

from .conftest import find_body_element, strip, to_bs


@pytest.mark.soup
@pytest.mark.combinator
class TestNextSiblingCombinator:
    """Class for NextSiblingCombinator unit test suite."""

    def test_raises_exception_when_invalid_input(self):
        """
        Tests if NextSiblingCombinator raises NotSelectableSoupException when
        invalid input is provided.
        """
        with pytest.raises(NotSelectableSoupException):
            NextSiblingCombinator(TagSelector("a"), "p")  # type: ignore

        with pytest.raises(NotSelectableSoupException):
            NextSiblingCombinator("a", TagSelector("p"))  # type: ignore

    def test_find_returns_first_tag_matching_all_selectors(self):
        """
        Tests if find method returns the first tag that matches
        next sibling combinator.
        """
        text = """
            <p>Hello 1</p>
            <a class="link"></a>
            <div>Hello 2</div>
            <p>Hello 3</p>
            <a class="widget"></a>
            <p>Hello 4</p>
        """
        bs = find_body_element(to_bs(text))

        tag = NextSiblingCombinator(
            TagSelector("a"),
            TagSelector("p"),
        )
        result = tag.find(bs)
        assert str(result) == strip("""<p>Hello 4</p>""")

    def test_find_raises_exception_when_no_tags_match_in_strict_mode(self):
        """
        Tests if find method raises TagNotFoundException when no tag is found
        that matches next sibling combinator in strict mode.
        """
        text = """
            <p>Hello 1</p>
            <a class="link"></a>
            <div>Hello 2</div>
            <p>Hello 3</p>
            <a class="widget"></a>
        """
        bs = to_bs(text)
        tag = NextSiblingCombinator(
            TagSelector("a"),
            TagSelector("p"),
        )

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True)

    def test_find_returns_none_if_no_tags_match_in_not_strict_mode(self):
        """
        Tests if find method returns None when no tag is found that
        matches next sibling combinator in not strict mode.
        """
        text = """
            <p>Hello 1</p>
            <a class="link"></a>
            <div>Hello 2</div>
            <p>Hello 3</p>
            <a class="widget"></a>
        """
        bs = to_bs(text)
        tag = NextSiblingCombinator(
            TagSelector("a"),
            TagSelector("p"),
        )
        assert tag.find(bs) is None

    def test_finds_all_tags_matching_selectors(self):
        """
        Tests if find_all method returns all tags that match next sibling combinator.
        """
        text = """
            <div>
                <a class="widget"></a>
                <p>Hello 1</p>
                <div>Text</div>
            </div>
            <a class="link">
                <p>Child</p>
            </a>
            <div>Hello 2</div>
            <p>Hello 3</p>
            <a class="widget"></a>
            <p>Hello 4</p>
        """
        bs = find_body_element(to_bs(text))

        tag = NextSiblingCombinator(
            TagSelector("a"),
            TagSelector("p"),
        )
        result = tag.find_all(bs)

        assert list(map(str, result)) == [
            strip("""<p>Hello 1</p>"""),
            strip("""<p>Hello 4</p>"""),
        ]

    def test_find_tag_for_multiple_selectors(self):
        """
        Tests if find method returns the first tag that matches
        next sibling combinator for multiple selectors.
        """
        text = """
            <div></div>
            <a></a>
            <span></span>
            <p>Hello 1</p>

            <div></div>
            <span></span>
            <a></a>
            <div></div>
            <p>Hello 2</p>

            <div></div>
            <span></span>
            <a></a>
            <p>Hello 3</p>
        """
        bs = find_body_element(to_bs(text))
        tag = NextSiblingCombinator(
            TagSelector("div"),
            TagSelector("span"),
            TagSelector("a"),
            TagSelector("p"),
        )

        result = tag.find(bs)
        assert str(result) == strip("""<p>Hello 3</p>""")

    def test_find_all_returns_empty_list_if_no_tag_matches(self):
        """
        Tests if find_all method returns an empty list when no tag is found
        that matches  next sibling combinator.
        """
        text = """
            <p>Hello 1</p>
            <a class="link"></a>
            <div>Hello 2</div>
            <p>Hello 3</p>
            <a class="widget"></a>
        """
        bs = to_bs(text)
        tag = NextSiblingCombinator(
            TagSelector("a"),
            TagSelector("p"),
        )

        result = tag.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        In this case first 'p' element matches the selector, as it occurs after
        "a" element, but it's not a child of body element.
        """
        text = """
            <div>
                <a class="widget"></a>
                <p>Hello 1</p>
            </div>
            <a class="widget"></a>
            <p>Hello 2</p>
        """
        bs = find_body_element(to_bs(text))
        tag = NextSiblingCombinator(
            TagSelector("a"),
            TagSelector("p"),
        )
        result = tag.find(bs, recursive=False)
        assert str(result) == strip("""<p>Hello 2</p>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div>
                <a class="widget"></a>
                <p>Hello 1</p>
            </div>
            <p>Hello 2</p>
            <a class="widget"></a>
            <div>Hello 3</div>
        """
        bs = find_body_element(to_bs(text))
        tag = NextSiblingCombinator(
            TagSelector("a"),
            TagSelector("p"),
        )
        result = tag.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <div>
                <a class="widget"></a>
                <p>Hello 1</p>
            </div>
            <p>Hello 2</p>
            <a class="widget"></a>
            <div>Hello 3</div>
        """
        bs = find_body_element(to_bs(text))
        tag = NextSiblingCombinator(
            TagSelector("a"),
            TagSelector("p"),
        )

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True, recursive=False)

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <a class="widget"></a>
            <p>Hello 1</p>
            <div>
                <a class="widget"></a>
                <p>Hello 2</p>
                <div>Text</div>
            </div>
            <a class="link">
                <p>Child</p>
            </a>
            <div>Hello 3</div>
            <p>Hello 4</p>
            <a class="widget"></a>
            <p>Hello 5</p>
        """
        bs = find_body_element(to_bs(text))
        tag = NextSiblingCombinator(
            TagSelector("a"),
            TagSelector("p"),
        )
        results = tag.find_all(bs, recursive=False)

        assert list(map(str, results)) == [
            strip("""<p>Hello 1</p>"""),
            strip("""<p>Hello 5</p>"""),
        ]

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self,
    ):
        """
        Tests if find_all returns an empty list if no child element
        matches the selector and recursive is False.
        """
        text = """
            <div>
                <a class="widget"></a>
                <p>Hello 1</p>
            </div>
            <p>Hello 2</p>
            <a class="widget"></a>
            <div>Hello 3</div>
        """
        bs = find_body_element(to_bs(text))
        tag = NextSiblingCombinator(
            TagSelector("a"),
            TagSelector("p"),
        )

        results = tag.find_all(bs, recursive=False)
        assert results == []

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <a class="widget"></a>
            <p>Hello 1</p>
            <div>
                <a class="widget"></a>
                <p>Hello 2</p>
                <div>Text</div>
            </div>
            <a class="link">
                <p>Child</p>
            </a>
            <div>Hello 3</div>
            <p>Hello 4</p>
            <a class="widget"></a>
            <p>Hello 5</p>
        """
        bs = find_body_element(to_bs(text))
        tag = NextSiblingCombinator(
            TagSelector("a"),
            TagSelector("p"),
        )
        results = tag.find_all(bs, limit=2)

        assert list(map(str, results)) == [
            strip("""<p>Hello 1</p>"""),
            strip("""<p>Hello 2</p>"""),
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
            <a class="widget"></a>
            <p>Hello 1</p>
            <div>
                <a class="widget"></a>
                <p>Hello 2</p>
                <div>Text</div>
            </div>
            <a class="link">
                <p>Child</p>
            </a>
            <p>Hello 3</p>
            <a class="widget"></a>
            <p>Hello 4</p>
            <div>Hello 5</div>
        """
        bs = find_body_element(to_bs(text))
        tag = NextSiblingCombinator(
            TagSelector("a"),
            TagSelector("p"),
        )
        results = tag.find_all(bs, recursive=False, limit=2)

        assert list(map(str, results)) == [
            strip("""<p>Hello 1</p>"""),
            strip("""<p>Hello 3</p>"""),
        ]

    @pytest.mark.edge_case
    def test_continue_if_first_element_has_no_parent(self):
        """
        Tests if find_all continues searching if first element has no parents.
        It is only possible when html element is the first element in the markup.
        This edge case test is only important for testing coverage and should not
        an issue in normal use cases.
        """
        text = """<p>First element</p>"""
        bs = to_bs(text)
        tag = NextSiblingCombinator(
            TagSelector("html"),
            TagSelector("p"),
        )
        # manipulate html Tag to have no parent (surprising it does have itself as parent)
        bs.find("html").parent = None  # type: ignore
        tag.find(bs)
