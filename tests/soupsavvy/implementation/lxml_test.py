"""
Module with unit tests for lxml implementation of IElement.
Tests `LXMLElement` component and the way it interacts with soupsavvy.
"""

import re

import pytest
from bs4 import BeautifulSoup
from lxml.etree import _Element as HtmlElement
from lxml.etree import fromstring, tostring

from soupsavvy.implementation.lxml import LXMLElement
from soupsavvy.selectors.css.api import CSSSelectApi
from soupsavvy.selectors.xpath.api import LXMLXpathApi
from tests.soupsavvy.conftest import strip


def to_lxml(html: str) -> HtmlElement:
    bs = BeautifulSoup(html, features="lxml")
    return fromstring(str(bs))


@pytest.mark.lxml
@pytest.mark.implementation
class TestLXMLElement:
    """Class with unit tests for `LXMLElement` component."""

    def test_raises_exception_when_invalid_init_node(self):
        """
        Tests if TypeError is raised when object of invalid type
        is passed to constructor.
        """
        text = """
            <div>Hello</div>
            <p>World</p>
        """

        with pytest.raises(TypeError):
            LXMLElement(text)  # type: ignore

    def test_node_is_wrapped_by_element(self):
        """
        Tests if node passed to constructor is wrapped by element and can be accessed
        with `node` attribute or `get` method. This should be the same object.
        """
        text = """
            <div>Hello</div>
            <p>World</p>
        """
        node = to_lxml(text)
        element = LXMLElement(node)

        assert element.node is node
        assert element.get() is node

    def test_can_be_constructed_with_from_node_class_method(self):
        """
        Tests if element can be constructed with `from_node` class method.
        This achieves the same result as init method.
        """
        text = """
            <div>Hello</div>
            <p>World</p>
        """
        node = to_lxml(text)
        element = LXMLElement.from_node(node)

        assert element.node is node
        assert element.get() is node

    def test_str_and_repr_are_correct(self):
        """
        Tests if `str` and `repr` methods return correct values.
        Repr should be a string with class name and wrapped node repr.
        str is constructed with `tostring` method from `lxml.etree` module
        with specific parameters.
        """
        text = """
            <div>Hello</div>
            <p>World</p>
        """
        node = to_lxml(text)
        element = LXMLElement(node)

        assert str(element) == tostring(node, method="html", with_tail=False).decode(
            "utf-8"
        )
        assert repr(element) == f"LXMLElement({node!r})"

    def test_hashes_of_two_elements_with_same_node_are_equal(self):
        """
        Tests if hashes of two elements with the same node are equal.
        In lxml, hash is equal to the hash of the wrapped node element.
        """
        text = """
            <div>Hello</div>
            <p>World</p>
        """
        node = to_lxml(text)

        node1 = node.find(".//div")
        node2 = node.find(".//div")
        node3 = node.find(".//p")

        assert node1 is not None
        assert node2 is not None
        assert node3 is not None

        element1 = LXMLElement(node1)
        element2 = LXMLElement(node2)
        element3 = LXMLElement(node3)

        assert hash(element1) == hash(element1)
        assert hash(element1) == hash(element2)
        assert hash(element1) != hash(element3)
        assert hash(element1) != hash(node1)

    def test_equality_is_implemented_correctly(self):
        """
        Tests if only two element objects with the same wrapped node element are equal,
        even when they are results of different searches.
        """
        text = """
            <div><p>Hello</p></div>
        """
        node = to_lxml(text)

        node1 = node.find(".//div")
        node2 = node.find(".//div")
        node3 = node.find(".//p")

        assert node1 is not None
        assert node2 is not None
        assert node3 is not None

        element1 = LXMLElement(node1)
        element2 = LXMLElement(node2)
        element3 = LXMLElement(node3)

        assert element1 == element1
        assert element1 == element2
        assert element1 != element3
        assert element1 != node1

    def test_equality_check_returns_not_implemented(self):
        """Tests if equality check returns NotImplemented for non comparable types."""
        text = """
            <div><p>Hello</p></div>
        """
        node = to_lxml(text)
        element = LXMLElement(node)

        assert element.__eq__(node) is NotImplemented
        assert element.__eq__("string") is NotImplemented

    def test_name_attribute_has_correct_value(self):
        """Tests if `name` attribute returns name of the node element."""
        text = """
            <div>Hello</div>
            <p>World</p>
        """
        node = to_lxml(text).find(".//div")
        assert node is not None

        element = LXMLElement(node)
        assert element.name == "div"

    @pytest.mark.parametrize(
        argnames="text, expected",
        argvalues=[
            ("<div>Hello</div>", "Hello"),
            ("<div> Hello\n</div>", " Hello\n"),
            ("<div>Hello<p>World</p> </div>", "HelloWorld "),
            ("Before<div>Hello<p>World</p>.</div>After", "HelloWorld."),
        ],
    )
    def test_text_return_expected_value(self, text: str, expected: str):
        """
        Tests if `text` property returns expected value.
        It joins text form text nodes in the lxml element.
        """
        node = to_lxml(text).find(".//div")
        assert node is not None

        element = LXMLElement(node)
        assert element.text == expected

    def test_children_returns_iterator_of_child_elements_in_order(self):
        """
        Tests if `children` property returns iterator of child elements
        in order they appear in the document.
        """
        text = """
            <div>
                <p>Hello</p>
                <p>World</p>
                <span><p>Hi</p><a>Earth</a></span>
            </div>
        """
        node = to_lxml(text).find(".//div")
        assert node is not None

        element = LXMLElement(node)
        children = list(element.children)

        assert all(isinstance(child, LXMLElement) for child in children)
        assert [strip(str(child)) for child in children] == [
            "<p>Hello</p>",
            "<p>World</p>",
            "<span><p>Hi</p><a>Earth</a></span>",
        ]

    def test_children_returns_empty_iterator_if_no_children_of_element(self):
        """
        Tests if `children` property returns empty iterator if element has no children.
        Text node are not included in children.
        """
        text = """
            <div>Hello</div>
        """
        node = to_lxml(text).find(".//div")
        assert node is not None

        element = LXMLElement(node)
        children = list(element.children)

        assert children == []

    def test_descendants_returns_iterator_of_descendant_elements_in_order(self):
        """
        Tests if `descendants` property returns iterator of descendant elements
        in order they appear in the document using depth-first iteration.
        """
        text = """
            <div>
                <p>Hello</p>
                <p>World</p>
                <span><span><h1>Hi</h1><h2>Hi</h2></span><a>Earth</a></span>
            </div>
        """
        node = to_lxml(text).find(".//div")
        assert node is not None

        element = LXMLElement(node)
        descendants = list(element.descendants)

        assert all(isinstance(child, LXMLElement) for child in descendants)
        assert [strip(str(child)) for child in descendants] == [
            "<p>Hello</p>",
            "<p>World</p>",
            "<span><span><h1>Hi</h1><h2>Hi</h2></span><a>Earth</a></span>",
            "<span><h1>Hi</h1><h2>Hi</h2></span>",
            "<h1>Hi</h1>",
            "<h2>Hi</h2>",
            "<a>Earth</a>",
        ]

    def test_descendants_returns_empty_iterator_if_no_descendants_of_element(self):
        """
        Tests if `descendants` property returns empty iterator
        if element has no descendants.
        """
        text = """
            <div>Hello</div>
        """
        node = to_lxml(text).find(".//div")
        assert node is not None

        element = LXMLElement(node)
        descendants = list(element.descendants)

        assert descendants == []

    def test_parent_return_element_wrapping_soup_parent(self):
        """
        Tests if `parent` property returns new element with parent node
        as the wrapped node.
        """
        text = """
            <div>
                <p>Hello</p>
                <p>World</p>
                <span><p>Hi</p><a>Earth</a></span>
            </div>
        """
        node = to_lxml(text).find(".//div")
        assert node is not None

        element = LXMLElement(node)
        parent = element.parent

        assert isinstance(parent, LXMLElement)
        assert parent.get() is node.getparent()

    def test_parent_return_none_when_root_node(self):
        """Tests if `parent` property returns None if element is root node."""
        text = """
            <div>
                <p>Hello</p>
                <p>World</p>
                <span><p>Hi</p><a>Earth</a></span>
            </div>
        """
        node = to_lxml(text)
        element = LXMLElement(node)
        parent = element.parent

        assert parent is None

    @pytest.mark.integration
    def test_css_api_works_properly(self):
        """
        Tests if `css` method returns `CSSSelectApi` object correctly initialized
        which select elements properly returning list of `LXMLElement` objects.
        """
        text = """
            <div>
                <p class="widget">Hello</p>
                <p class="menu">World</p>
                <span><p>Hi</p><a>Earth</a></span>
            </div>
            <p class="widget">Hi</p>
        """
        node = to_lxml(text)
        element = LXMLElement(node)

        api = element.css("p.widget")
        assert isinstance(api, CSSSelectApi)

        result = api.select(element)
        assert all(isinstance(element, LXMLElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<p class="widget">Hello</p>""",
            """<p class="widget">Hi</p>""",
        ]

    @pytest.mark.integration
    def test_xpath_api_works_properly(self):
        """
        Tests if `xpath` method returns `LXMLXpathApi` object correctly initialized
        which select elements properly returning list of `LXMLElement` objects.
        """
        text = """
            <div>
                <p class="widget">Hello</p>
                <span><span>Hi</span><a>Earth</a></span>
            </div>
            <p class="widget">Hi</p>
        """
        node = to_lxml(text)
        element = LXMLElement(node)

        api = element.xpath(".//p")
        assert isinstance(api, LXMLXpathApi)

        result = api.select(element)
        assert all(isinstance(element, LXMLElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<p class="widget">Hello</p>""",
            """<p class="widget">Hi</p>""",
        ]

    def test_finds_all_ancestors_of_element_in_order(self):
        """
        Tests if `find_ancestors` method returns list of ancestors of element
        starting from parent moving up to the root of the document.
        """
        text = """
            <div>
                <p class="widget">Hello</p>
                <span><p><a>Hello</a></p></span>
            </div>
        """
        node = to_lxml(text).find(".//a")
        assert node is not None

        element = LXMLElement(node)
        ancestors = element.find_ancestors()

        assert all(isinstance(element, LXMLElement) for element in ancestors)
        assert [strip(str(x)) for x in ancestors] == [
            "<p><a>Hello</a></p>",
            "<span><p><a>Hello</a></p></span>",
            """<div><p class="widget">Hello</p><span><p><a>Hello</a></p></span></div>""",
            """<body><div><p class="widget">Hello</p><span><p><a>Hello</a></p></span></div></body>""",
            """<html><body><div><p class="widget">Hello</p><span><p><a>Hello</a></p></span></div></body></html>""",
        ]

    def test_finds_ancestors_with_limit(self):
        """
        Tests if `find_ancestors` method returns ancestors up to the limit.
        No more than `limit` ancestors are returned.
        """
        text = """
            <div>
                <p class="widget">Hello</p>
                <span><p><a>Hello</a></p></span>
            </div>
        """
        node = to_lxml(text).find(".//a")
        assert node is not None

        element = LXMLElement(node)
        ancestors = element.find_ancestors(limit=2)

        assert all(isinstance(element, LXMLElement) for element in ancestors)
        assert [strip(str(x)) for x in ancestors] == [
            "<p><a>Hello</a></p>",
            "<span><p><a>Hello</a></p></span>",
        ]

    def test_find_ancestors_returns_empty_list_if_root_element(self):
        """Tests if `find_ancestors` method returns empty list if element is root."""
        text = """
            <div>
                <p class="widget">Hello</p>
                <span><p><a>Hello</a></p></span>
            </div>
        """
        node = to_lxml(text)

        element = LXMLElement(node)
        assert element.find_ancestors() == []

    def test_finds_all_subsequent_siblings_of_element(self):
        """
        Tests if `find_subsequent_siblings` method returns all subsequent siblings.
        """
        text = """
            <div>
                <p class="widget">Hello</p>
                <span class="anchor">Hello</span>
                <p><a>World</a></p>
                <span>Earth</span>
                <h1>Nice</h1>
            </div>
            <span>Hi</span>
        """
        node = to_lxml(text).find(".//span")
        assert isinstance(node, HtmlElement)

        element = LXMLElement(node)
        siblings = element.find_subsequent_siblings()

        assert all(isinstance(element, LXMLElement) for element in siblings)
        assert [strip(str(x)) for x in siblings] == [
            "<p><a>World</a></p>",
            "<span>Earth</span>",
            "<h1>Nice</h1>",
        ]

    def test_finds_all_subsequent_returns_empty_list_if_last_child(self):
        """
        Tests if `find_subsequent_siblings` method returns empty list
        if element is the last child of the parent.
        """
        text = """
            <div>
                <p class="widget">Hello</p>
                <span class="anchor">Hello</span>
            </div>
            <span>Hi</span>
        """
        node = to_lxml(text).find(".//span")
        assert isinstance(node, HtmlElement)

        element = LXMLElement(node)
        assert element.find_subsequent_siblings() == []

    def test_finds_all_subsequent_with_limit(self):
        """
        Tests if `find_subsequent_siblings` method returns
        all subsequent siblings up to the limit.
        """
        text = """
            <div>
                <p class="widget">Hello</p>
                <span class="anchor">Hello</span>
                <p><a>World</a></p>
                <span>Earth</span>
                <h1>Nice</h1>
            </div>
            <span>Hi</span>
        """
        node = to_lxml(text).find(".//span")
        assert isinstance(node, HtmlElement)

        element = LXMLElement(node)
        siblings = element.find_subsequent_siblings(limit=2)

        assert all(isinstance(element, LXMLElement) for element in siblings)
        assert [strip(str(x)) for x in siblings] == [
            "<p><a>World</a></p>",
            "<span>Earth</span>",
        ]

    def test_finds_all_elements_when_no_specifications(self):
        """
        Tests if `find_all` method returns all descendant elements
        if no specifications are provided.
        """
        text = """
            <div>
                <p class="widget">Hello</p>
                <p><a>World</a></p>
            </div>
            <span>Hi</span>
        """
        node = to_lxml(text).find(".//body")
        assert node is not None

        element = LXMLElement(node)
        result = element.find_all()

        assert all(isinstance(element, LXMLElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<div><p class="widget">Hello</p><p><a>World</a></p></div>""",
            """<p class="widget">Hello</p>""",
            """<p><a>World</a></p>""",
            """<a>World</a>""",
            """<span>Hi</span>""",
        ]

    def test_finds_all_returns_list_of_children_when_recursive_false(self):
        """
        Tests if `find_all` method returns all child elements
        if no specifications are provided and recursive is False.
        """
        text = """
            <div>
                <p class="widget">Hello</p>
                <p><a>World</a></p>
            </div>
            <span>Hi</span>
        """
        node = to_lxml(text).find(".//body")
        assert node is not None

        element = LXMLElement(node)
        result = element.find_all(recursive=False)

        assert all(isinstance(element, LXMLElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<div><p class="widget">Hello</p><p><a>World</a></p></div>""",
            """<span>Hi</span>""",
        ]

    def test_finds_all_elements_with_limit(self):
        """
        Tests if `find_all` method returns all descendant elements up to the limit.
        They appear in the order they are found in the document
        using depth-first search.
        """
        text = """
            <div>
                <p class="widget">Hello</p>
                <p><a>World</a></p>
            </div>
            <span>Hi</span>
        """
        node = to_lxml(text).find(".//body")
        assert node is not None

        element = LXMLElement(node)
        result = element.find_all(limit=3)

        assert all(isinstance(element, LXMLElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<div><p class="widget">Hello</p><p><a>World</a></p></div>""",
            """<p class="widget">Hello</p>""",
            """<p><a>World</a></p>""",
        ]

    def test_finds_all_elements_with_limit_and_recursive_false(self):
        """
        Tests if `find_all` method returns child elements up to the limit
        if recursive is False and limit is set.
        """
        text = """
            <div>
                <p class="widget">Hello</p>
                <span><h1>World</h1></span>
            </div>
            <span>Hi</span>
            <p>Earth</p>
        """
        node = to_lxml(text).find(".//body")
        assert node is not None

        element = LXMLElement(node)
        result = element.find_all(limit=2, recursive=False)

        assert all(isinstance(element, LXMLElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<div><p class="widget">Hello</p><span><h1>World</h1></span></div>""",
            """<span>Hi</span>""",
        ]

    def test_finds_all_returns_empty_list_if_nothing_matches(self):
        """
        Tests if `find_all` method returns empty list if no elements match the criteria.
        """
        text = """
            <div>
                <p class="widget">Hello</p>
                <span><h1>World</h1></span>
            </div>
            <span>Hi</span>
        """
        node = to_lxml(text)
        element = LXMLElement(node)

        result = element.find_all(name="h2")
        assert result == []

    def test_finds_all_returns_empty_list_if_nothing_matches_and_recursive_false(self):
        """
        Tests if `find_all` method returns empty list if no elements match the criteria
        when recursive is False.
        """
        text = """
            <div>
                <p class="widget">Hello</p>
                <span><h2>World</h2></span>
            </div>
            <span>Hi</span>
        """
        node = to_lxml(text)
        element = LXMLElement(node)

        result = element.find_all(name="h2", recursive=False)
        assert result == []

    def test_finds_all_elements_with_specific_name(self):
        """
        Tests if `find_all` method returns all descendant elements with specific name.
        """
        text = """
            <div>
                <p class="widget">Hello</p>
                <p><a>World</a></p>
            </div>
            <span>Hi</span>
        """
        node = to_lxml(text)
        element = LXMLElement(node)
        result = element.find_all(name="p")

        assert all(isinstance(element, LXMLElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<p class="widget">Hello</p>""",
            """<p><a>World</a></p>""",
        ]

    def test_finds_all_elements_with_specific_name_and_recursive_false(self):
        """
        Tests if `find_all` method returns all child elements with specific name
        when recursive is False.
        """
        text = """
            <span>Hi</span>
            <div>
                <span><h1>Earth</h1></span>
                <p class="widget">Hello</p>
                <span>Morning</span>
            </div>
            <span><p>World</p></span>
        """
        node = to_lxml(text).find(".//body")
        assert node is not None

        element = LXMLElement(node)
        result = element.find_all(name="span", recursive=False)

        assert all(isinstance(element, LXMLElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<span>Hi</span>""",
            """<span><p>World</p></span>""",
        ]

    def test_finds_all_elements_with_exact_attribute_match(self):
        """
        Tests if `find_all` method returns all descendant elements
        with specific attribute and value.
        Additionally, if any of element classes == value, it is also returned.
        """
        text = """
            <div>
                <p class="widget">Hello</p>
                <p><a>World</a></p>
            </div>
            <span class="widget">Hi</span>
        """
        node = to_lxml(text)
        element = LXMLElement(node)
        result = element.find_all(attrs={"class": "widget"})

        assert all(isinstance(element, LXMLElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<p class="widget">Hello</p>""",
            """<span class="widget">Hi</span>""",
        ]

    def test_finds_all_elements_with_regex_attribute_match(self):
        """
        Tests if `find_all` method returns all descendant elements
        with specific attribute matching regex pattern.
        """
        text = """
            <div>
                <p class="widget123">Hello</p>
                <span><h1>World</h1></span>
            </div>
            <span class="widget menu">Hi</span>
            <h1 class="widge">Welcome</h1>
            <span class="menu your_widget">Hello</span>
        """
        node = to_lxml(text)
        element = LXMLElement(node)
        result = element.find_all(attrs={"class": re.compile("widget")})

        assert all(isinstance(element, LXMLElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<p class="widget123">Hello</p>""",
            """<span class="widget menu">Hi</span>""",
            """<span class="menu your_widget">Hello</span>""",
        ]

    def test_finds_all_elements_with_matching_multiple_attributes(self):
        """
        Tests if `find_all` method returns all descendant elements
        that match all provided attributes.
        """
        text = """
            <div>
                <p class="widget">Hello</p>
                <span><h1 name="menu">World</h1></span>
            </div>
            <span class="widget" name="navbar">Hi</span>
            <h1 class="widget" name="menu">Welcome</h1>
        """
        node = to_lxml(text)
        element = LXMLElement(node)
        result = element.find_all(attrs={"class": "widget", "name": "menu"})

        assert all(isinstance(element, LXMLElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<h1 class="widget" name="menu">Welcome</h1>"""
        ]

    def test_finds_all_elements_with_matching_attributes_and_name(self):
        """
        Tests if `find_all` method returns all descendant elements
        that match both provided attributes and name.
        """
        text = """
            <span id="widget">Not class</span>
            <div>
                <p class="widget">Not span</p>
                <span class="widget">Hi</span>
            </div>
            <h1 class="widge">Welcome</h1>
            <span class="widget">Hello</span>
        """
        node = to_lxml(text)
        element = LXMLElement(node)
        result = element.find_all(name="span", attrs={"class": "widget"})

        assert all(isinstance(element, LXMLElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<span class="widget">Hi</span>""",
            """<span class="widget">Hello</span>""",
        ]

    def test_finds_all_elements_with_matching_attributes_and_name_with_limit_and_recursive_false(
        self,
    ):
        """
        Tests if `find_all` method returns all child elements, that match both provided
        attributes and name, up to the limit when recursive is False.
        Testing if method works when all parameters are provided.
        """
        text = """
            <span id="widget">Not class</span>
            <span class="widget">Welcome</span>
            <p class="widget">Not span</p>
            <div>
                <p class="widget">Not span nor child</p>
                <span class="widget">Not child</span>
            </div>
            <h1 class="widge">Welcome</h1>
            <span class="widget">Hello</span>
        """
        node = to_lxml(text).find(".//body")
        assert node is not None

        element = LXMLElement(node)
        result = element.find_all(
            name="span",
            attrs={"class": "widget"},
            recursive=False,
            limit=1,
        )

        assert all(isinstance(element, LXMLElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<span class="widget">Welcome</span>""",
        ]

    def test_get_attribute_returns_specific_attribute_value(self):
        """Tests if `get_attribute` method returns specific attribute value."""
        text = """
            <div name="menu">
                <p class="widget">Hello</p>
                <p><a>World</a></p>
            </div>
            <span class="widget">Hi</span>
        """
        node = to_lxml(text).find(".//div")
        assert node is not None

        element = LXMLElement(node)
        result = element.get_attribute("name")
        assert result == "menu"

    def test_get_attribute_returns_string_for_class(self):
        """Tests if `get_attribute` method returns string for class attribute."""
        text = """
            <div class="menu widget">
                <p class="widget">Hello</p>
                <p><a>World</a></p>
            </div>
            <span class="widget">Hi</span>
        """
        node = to_lxml(text).find(".//div")
        assert node is not None

        element = LXMLElement(node)
        result = element.get_attribute("class")
        assert result == "menu widget"
