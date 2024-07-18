"""Testing module for ChildCombinator class."""

import pytest

from soupsavvy.exceptions import NotSoupSelectorException, TagNotFoundException
from soupsavvy.tags.combinators import ChildCombinator
from soupsavvy.tags.components import AttributeSelector, TagSelector
from tests.soupsavvy.tags.conftest import find_body_element, strip, to_bs


@pytest.mark.soup
@pytest.mark.combinator
class TestChildCombinator:
    """Class for ChildCombinator unit test suite."""

    def test_raises_exception_when_invalid_input(self):
        """
        Tests if ChildCombinator raises NotSoupSelectorException when
        invalid input is provided.
        """
        with pytest.raises(NotSoupSelectorException):
            ChildCombinator(TagSelector("a"), "p")  # type: ignore

        with pytest.raises(NotSoupSelectorException):
            ChildCombinator("a", TagSelector("p"))  # type: ignore

    def test_find_returns_first_tag_matching_all_selectors(self):
        """
        Tests if find method returns the first tag that matches
        child combinator.
        """
        text = """
            <a class="link">
                <div class="link"></div>
            </a>
            <div>
                <a class="widget"></a>
            </div>
            <a>
                <span class="widget"></span>
            </a>
        """
        bs = find_body_element(to_bs(text))

        tag = ChildCombinator(
            TagSelector("a"),
            AttributeSelector("class", "widget"),
        )
        result = tag.find(bs)
        assert strip(str(result)) == strip("""<span class="widget"></span>""")

    def test_find_raises_exception_when_no_tags_match_in_strict_mode(self):
        """
        Tests if find method raises TagNotFoundException when no tag is found
        that matches child combinator in strict mode.
        """
        text = """
            <a class="link">
                <div class="link"></div>
            </a>
            <div>
                <a class="widget"></a>
            </div>
        """
        bs = to_bs(text)
        tag = ChildCombinator(
            TagSelector("a"),
            AttributeSelector("class", "widget"),
        )

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True)

    def test_find_returns_none_if_no_tags_match_in_not_strict_mode(self):
        """
        Tests if find method returns None when no tag is found that
        matches child combinator in not strict mode.
        """
        text = """
            <a class="link">
                <div class="link"></div>
            </a>
            <div>
                <a class="widget"></a>
            </div>
        """
        bs = to_bs(text)
        tag = ChildCombinator(
            TagSelector("a"),
            AttributeSelector("class", "widget"),
        )
        assert tag.find(bs) is None

    def test_finds_all_tags_matching_selectors(self):
        """
        Tests if find_all method returns all tags that match child combinator.
        """
        text = """
            <a class="link">
                <div class="link"></div>
            </a>
            <div>
                <a class="widget"></a>
            </div>
            <a>
                <div>
                    <span class="widget">Hello 1</span>
                </div>
                <div class="widget">Helo 2</div>
            </a>
            <div>
                <a>
                    <span>Hello 3</span>
                    <span class="widget">Hello 4</span>
                </a>
            </div>
        """
        bs = find_body_element(to_bs(text))

        tag = ChildCombinator(
            TagSelector("a"),
            AttributeSelector("class", "widget"),
        )
        result = tag.find_all(bs)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div class="widget">Helo 2</div>"""),
            strip("""<span class="widget">Hello 4</span>"""),
        ]

    def test_find_all_returns_empty_list_if_no_tag_matches(self):
        """
        Tests if find_all method returns an empty list when no tag is found
        that matches child combinator.
        """
        text = """
            <a class="link">
                <div class="link"></div>
            </a>
            <div>
                <a class="widget"></a>
            </div>
        """
        bs = to_bs(text)
        tag = ChildCombinator(
            TagSelector("a"),
            AttributeSelector("class", "widget"),
        )
        result = tag.find_all(bs)
        assert result == []

    def test_find_returns_match_with_multiple_selectors(self):
        """
        Tests if find method returns the first tag that matches all selectors
        in child combinator, if there are multiple selectors.
        """
        text = """
            <p>Hello World</p>
            <div>
                <p>Hello 1</p>
            </div>
            <div>
                <span>
                    <p>Hello 2</p>
                </span>
            </div>
            <div>
                <a>
                    <span>
                        <a>
                            <p>Hello 3</p>
                            <h1>Hello 4</h1>
                        </a>
                    </span>
                </a>
            </div>
            <div>
                <span>
                    <a>
                        <h1>Hello 5</h1>
                        <p>Hello 6</p>
                    </a>
                </span>
            </div>
        """
        bs = to_bs(text)
        tag = ChildCombinator(
            TagSelector("div"),
            TagSelector("span"),
            TagSelector("a"),
            TagSelector("p"),
        )
        result = tag.find(bs)
        assert strip(str(result)) == strip("""<p>Hello 6</p>""")

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        In this case first 'p' element matches the selector, but it's not a child
        of body element, so it's not returned.
        """
        text = """
            <div>
                <a href="github">
                    <p>Hello 1</p>
                </a>
            </div>
            <a class="github">Hello 2</a>
            <p>Hello 3</p>
            <a class="github"><p>Text</p></a>
        """
        bs = find_body_element(to_bs(text))
        tag = ChildCombinator(
            TagSelector("a"),
            TagSelector("p"),
        )
        result = tag.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<p>Text</p>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div>
                <a href="github">
                    <p>Hello 1</p>
                </a>
            </div>
            <a class="github">Hello 2</a>
            <p>Hello 3</p>
        """
        bs = find_body_element(to_bs(text))
        tag = ChildCombinator(
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
                <a href="github">
                    <p>Hello 1</p>
                </a>
            </div>
            <a class="github">Hello 2</a>
            <p>Hello 3</p>
        """
        bs = find_body_element(to_bs(text))
        tag = ChildCombinator(
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
            <a class="link">
                <div class="link"></div>
                <p>Text 1</p>
            </a>
            <a>
                <div>
                    <span class="widget">Hello 1</span>
                </div>
                <p>Text 2</p>
            </a>
            <div>
                <a>
                    <span>Hello 2</span>
                    <p>Text 3</p>
                </a>
            </div>
        """
        bs = find_body_element(to_bs(text))
        tag = ChildCombinator(
            TagSelector("a"),
            TagSelector("p"),
        )
        results = tag.find_all(bs, recursive=False)

        assert list(map(lambda x: strip(str(x)), results)) == [
            strip("""<p>Text 1</p>"""),
            strip("""<p>Text 2</p>"""),
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
                <a href="github">
                    <p>Hello 1</p>
                </a>
            </div>
            <a class="github">Hello 2</a>
            <p>Hello 3</p>
        """
        bs = find_body_element(to_bs(text))
        tag = ChildCombinator(
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
            <a class="link">
                <div class="link"></div>
                <p>Text 1</p>
            </a>
            <div>
                <a>
                    <span>Hello 1</span>
                    <p>Text 2</p>
                </a>
            </div>
            <a>
                <div>
                    <span class="widget">Hello 2</span>
                </div>
                <p>Text 3</p>
            </a>
        """
        bs = find_body_element(to_bs(text))
        tag = ChildCombinator(
            TagSelector("a"),
            TagSelector("p"),
        )
        results = tag.find_all(bs, limit=2)

        assert list(map(lambda x: strip(str(x)), results)) == [
            strip("""<p>Text 1</p>"""),
            strip("""<p>Text 2</p>"""),
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
            <a class="link">
                <div class="link"></div>
                <p>Text 1</p>
            </a>
            <div>
                <a>
                    <span>Hello 1</span>
                    <p>Text 2</p>
                </a>
            </div>
            <a>
                <div>
                    <span class="widget">Hello 2</span>
                </div>
                <p>Text 3</p>
                <p>Text 4</p>
            </a>
        """
        bs = find_body_element(to_bs(text))
        tag = ChildCombinator(
            TagSelector("a"),
            TagSelector("p"),
        )
        results = tag.find_all(bs, recursive=False, limit=2)

        assert list(map(lambda x: strip(str(x)), results)) == [
            strip("""<p>Text 1</p>"""),
            strip("""<p>Text 3</p>"""),
        ]
