"""Testing module for TagSelector class."""

import re

import pytest

import soupsavvy.tags.namespace as ns
from soupsavvy.tags.components import AnyTagSelector, AttributeSelector, TagSelector
from soupsavvy.tags.exceptions import TagNotFoundException
from tests.soupsavvy.tags.conftest import (
    MockLinkSelector,
    find_body_element,
    strip,
    to_bs,
)


@pytest.mark.soup
class TestTagSelector:
    """
    Class for TagSelector unit test suite.
    Idea behind these tests is to check find_all for more complex variations
    of TagSelector and test basic functionality and behavior with simpler instances.
    """

    def test_find_all_returns_all_tags_for_empty_selector(self):
        """Tests if find_all method returns all tags if selector is empty."""
        text = """
            <div href="github">1</div>
            <a><p>23</p></a>
            <a class="widget">4</a>
        """
        bs = find_body_element(to_bs(text))
        selector = TagSelector()
        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div href="github">1</div>"""),
            strip("""<a><p>23</p></a>"""),
            strip("""<p>23</p>"""),
            strip("""<a class="widget">4</a>"""),
        ]

    def test_find_all_returns_all_matching_tags_for_selector_with_tag_name(self):
        """
        Tests if find_all method returns all matching tags if selector has tag name.
        """
        text = """
            <div href="github"></div>
            <a class="widget">1</a>
            <a><p>2</p></a>
            <span>
                <a>3</a>
            </span>
        """
        bs = to_bs(text)
        selector = TagSelector(tag="a")
        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="widget">1</a>"""),
            strip("""<a><p>2</p></a>"""),
            strip("""<a>3</a>"""),
        ]

    def test_find_all_returns_all_matching_tags_for_selector_with_attributes(
        self,
    ):
        """
        Tests if find_all method returns all matching tags if selector has attributes
        without tag name.
        """
        text = """
            <div class="widget" href="github">1</div>
            <a class="widget123" href="github">Hello</a>
            <span class="widget"></span>
            <a class="widget" href="github123">Hello</a>
            <div href="github"></div>
            <a class="widget" href="github"><p>2</p></a>
            <span>
                <a id="widget" class="github"></a>
                <a class="widget" href="github" rel="help">3</a>
            </span>
        """
        bs = to_bs(text)
        selector = TagSelector(
            attributes=[
                AttributeSelector(name="class", value="widget"),
                AttributeSelector(name="href", value="github"),
            ],
        )
        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div class="widget" href="github">1</div>"""),
            strip("""<a class="widget" href="github"><p>2</p></a>"""),
            strip("""<a class="widget" href="github" rel="help">3</a>"""),
        ]

    def test_find_all_returns_all_matching_tags_for_selector_with_tag_name_and_attribute(
        self,
    ):
        """
        Tests if find_all method returns all matching tags if selector has tag name
        and one attribute selector.
        """
        text = """
            <div href="github"></div>
            <a class="widget123">Hello</a>
            <div class="widget"></div>
            <a class="widget">1</a>
            <a href="widget"><p></p></a>
            <a class="widget"><p>2</p></a>
            <span>
                <a id="widget" class="github"></a>
                <a class="widget">3</a>
            </span>
        """
        bs = to_bs(text)
        selector = TagSelector(
            tag="a",
            attributes=[
                AttributeSelector(name="class", value="widget"),
            ],
        )
        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="widget">1</a>"""),
            strip("""<a class="widget"><p>2</p></a>"""),
            strip("""<a class="widget">3</a>"""),
        ]

    def test_find_all_returns_all_matching_tags_for_selector_with_tag_name_and_multiple_attributes(
        self,
    ):
        """
        Tests if find method returns first matching tag if selector has tag name
        and one attribute selector.
        """
        text = """
            <div class="widget" href="github" target="_blank"></div>
            <a class="widget" href="github" target="_parent">Hello</a>
            <div class="widget"></div>
            <a class="widget" href="github" target="_blank">1</a>
            <a class="widget123" href="github" target="_blank">Hello</a>
            <a class="widget" href="facebook" target="_blank">Hello</a>
            <a class="widget">World</a>
            <a class="widget" href="github" rel="author" target="_blank"><p>2</p></a>
            <a class="widget"><p>2</p></a>
            <span>
                <a id="widget" href="github" target="_blank"></a>
                <a class="widget" href="github123" target="_blank">3</a>
            </span>
        """
        bs = to_bs(text)
        selector = TagSelector(
            tag="a",
            attributes=[
                AttributeSelector(name="class", value="widget"),
                AttributeSelector(name="href", value="github", re=True),
                AttributeSelector(name="target", value="_blank"),
            ],
        )
        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="widget" href="github" target="_blank">1</a>"""),
            strip(
                """<a class="widget" href="github" rel="author" target="_blank"><p>2</p></a>"""
            ),
            strip("""<a class="widget" href="github123" target="_blank">3</a>"""),
        ]

    def test_find_returns_first_tag_matching_selector(self):
        """Tests if find method returns first tag matching selector."""
        text = """
            <div href="github"></div>
            <a class="widget">1</a>
            <a><p>2</p></a>
            <span>
                <a>3</a>
            </span>
        """
        bs = to_bs(text)
        selector = TagSelector(tag="a")
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<a class="widget">1</a>""")

    def test_find_returns_none_if_no_match_and_strict_false(self):
        """
        Tests if find returns None if no element matches the selector
        and strict is False.
        """
        text = """
            <div href="github"></div>
            <span class="widget"></span>
            <div><p>Hello</p></div>
            <span>
                <div>Hello</div>
            </span>
        """
        bs = to_bs(text)
        selector = TagSelector(tag="a")
        result = selector.find(bs)
        assert result is None

    def test_find_raises_exception_if_no_match_and_strict_true(self):
        """
        Tests if find raises TagNotFoundException if no element matches the selector
        and strict is True.
        """
        text = """
            <div href="github"></div>
            <span class="widget"></span>
            <div><p>Hello</p></div>
            <span>
                <div>Hello</div>
            </span>
        """
        bs = to_bs(text)
        selector = TagSelector(tag="a")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_all_returns_empty_list_when_no_match(self):
        """Tests if find returns an empty list if no element matches the selector."""
        text = """
            <div href="github"></div>
            <span class="widget"></span>
            <div><p>Hello</p></div>
            <span>
                <div>Hello</div>
            </span>
        """
        bs = to_bs(text)
        selector = TagSelector(tag="a")
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <div class="google">
                <a href="github">Not child</a>
            </div>
            <a href="github">1</a>
            <div><a>Not child</a></div>
            <a><p>2</p></a>
            <span>Hello</span>
            <a>3</a>
        """
        bs = find_body_element(to_bs(text))
        selector = TagSelector(tag="a")
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<a href="github">1</a>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div class="google">
                <a href="github">Not child</a>
            </div>
            <div><a>Not child</a></div>
            <span>Hello</span>
        """
        bs = find_body_element(to_bs(text))
        selector = TagSelector(tag="a")
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <div class="google">
                <a href="github">Not child</a>
            </div>
            <div><a>Not child</a></div>
            <span>Hello</span>
        """
        bs = find_body_element(to_bs(text))
        selector = TagSelector(tag="a")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <div class="google">
                <a href="github">Not child</a>
            </div>
            <a href="github">1</a>
            <div><a>Not child</a></div>
            <a><p>2</p></a>
            <span>Hello</span>
            <a>3</a>
        """
        bs = find_body_element(to_bs(text))
        selector = TagSelector(tag="a")
        result = selector.find_all(bs, recursive=False)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a href="github">1</a>"""),
            strip("""<a><p>2</p></a>"""),
            strip("""<a>3</a>"""),
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
                <a href="github">Not child</a>
            </div>
            <div><a>Not child</a></div>
            <span>Hello</span>
        """
        bs = find_body_element(to_bs(text))
        selector = TagSelector(tag="a")
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <div href="github"></div>
            <a class="widget">1</a>
            <a><p>2</p></a>
            <span>
                <a>3</a>
            </span>
        """
        bs = find_body_element(to_bs(text))
        selector = TagSelector(tag="a")
        result = selector.find_all(bs, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="widget">1</a>"""),
            strip("""<a><p>2</p></a>"""),
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
            <div class="google">
                <a href="github">Not child</a>
            </div>
            <a href="github">1</a>
            <div><a>Not child</a></div>
            <a><p>2</p></a>
            <span>Hello</span>
            <a>3</a>
        """
        bs = find_body_element(to_bs(text))
        selector = TagSelector(tag="a")
        result = selector.find_all(bs, recursive=False, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a href="github">1</a>"""),
            strip("""<a><p>2</p></a>"""),
        ]

    @pytest.mark.css_selector
    @pytest.mark.parametrize(
        argnames="tag, selector",
        argvalues=[
            (
                TagSelector(attributes=[AttributeSelector("class", value="menu")]),
                "[class='menu']",
            ),
            (
                TagSelector(
                    attributes=[
                        AttributeSelector("class", value="menu"),
                        AttributeSelector("id", value="menu_2"),
                    ]
                ),
                "[class='menu'][id='menu_2']",
            ),
            (
                TagSelector(
                    tag="div",
                    attributes=[
                        AttributeSelector("class", value="menu"),
                        AttributeSelector("id", value="menu_2"),
                    ],
                ),
                "div[class='menu'][id='menu_2']",
            ),
            (
                TagSelector(
                    tag="a",
                    attributes=[
                        AttributeSelector("class", value="menu", re=True),
                        AttributeSelector("awesomeness", value="3", re=False),
                    ],
                ),
                "a[class*='menu'][awesomeness='3']",
            ),
            (
                TagSelector(
                    tag="a",
                    attributes=[
                        AttributeSelector("class", value="menu"),
                        AttributeSelector("class", value="menu"),
                    ],
                ),
                "a[class='menu']",
            ),
            (TagSelector(tag="a", attributes=[AttributeSelector("class")]), "a[class]"),
            (TagSelector(), ns.CSS_SELECTOR_WILDCARD),
            (
                TagSelector(
                    tag="a",
                    attributes=[AttributeSelector("class", value="widget menu")],
                ),
                "a[class='widget menu']",
            ),
        ],
    )
    def test_selector_is_correct(self, tag: TagSelector, selector: str):
        """Tests if css selector for TagSelector is constructed as expected."""
        assert tag.selector == selector

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            # tags must be equal
            (TagSelector("a"), TagSelector("a")),
            # tags and attributes must be equal
            (
                TagSelector(
                    "a", attributes=[AttributeSelector("class", value="widget")]
                ),
                TagSelector(
                    "a", attributes=[AttributeSelector("class", value="widget")]
                ),
            ),
            # self.attributes must be equal to other.attributes
            (
                TagSelector(
                    attributes=[
                        AttributeSelector("class", value="widget"),
                        AttributeSelector("id", value="footnote", re=True),
                    ]
                ),
                TagSelector(
                    attributes=[
                        AttributeSelector("class", value="widget"),
                        AttributeSelector("id", value=re.compile("footnote")),
                    ]
                ),
            ),
            # empty TagSelectors and AnyTagSelectors are equal
            (TagSelector(), AnyTagSelector()),
        ],
    )
    def test_two_tag_selectors_are_equal(
        self, selectors: tuple[TagSelector, TagSelector]
    ):
        """Tests if two TagSelectors are equal."""
        assert (selectors[0] == selectors[1]) is True

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            # tags are different
            (TagSelector("a"), TagSelector("div")),
            # not TagSelector instance
            (TagSelector("a"), MockLinkSelector()),
            # attributes in wrong order
            (
                TagSelector(
                    "a",
                    attributes=[
                        AttributeSelector("class", value="widget"),
                        AttributeSelector("id", value="menu"),
                    ],
                ),
                TagSelector(
                    "a",
                    attributes=[
                        AttributeSelector("id", value="menu"),
                        AttributeSelector("class", value="widget"),
                    ],
                ),
            ),
            # one attribute is different
            (
                TagSelector(
                    attributes=[
                        AttributeSelector("class", value="widget"),
                        AttributeSelector("id", value="menu"),
                    ]
                ),
                TagSelector(
                    attributes=[
                        AttributeSelector("class", value="widget"),
                        AttributeSelector("id", value="footnote"),
                    ]
                ),
            ),
        ],
    )
    def test_two_tag_selectors_are_not_equal(
        self, selectors: tuple[TagSelector, TagSelector]
    ):
        """Tests if two TagSelectors are not equal."""
        assert (selectors[0] == selectors[1]) is False

    @pytest.mark.edge_case
    def test_do_not_shadow_bs4_find_method_parameters(self):
        """
        Tests that find method does not shadow bs4.Tag find method parameters.
        If attribute name is the same as bs4.Tag find method parameter
        like ex. 'string' or 'name' it should not cause any conflicts.
        The way to avoid it is to pass attribute filters as a dictionary to 'attrs'
        parameter in bs4.Tag find method instead of as keyword arguments.
        """
        text = """
            <div string="Hello"></div>
            <div href="github" class="menu"></div>
            <a class="github"></a>
            <div name="github">Hello</div>
            <github string="Hello"></github>
            <div name="github"></div>
            <span name="github" string="Hello"></span>
            <div name="github" string="Hello">1</div>
            <a name="github" string="Hello"></a>
            <div name="github" string="Hello">2</div>
        """
        bs = to_bs(text)
        tag = TagSelector(
            "div",
            attributes=[
                AttributeSelector("name", "github"),
                AttributeSelector("string"),
            ],
        )
        result = tag.find(bs)
        assert strip(str(result)) == strip(
            """<div name="github" string="Hello">1</div>"""
        )
