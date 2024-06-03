"""Testing module for DescendantCombinator class."""

import pytest

from soupsavvy.tags.combinators import DescendantCombinator, SelectorList
from soupsavvy.tags.components import (
    AnyTagSelector,
    AttributeSelector,
    PatternSelector,
    TagSelector,
)
from soupsavvy.tags.exceptions import NotSoupSelectorException, TagNotFoundException
from tests.soupsavvy.tags.conftest import find_body_element, strip, to_bs


@pytest.mark.soup
@pytest.mark.combinator
class TestDescendantCombinator:
    """Class for DescendantCombinator unit test suite."""

    def test_not_SoupSelector_in_init_raises_exception(self):
        """
        Tests if NotSoupSelectorException is raised when one of input parameters
        is not a SoupSelector object.
        """
        with pytest.raises(NotSoupSelectorException):
            DescendantCombinator(TagSelector(tag="div"), "string")  # type: ignore

    @pytest.mark.parametrize(
        argnames="tag",
        argvalues=[
            DescendantCombinator(TagSelector(tag="div"), TagSelector(tag="a")),
            DescendantCombinator(
                TagSelector(
                    tag="div",
                    attributes=[AttributeSelector(name="class", value="container")],
                ),
                TagSelector(
                    tag="a", attributes=[AttributeSelector(name="href", value="search")]
                ),
            ),
            DescendantCombinator(TagSelector(tag="div"), AnyTagSelector()),
            DescendantCombinator(
                AttributeSelector(name="href", value="google"), TagSelector("a")
            ),
            DescendantCombinator(
                TagSelector(tag="div"),
                PatternSelector(tag=TagSelector("a"), pattern="Welcome"),
            ),
        ],
        ids=[
            "with_only_tag_names",
            "with_tags_attributes",
            "with_any_tag",
            "with_only_attribute",
            "with_pattern_tag",
        ],
    )
    def test_element_is_found_for_valid_steps_elements(self, tag: DescendantCombinator):
        """
        Tests if element was found for various valid DescendantCombinator.
        Element is returned if it matches multi-step tags.
        """
        text = """
            <div class="container" href="google">
                <a class="link" href="search">Welcome</a>
            </div>
        """
        bs = to_bs(text)
        result = tag.find(bs)
        assert str(result) == strip("""<a class="link" href="search">Welcome</a>""")

    @pytest.mark.parametrize(
        argnames="tag",
        argvalues=[
            DescendantCombinator(TagSelector(tag="div"), TagSelector(tag="span")),
            DescendantCombinator(TagSelector(tag="footer"), TagSelector(tag="a")),
            DescendantCombinator(
                TagSelector(
                    tag="div",
                    attributes=[AttributeSelector(name="class", value="container")],
                ),
                TagSelector(
                    tag="a",
                    attributes=[AttributeSelector(name="href", value="funhub.com")],
                ),
            ),
            DescendantCombinator(
                AttributeSelector(name="href", value="funhub.com"), TagSelector("a")
            ),
            DescendantCombinator(
                TagSelector(tag="div"),
                PatternSelector(tag=TagSelector("a"), pattern="Goodbye"),
            ),
        ],
        ids=[
            "with_only_tag_names",
            "with_tags_attributes",
            "with_empty_element_tag",
            "with_only_attribute",
            "with_pattern_tag",
        ],
    )
    def test_element_is_not_found_for_not_matching_steps_tags(
        self, tag: DescendantCombinator
    ):
        """
        Tests if element was not found for various invalid DescendantCombinator
        and None was returned.
        """
        text = """
            <div class="container" href="google">
                <a class="link" href="search">Welcome</a>
            </div>
        """
        bs = to_bs(text)
        assert tag.find(bs) is None

    def test_find_raises_exception_when_tag_not_found_in_strict_mode(self):
        """
        Tests if find raises TagNotFoundException exception if no element was found
        and method was called in a strict mode.
        """
        text = """
             <div class="container" href="google">
                <a class="link" href="search">Welcome</a>
            </div>
        """
        bs = to_bs(text)
        tag = DescendantCombinator(TagSelector(tag="div"), TagSelector(tag="span"))

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True)

    def test_finds_nested_elements_that_are_not_direct_children(self):
        """
        Tests if DescendantCombinator find method returns matching elements if they
        are in markup as not direct children of previous element in steps.
        """
        text = """
            <div class="wrapper">
                <div class="container" href="google">
                    <span>
                        <a class="link" href="search">Welcome</a>
                    </span>
                </div>
            </div>
        """
        bs = to_bs(text)
        tag = DescendantCombinator(
            TagSelector(
                tag="div",
                attributes=[AttributeSelector(name="class", value="container")],
            ),
            TagSelector(tag="a"),
        )
        result = tag.find(bs)
        assert str(result) == strip("""<a class="link" href="search">Welcome</a>""")

    def test_finds_for_multiple_options_with_soup_union_tag(self):
        """
        Tests if DescendantCombinator find_all method returns matching elements if they
        match any of tags that are part of SoupUnionTag at any step.
        """
        text = """
            <div class="wrapper">
                <a class="link">Welcome</a>
            </div>
            <div>
                <a class="link">Welcome</a>
            </div>
            <div class="container">
                <a class="link">Goodbye</a>
            </div>
            <div class="wrapper">
                <a class="wrong_link">Welcome</a>
            </div>
            <div class="container">
                <a class="funhub">See you</a>
            </div>
        """
        bs = to_bs(text)
        tag = DescendantCombinator(
            SelectorList(
                TagSelector(
                    tag="div",
                    attributes=[AttributeSelector(name="class", value="container")],
                ),
                TagSelector(
                    tag="div",
                    attributes=[AttributeSelector(name="class", value="wrapper")],
                ),
            ),
            SelectorList(
                TagSelector(
                    tag="a",
                    attributes=[AttributeSelector(name="class", value="link")],
                ),
                TagSelector(
                    tag="a",
                    attributes=[AttributeSelector(name="class", value="funhub")],
                ),
            ),
        )
        results = tag.find_all(bs)
        expected = {
            strip("""<a class="link">Welcome</a>"""),
            strip("""<a class="link">Goodbye</a>"""),
            strip("""<a class="funhub">See you</a>"""),
        }
        # order is different in case of SoupUnionTag
        assert set(map(str, results)) == expected

    def test_finds_element_for_more_than_two_steps(self):
        """
        Tests if DescendantCombinator find method returns matching elements if there are
        more than two tags are in steps.
        """
        text = """
            <div class="wrapper">
                <div class="container" href="google">
                    <span id="funhub_link">
                        <a class="link" href="funhub.com">Welcome</a>
                    </span>
                </div>
            </div>
        """
        bs = to_bs(text)
        tag = DescendantCombinator(
            TagSelector(
                tag="div",
                attributes=[AttributeSelector(name="class", value="container")],
            ),
            TagSelector(
                tag="span",
                attributes=[AttributeSelector(name="id", value="funhub_link")],
            ),
            TagSelector(tag="a"),
        )
        result = tag.find(bs)
        assert str(result) == strip("""<a class="link" href="funhub.com">Welcome</a>""")

    def test_find_all_handles_multiple_different_levels_of_elements(self):
        """
        Tests if DescendantCombinator find_all method returns matching elements
        if there are at different depth levels.
        """
        text = """
            <div class="wrapper">
                <div class="container" href="google">
                    <span class="funhub_link">
                        <a class="link" href="funhub.com">Welcome</a>
                    </span>
                </div>
            </div>
            <div class="container" href="google">
                <span class="funhub_link">
                    <a class="link" href="funhub.com">Goodbye</a>
                </span>
            </div>
            <span class="funhub_link">
                <a class="link" href="funhub.com">See you</a>
            </span>
        """
        bs = to_bs(text)
        tag = DescendantCombinator(
            TagSelector(
                tag="span",
                attributes=[AttributeSelector(name="class", value="funhub_link")],
            ),
            TagSelector(
                tag="a", attributes=[AttributeSelector(name="class", value="link")]
            ),
        )
        results = tag.find_all(bs)
        expected = [
            strip("""<a class="link" href="funhub.com">Welcome</a>"""),
            strip("""<a class="link" href="funhub.com">Goodbye</a>"""),
            strip("""<a class="link" href="funhub.com">See you</a>"""),
        ]
        assert list(map(str, results)) == expected

    def test_find_all_returns_list_of_matched_elements(self):
        """
        Tests if DescendantCombinator find_all method returns
        a list of all matched elements.
        """
        text = """
            <div class="container" href="google">
                <a class="link" href="search">Welcome here</a>
            </div>
            <div class="wrapper">
                <a class="funhub" href="search">Goodbye</a>
            </div>
            <div>
                <a class="link" href="search">Welcome there</a>
            </div>
            <span class="wrapper">
                <a class="link" href="search">Goodbye</a>
            </span>
            <div class="wrapper">
                <a class="link" href="search">Goodbye</a>
            </div>
            <div>
                <span class="link">Goodbye</span>
            </div>
        """
        bs = to_bs(text)
        tag = DescendantCombinator(
            TagSelector("div"),
            TagSelector(
                "a", attributes=[AttributeSelector(name="class", value="link")]
            ),
        )
        results = tag.find_all(bs)
        expected = [
            strip("""<a class="link" href="search">Welcome here</a>"""),
            strip("""<a class="link" href="search">Welcome there</a>"""),
            strip("""<a class="link" href="search">Goodbye</a>"""),
        ]
        assert list(map(str, results)) == expected

    def test_find_all_returns_empty_list_if_no_matched_elements(self):
        """
        Tests if DescendantCombinator find_all method returns empty list if
        no element matches the tag.
        """
        text = """
            <span class="container">
                <a class="link" href="search">Welcome here</a>
            </span>
            <div>
                <a class="funhub" href="search">Welcome there</a>
            </div>
            <div class="wrapper">
                <span class="link"Goodbye</span>
            </div>
        """
        bs = to_bs(text)
        tag = DescendantCombinator(
            TagSelector("div"),
            TagSelector(
                "a", attributes=[AttributeSelector(name="class", value="link")]
            ),
        )
        results = tag.find_all(bs)
        assert results == []

    def test_find_element_with_nested_steps_elements(self):
        """
        Tests if DescendantCombinator can take another DescendantCombinator as a step
        and find element that matches.
        """
        text = """
            <span class="container">
                <a class="link" href="search">Welcome here</a>
            </span>
            <div>
                <a class="funhub" href="search">
                    <span>Welcome there</span>
                </a>
            </div>
            <div class="wrapper">
                <a class="funhub" href="search"></a>
            </div>
        """
        bs = to_bs(text)
        tag = DescendantCombinator(
            DescendantCombinator(
                TagSelector("div"),
                TagSelector(
                    "a", attributes=[AttributeSelector(name="class", value="funhub")]
                ),
            ),
            TagSelector("span"),
        )
        result = tag.find(bs)
        assert str(result) == strip("""<span>Welcome there</span>""")

    def test_find_skips_elements_partially_matching_steps(self):
        """
        Tests if DescendantCombinator find method skips elements that partially match
        the steps and returns the first element that matches all steps.
        In this case first tag matches only first step,
        but second tag matches both steps.
        """
        text = """
            <div class="container" href="google">
                <a class="link" href="search">Welcome</a>
            </div>
            <div class="container" href="google">
                <span class="link" href="search">Welcome</span>
            </div>
        """
        bs = to_bs(text)
        tag = DescendantCombinator(TagSelector(tag="div"), TagSelector(tag="span"))
        result = tag.find(bs)

        expected = """<span class="link" href="search">Welcome</span>"""
        assert str(result) == strip(expected)

    def test_returns_empty_list_if_first_step_was_not_matched(self):
        """
        Tests if DescendantCombinator find_all method returns an empty list
        if the first step was not matched.
        """
        text = """
            <div class="container" href="google">
                <a class="link" href="search">Welcome</a>
            </div>
        """
        bs = to_bs(text)
        tag = DescendantCombinator(TagSelector(tag="span"), TagSelector(tag="a"))
        result = tag.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        In this case only last tag matches the selector and it child of body.
        """
        text = """
            <span>
                <div><a>Hello 1</a></div>
            </span>
            <div class="google"></div>
            <a href="github">Hello 2</a>
            <div>
                <a>Hello 1</a>
                <span>Hello</span>
            </div>
        """
        bs = find_body_element(to_bs(text))
        tag = DescendantCombinator(
            TagSelector("div"),
            TagSelector("a"),
        )
        result = tag.find(bs, recursive=False)
        assert str(result) == strip("""<a>Hello 1</a>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <span>
                <div><a>Hello 1</a></div>
            </span>
            <div class="google"></div>
            <a href="github">Hello 2</a>
        """
        bs = find_body_element(to_bs(text))
        tag = DescendantCombinator(
            TagSelector("div"),
            TagSelector("a"),
        )
        result = tag.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <span>
                <div><a>Hello 1</a></div>
            </span>
            <div class="google"></div>
            <a href="github">Hello 2</a>
        """
        bs = find_body_element(to_bs(text))
        tag = DescendantCombinator(
            TagSelector("div"),
            TagSelector("a"),
        )

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True, recursive=False)

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <span>
                <div><a>Hello 1</a></div>
            </span>
            <div class="google"></div>
            <div><a>Hello 1</a></div>
            <a href="github">Hello 2</a>
            <div><a>Hello 2</a></div>
        """
        bs = find_body_element(to_bs(text))
        tag = DescendantCombinator(
            TagSelector("div"),
            TagSelector("a"),
        )
        results = tag.find_all(bs, recursive=False)

        assert list(map(str, results)) == [
            strip("""<a>Hello 1</a>"""),
            strip("""<a>Hello 2</a>"""),
        ]

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self,
    ):
        """
        Tests if find_all returns an empty list if no child element matches the selector
        and recursive is False.
        """
        text = """
            <span>
                <div><a>Hello 1</a></div>
            </span>
            <div class="google"></div>
            <a href="github">Hello 2</a>
        """
        bs = find_body_element(to_bs(text))
        tag = DescendantCombinator(
            TagSelector("div"),
            TagSelector("a"),
        )

        results = tag.find_all(bs, recursive=False)
        assert results == []

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <a></a>
            <span>
                <div><a>Hello 1</a></div>
            </span>
            <div>Hello</div>
            <div><a>Hello 2</a></div>
            <div><a>Hello 3</a></div>
            <div><a>Hello 4</a></div>
        """
        bs = find_body_element(to_bs(text))
        tag = DescendantCombinator(
            TagSelector("div"),
            TagSelector("a"),
        )
        results = tag.find_all(bs, limit=2)

        assert list(map(str, results)) == [
            strip("""<a>Hello 1</a>"""),
            strip("""<a>Hello 2</a>"""),
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
            <a></a>
            <span>
                <div><a>Hello 1</a></div>
            </span>
            <div>Hello</div>
            <div><a>Hello 2</a></div>
            <div><a>Hello 3</a></div>
            <div><a>Hello 4</a></div>
        """
        bs = find_body_element(to_bs(text))
        tag = DescendantCombinator(
            TagSelector("div"),
            TagSelector("a"),
        )
        results = tag.find_all(bs, recursive=False, limit=2)

        assert list(map(str, results)) == [
            strip("""<a>Hello 2</a>"""),
            strip("""<a>Hello 3</a>"""),
        ]

    def test_find_steps_after_first_are_always_recursive(self):
        """
        Tests if find recursive is only specified for first step,
        next steps are always recursive.
        """
        text = """
            <div>
                <span>
                    <div class="soo_deep_down">
                        <span>
                            <a>Hello 1</a>
                        </span>
                    </div>
                </span>
            </div>
        """
        bs = find_body_element(to_bs(text))
        tag = DescendantCombinator(
            TagSelector("div"),
            TagSelector("div"),
            TagSelector("a"),
        )
        result = tag.find(bs, recursive=False)
        assert str(result) == strip("""<a>Hello 1</a>""")
