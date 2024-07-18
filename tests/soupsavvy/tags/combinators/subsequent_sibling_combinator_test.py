"""Testing module for SubsequentSiblingCombinator class."""

import pytest

from soupsavvy.exceptions import NotSoupSelectorException, TagNotFoundException
from soupsavvy.tags.combinators import SubsequentSiblingCombinator
from soupsavvy.tags.components import TagSelector
from tests.soupsavvy.tags.conftest import find_body_element, strip, to_bs


@pytest.mark.soup
@pytest.mark.combinator
class TestSubsequentSiblingCombinator:
    """Class for SubsequentSiblingCombinator unit test suite."""

    def test_raises_exception_when_invalid_input(self):
        """
        Tests if SubsequentSiblingCombinator raises NotSoupSelectorException when
        invalid input is provided.
        """
        with pytest.raises(NotSoupSelectorException):
            SubsequentSiblingCombinator(TagSelector("a"), "p")  # type: ignore

        with pytest.raises(NotSoupSelectorException):
            SubsequentSiblingCombinator("a", TagSelector("p"))  # type: ignore

    def test_find_returns_first_tag_matching_all_selectors(self):
        """
        Tests if find method returns the first tag that matches
        subsequent sibling combinator.
        """
        text = """
            <p>Hello 1</p>
            <a class="link"></a>
            <div>
                <p>Hello 2</p>
            </div>
            <p>Hello 3</p>
            <a class="widget"></a>
            <p>Hello 4</p>
        """
        bs = find_body_element(to_bs(text))

        tag = SubsequentSiblingCombinator(
            TagSelector("a"),
            TagSelector("p"),
        )
        result = tag.find(bs)
        assert strip(str(result)) == strip("""<p>Hello 3</p>""")

    def test_find_raises_exception_when_no_tags_match_in_strict_mode(self):
        """
        Tests if find method raises TagNotFoundException when no tag is found
        that matches subsequent sibling combinator in strict mode.
        """
        text = """
            <p>Hello 1</p>
            <a class="link"></a>
            <div>
                <p>Hello 2</p>
            </div>
            <div>Hello 3</div>
        """
        bs = to_bs(text)
        tag = SubsequentSiblingCombinator(
            TagSelector("a"),
            TagSelector("p"),
        )

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True)

    def test_find_returns_none_if_no_tags_match_in_not_strict_mode(self):
        """
        Tests if find method returns None when no tag is found that
        matches subsequent sibling combinator in not strict mode.
        """
        text = """
            <p>Hello 1</p>
            <a class="link"></a>
            <div>
                <p>Hello 2</p>
            </div>
            <div>Hello 3</div>
        """
        bs = to_bs(text)
        tag = SubsequentSiblingCombinator(
            TagSelector("a"),
            TagSelector("p"),
        )
        assert tag.find(bs) is None

    def test_finds_all_tags_matching_selectors(self):
        """
        Tests if find_all method returns all tags
        that match subsequent sibling combinator.
        """
        text = """
            <p>Hello</p>
            <div>
                <a class="widget"></a>
                <p>Hello 1</p>
                <div>Text</div>
            </div>
            <a class="widget"></a>
            <div>
                <p>Hello 2</p>
            </div>
            <p>Hello 3</p>
            <p>Hello 4</p>
            <div class="link">
                <p>Child</p>
            </div>
        """
        bs = find_body_element(to_bs(text))

        tag = SubsequentSiblingCombinator(
            TagSelector("a"),
            TagSelector("p"),
        )
        result = tag.find_all(bs)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<p>Hello 1</p>"""),
            strip("""<p>Hello 3</p>"""),
            strip("""<p>Hello 4</p>"""),
        ]

    def test_finds_all_does_not_duplicate_elements(self):
        """
        Tests if find_all method returns all tags that match
        subsequent sibling combinator without duplication in case of having
        multiple tags that match first selector, like in this case with 'a' tag.
        """
        text = """
            <p>Hello</p>
            <a class="link"></a>
            <a class="widget"></a>
            <div>Hello 1</div>
            <p>Hello 2</p>
            <p>Hello 3</p>
        """
        bs = find_body_element(to_bs(text))

        tag = SubsequentSiblingCombinator(
            TagSelector("a"),
            TagSelector("p"),
        )
        result = tag.find_all(bs)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<p>Hello 2</p>"""),
            strip("""<p>Hello 3</p>"""),
        ]

    def test_find_all_returns_empty_list_if_no_tag_matches(self):
        """
        Tests if find_all method returns an empty list when no tag is found
        that matches  subsequent sibling combinator.
        """
        text = """
            <p>Hello 1</p>
            <a class="link"></a>
            <div>
                <p>Hello 2</p>
            </div>
            <div>Hello 3</div>
        """
        bs = to_bs(text)
        tag = SubsequentSiblingCombinator(
            TagSelector("a"),
            TagSelector("p"),
        )

        result = tag.find_all(bs)
        assert result == []

    def test_find_tag_for_multiple_selectors(self):
        """
        Tests if find method returns the first tag that matches
        subsequent sibling combinator with multiple selectors.
        """
        text = """
            <div>
                <a></a>
                <span></span>
                <p>Hello 1</p>
            </div>

            <div>
                <a></a>
                <span>
                    <a></a>
                    <p>Hello 2</p>
                </span>
            </div>

            <div>
                <a></a>
                <div></div>
                <span></span>
                <div></div>
                <a></a>
                <div></div>
                <p>Hello 3</p>
            </div>
        """
        bs = find_body_element(to_bs(text))
        tag = SubsequentSiblingCombinator(
            TagSelector("a"),
            TagSelector("span"),
            TagSelector("a"),
            TagSelector("p"),
        )

        result = tag.find(bs)
        assert strip(str(result)) == strip("""<p>Hello 3</p>""")

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        In this case first 'p' element matches the selector, as it occurs after
        "a" element, but it's not a child of body element.
        """
        text = """
            <p>First element</p>
            <div>
                <a class="widget"></a>
                <div>Just hanging around</div>
                <p>Hello 1</p>
            </div>
            <a class="widget"></a>
            <div>Just hanging around too</div>
            <p>Hello 2</p>
        """
        bs = find_body_element(to_bs(text))
        tag = SubsequentSiblingCombinator(
            TagSelector("a"),
            TagSelector("p"),
        )
        result = tag.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<p>Hello 2</p>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <p>First element</p>
            <div>
                <a class="widget"></a>
                <div>Just hanging around</div>
                <p>Hello 1</p>
            </div>
            <a class="widget"></a>
            <div>
                <p>Not a match</p>
            </div>
            <div>Just hanging around too</div>
        """
        bs = find_body_element(to_bs(text))
        tag = SubsequentSiblingCombinator(
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
            <p>First element</p>
            <div>
                <a class="widget"></a>
                <div>Just hanging around</div>
                <p>Hello 1</p>
            </div>
            <a class="widget"></a>
            <div>
                <p>Not a match</p>
            </div>
            <div>Just hanging around too</div>
        """
        bs = find_body_element(to_bs(text))
        tag = SubsequentSiblingCombinator(
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
            <p>First element</p>
            <div>
                <a class="widget"></a>
                <div>Just hanging around</div>
                <p>Hello 1</p>
            </div>
            <a class="widget"></a>
            <div>
                <p>Not a match</p>
            </div>
            <p>Hello 2</p>
            <span></span>
            <p>Hello 3</p>
        """
        bs = find_body_element(to_bs(text))
        tag = SubsequentSiblingCombinator(
            TagSelector("a"),
            TagSelector("p"),
        )
        results = tag.find_all(bs, recursive=False)

        assert list(map(lambda x: strip(str(x)), results)) == [
            strip("""<p>Hello 2</p>"""),
            strip("""<p>Hello 3</p>"""),
        ]

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self,
    ):
        """
        Tests if find_all returns an empty list if no child element
        matches the selector and recursive is False.
        """
        text = """
            <p>First element</p>
            <div>
                <a class="widget"></a>
                <div>Just hanging around</div>
                <p>Hello 1</p>
            </div>
            <a class="widget"></a>
            <div>
                <p>Not a match</p>
            </div>
            <div>Just hanging around too</div>
        """
        bs = find_body_element(to_bs(text))
        tag = SubsequentSiblingCombinator(
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
            <p>First element</p>
            <div>
                <a class="widget"></a>
                <div>Just hanging around</div>
                <p>Hello 1</p>
            </div>
            <a class="widget"></a>
            <div>
                <p>Not a match</p>
            </div>
            <p>Hello 2</p>
            <span></span>
            <p>Hello 3</p>
        """
        bs = find_body_element(to_bs(text))
        tag = SubsequentSiblingCombinator(
            TagSelector("a"),
            TagSelector("p"),
        )
        results = tag.find_all(bs, limit=2)

        assert list(map(lambda x: strip(str(x)), results)) == [
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
            <p>First element</p>
            <div>
                <a class="widget"></a>
                <div>Just hanging around</div>
                <p>Hello 1</p>
            </div>
            <a class="widget"></a>
            <div>
                <p>Not a match</p>
            </div>
            <p>Hello 2</p>
            <span></span>
            <p>Hello 3</p>
            <p>Hello 4</p>
        """
        bs = find_body_element(to_bs(text))
        tag = SubsequentSiblingCombinator(
            TagSelector("a"),
            TagSelector("p"),
        )
        results = tag.find_all(bs, recursive=False, limit=2)

        assert list(map(lambda x: strip(str(x)), results)) == [
            strip("""<p>Hello 2</p>"""),
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
        tag = SubsequentSiblingCombinator(
            TagSelector("html"),
            TagSelector("p"),
        )
        # manipulate html Tag to have no parent (surprising it does have itself as parent)
        bs.find("html").parent = None  # type: ignore
        tag.find(bs)
