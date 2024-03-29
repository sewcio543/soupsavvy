"""Testing module for StepsElementTag class."""

import pytest

from soupsavvy.tags.base import SoupUnionTag
from soupsavvy.tags.components import (
    AnyTag,
    AttributeTag,
    ElementTag,
    PatternElementTag,
    StepsElementTag,
)
from soupsavvy.tags.exceptions import NotSelectableSoupException, TagNotFoundException

from .conftest import strip, to_bs


@pytest.mark.soup
class TestStepsElementTag:
    """Class for StepsElementTag unit test suite."""

    def test_not_selectablesoup_in_init_raises_exception(self):
        """
        Tests if NotSelectableSoupException is raised when one of input parameters
        is not a SelectableSoup object.
        """
        with pytest.raises(NotSelectableSoupException):
            StepsElementTag(ElementTag(tag="div"), "string")  # type: ignore

    @pytest.mark.parametrize(
        argnames="tag",
        argvalues=[
            StepsElementTag(ElementTag(tag="div"), ElementTag(tag="a")),
            StepsElementTag(
                ElementTag(
                    tag="div",
                    attributes=[AttributeTag(name="class", value="container")],
                ),
                ElementTag(
                    tag="a", attributes=[AttributeTag(name="href", value="search")]
                ),
            ),
            StepsElementTag(ElementTag(tag="div"), AnyTag()),
            StepsElementTag(AttributeTag(name="href", value="google"), ElementTag("a")),
            StepsElementTag(
                ElementTag(tag="div"),
                PatternElementTag(tag=ElementTag("a"), pattern="Welcome"),
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
    def test_element_is_found_for_valid_steps_elements(self, tag: StepsElementTag):
        """
        Tests if element was found for various valid StepsElementTag.
        Element is returned if it matches multistep tags.
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
            StepsElementTag(ElementTag(tag="div"), ElementTag(tag="span")),
            StepsElementTag(ElementTag(tag="footer"), ElementTag(tag="a")),
            StepsElementTag(
                ElementTag(
                    tag="div",
                    attributes=[AttributeTag(name="class", value="container")],
                ),
                ElementTag(
                    tag="a", attributes=[AttributeTag(name="href", value="funhub.com")]
                ),
            ),
            StepsElementTag(
                AttributeTag(name="href", value="funhub.com"), ElementTag("a")
            ),
            StepsElementTag(
                ElementTag(tag="div"),
                PatternElementTag(tag=ElementTag("a"), pattern="Goodbye"),
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
        self, tag: StepsElementTag
    ):
        """
        Tests if element was not found for various invalid StepsElementTag
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
        tag = StepsElementTag(ElementTag(tag="div"), ElementTag(tag="span"))

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True)

    def test_finds_nested_elements_that_are_not_direct_children(self):
        """
        Tests if StepsElementTag find method returns matching elements if they
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
        tag = StepsElementTag(
            ElementTag(
                tag="div", attributes=[AttributeTag(name="class", value="container")]
            ),
            ElementTag(tag="a"),
        )
        result = tag.find(bs)
        assert str(result) == strip("""<a class="link" href="search">Welcome</a>""")

    def test_finds_for_multiple_options_with_soup_union_tag(self):
        """
        Tests if StepsElementTag find_all method returns matching elements if they
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
        tag = StepsElementTag(
            SoupUnionTag(
                ElementTag(
                    tag="div",
                    attributes=[AttributeTag(name="class", value="container")],
                ),
                ElementTag(
                    tag="div",
                    attributes=[AttributeTag(name="class", value="wrapper")],
                ),
            ),
            SoupUnionTag(
                ElementTag(
                    tag="a",
                    attributes=[AttributeTag(name="class", value="link")],
                ),
                ElementTag(
                    tag="a",
                    attributes=[AttributeTag(name="class", value="funhub")],
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
        Tests if StepsElementTag find method returns matching elements if there are
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
        tag = StepsElementTag(
            ElementTag(
                tag="div", attributes=[AttributeTag(name="class", value="container")]
            ),
            ElementTag(
                tag="span", attributes=[AttributeTag(name="id", value="funhub_link")]
            ),
            ElementTag(tag="a"),
        )
        result = tag.find(bs)
        assert str(result) == strip("""<a class="link" href="funhub.com">Welcome</a>""")

    def test_find_all_handles_multiple_different_levels_of_elements(self):
        """
        Tests if StepsElementTag find_all method returns matching elements
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
        tag = StepsElementTag(
            ElementTag(
                tag="span", attributes=[AttributeTag(name="class", value="funhub_link")]
            ),
            ElementTag(tag="a", attributes=[AttributeTag(name="class", value="link")]),
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
        Tests if StepsElementTag find_all method returns
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
        tag = StepsElementTag(
            ElementTag("div"),
            ElementTag("a", attributes=[AttributeTag(name="class", value="link")]),
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
        Tests if StepsElementTag find_all method returns empty list if
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
        tag = StepsElementTag(
            ElementTag("div"),
            ElementTag("a", attributes=[AttributeTag(name="class", value="link")]),
        )
        results = tag.find_all(bs)
        assert isinstance(results, list)
        assert len(results) == 0

    def test_find_element_with_nested_steps_elements(self):
        """
        Tests if StepsElementTag can take another StepsElementTag as a step
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
        tag = StepsElementTag(
            StepsElementTag(
                ElementTag("div"),
                ElementTag(
                    "a", attributes=[AttributeTag(name="class", value="funhub")]
                ),
            ),
            ElementTag("span"),
        )
        result = tag.find(bs)
        assert str(result) == strip("""<span>Welcome there</span>""")
