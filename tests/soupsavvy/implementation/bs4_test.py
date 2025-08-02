"""
Module with unit tests for bs4 implementation of IElement.
Tests `SoupElement` component and the way it interacts with soupsavvy.
"""

import re

import pytest
from bs4 import BeautifulSoup, Tag

from soupsavvy.implementation.bs4 import SoupElement
from soupsavvy.selectors.css.api import SoupsieveApi
from tests.soupsavvy.conftest import strip


@pytest.mark.bs4
@pytest.mark.implementation
class TestSoupElement:
    """Class with unit tests for `SoupElement` component."""

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
            SoupElement(text)

    def test_node_is_wrapped_by_element(self):
        """
        Tests if node passed to constructor is wrapped by element and can be accessed
        with `node` attribute or `get` method. This should be the same object.
        """
        text = """
            <div>Hello</div>
            <p>World</p>
        """
        bs = BeautifulSoup(text, features="lxml")
        element = SoupElement(bs)

        assert element.node is bs
        assert element.get() is bs

    def test_can_be_constructed_with_from_node_class_method(self):
        """
        Tests if element can be constructed with `from_node` class method.
        This achieves the same result as init method.
        """
        text = """
            <div>Hello</div>
            <p>World</p>
        """
        bs = BeautifulSoup(text, features="lxml")
        element = SoupElement.from_node(bs)

        assert element.node is bs
        assert element.get() is bs

    def test_str_and_repr_are_correct(self):
        """
        Tests if `str` and `repr` methods return correct values.
        str is supposed to be the same as wrapped node element.
        Repr should be a string with class name and wrapped node element repr.
        """
        text = """
            <div>Hello</div>
            <p>World</p>
        """
        bs = BeautifulSoup(text, features="lxml")
        element = SoupElement(bs)

        assert str(element) == str(bs)
        assert repr(element) == f"SoupElement({bs!r})"

    def test_hashes_of_two_elements_with_same_node_are_equal(self):
        """
        Tests if hashes of two elements with the same node are equal.
        For bs4 it tests if hash of SoupElement is equal to id of wrapped element.
        Bs4 element is hashed by string representation, two elements with the same
        content will have the same hash.
        To prevent this, implementation uses hash of id.
        """
        text = """
            <div>Hello</div>
            <p>World</p>
        """
        bs = BeautifulSoup(text, features="lxml")
        element = SoupElement(bs)

        div = bs.find("div")
        div2 = bs.find("div")

        assert hash(SoupElement(div)) == hash(SoupElement(div2))
        assert hash(element) == hash(id(bs))

    def test_equality_is_implemented_correctly(self):
        """
        Tests if only two SoupElement objects
        with the same wrapped bs4 element are equal.
        """
        text = """
            <div><p>Hello</p></div>
        """
        bs = BeautifulSoup(text, features="lxml")
        element = SoupElement(bs)

        assert element == SoupElement(bs)
        assert element != SoupElement(bs.p)  # type: ignore
        assert element != bs

    def test_name_attribute_has_correct_value(self):
        """Tests if `name` attribute returns name of the node element."""
        text = """
            <div>Hello</div>
            <p>World</p>
        """
        bs = BeautifulSoup(text, features="lxml").div
        assert bs is not None

        element = SoupElement(bs)
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
        It uses default bs4 `text` property, which does not strip text
        or use any separator. All text nodes inside element are concatenated.
        """
        bs = BeautifulSoup(text, features="lxml").div
        assert bs is not None

        element = SoupElement(bs)
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
        bs = BeautifulSoup(text, "html.parser").div
        assert bs is not None

        element = SoupElement(bs)
        children = list(element.children)

        assert all(isinstance(child, SoupElement) for child in children)
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
        bs = BeautifulSoup(text, features="lxml").div
        assert bs is not None

        element = SoupElement(bs)
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
        bs = BeautifulSoup(text, features="lxml").div
        assert bs is not None

        element = SoupElement(bs)
        descendants = list(element.descendants)

        assert all(isinstance(child, SoupElement) for child in descendants)
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
        bs = BeautifulSoup(text, features="lxml").div
        assert bs is not None

        element = SoupElement(bs)
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
        bs = BeautifulSoup(text, features="lxml").p
        assert bs is not None

        element = SoupElement(bs)
        parent = element.parent

        assert isinstance(parent, SoupElement)
        assert parent.get() is bs.parent

    def test_parent_return_none_when_root_node(self):
        """Tests if `parent` property returns None if element is root node."""
        text = """
            <div>
                <p>Hello</p>
                <p>World</p>
                <span><p>Hi</p><a>Earth</a></span>
            </div>
        """
        bs = BeautifulSoup(text, features="lxml")
        element = SoupElement(bs)
        parent = element.parent

        assert parent is None

    @pytest.mark.integration
    def test_css_api_works_properly(self):
        """
        Tests if `css` method returns `SoupsieveApi` object correctly initialized
        which select elements properly returning list of `SoupElement` objects.
        """
        text = """
            <div>
                <p class="widget">Hello</p>
                <p class="menu">World</p>
                <span><p>Hi</p><a>Earth</a></span>
            </div>
            <p class="widget">Hi</p>
        """
        bs = BeautifulSoup(text, features="lxml")
        element = SoupElement(bs)
        api = element.css("p.widget")

        assert isinstance(api, SoupsieveApi)

        result = api.select(element)
        assert all(isinstance(element, SoupElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<p class="widget">Hello</p>""",
            """<p class="widget">Hi</p>""",
        ]

    def test_xpath_is_not_implemented(self):
        """
        Tests if `xpath` method raises `NotImplementedError`.
        This is not implemented for bs4 implementation.
        """
        text = """
            <div>
                <p class="widget">Hello</p>
                <p class="menu">World</p>
            </div>
        """
        bs = BeautifulSoup(text, features="lxml")
        element = SoupElement(bs)

        with pytest.raises(NotImplementedError):
            element.xpath(".//p")

    def test_finds_all_ancestors_of_element_in_order(self):
        """
        Tests if `find_ancestors` method returns list of ancestors of element
        starting from parent moving up to the root of the document.
        For bs4, last ancestor will always be root element.
        """
        text = """
            <div>
                <p class="widget">Hello</p>
                <span><span><h1>Hello</h1></span></span>
            </div>
        """
        # html.parser is used to not include body and html
        bs = BeautifulSoup(text, features="html.parser").h1
        assert bs is not None

        element = SoupElement(bs)
        ancestors = element.find_ancestors()

        assert all(isinstance(element, SoupElement) for element in ancestors)
        assert [strip(str(x)) for x in ancestors] == [
            "<span><h1>Hello</h1></span>",
            "<span><span><h1>Hello</h1></span></span>",
            """<div><p class="widget">Hello</p><span><span><h1>Hello</h1></span></span></div>""",
            # root - document
            """<div><p class="widget">Hello</p><span><span><h1>Hello</h1></span></span></div>""",
        ]

    def test_finds_ancestors_with_limit(self):
        """
        Tests if `find_ancestors` method returns ancestors up to the limit.
        No more than `limit` ancestors are returned.
        """
        text = """
            <div>
                <p class="widget">Hello</p>
                <span><span><h1>Hello</h1></span></span>
            </div>
        """
        bs = BeautifulSoup(text, features="html.parser").h1
        assert bs is not None

        element = SoupElement(bs)
        ancestors = element.find_ancestors(limit=2)

        assert all(isinstance(element, SoupElement) for element in ancestors)
        assert [strip(str(x)) for x in ancestors] == [
            "<span><h1>Hello</h1></span>",
            "<span><span><h1>Hello</h1></span></span>",
        ]

    def test_find_ancestors_returns_empty_list_if_root_element(self):
        """Tests if `find_ancestors` method returns empty list if element is root."""
        text = """
            <div>
                <p class="widget">Hello</p>
                <span><span><h1>Hello</h1></span></span>
            </div>
        """
        bs = BeautifulSoup(text, features="html.parser")
        assert bs is not None

        element = SoupElement(bs)
        assert element.find_ancestors() == []

    def test_finds_all_subsequent_siblings_of_element(self):
        """
        Tests if `find_subsequent_siblings` method returns all subsequent siblings.
        """
        text = """
            <div>
                <p class="widget">Hello</p>
                <span class="anchor">Hello</span>
                <span><h1>World</h1></span>
                <span>Earth</span>
                <h1>Nice</h1>
            </div>
            <span>Hi</span>
        """
        bs = BeautifulSoup(text, features="lxml").find(class_="anchor")
        assert isinstance(bs, Tag)

        element = SoupElement(bs)
        siblings = element.find_subsequent_siblings()

        assert all(isinstance(element, SoupElement) for element in siblings)
        assert [strip(str(x)) for x in siblings] == [
            "<span><h1>World</h1></span>",
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
        bs = BeautifulSoup(text, features="lxml").find(class_="anchor")
        assert isinstance(bs, Tag)

        element = SoupElement(bs)
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
                <span><h1>World</h1></span>
                <span>Earth</span>
                <h1>Nice</h1>
            </div>
            <span>Hi</span>
        """
        bs = BeautifulSoup(text, features="lxml").find(class_="anchor")
        assert isinstance(bs, Tag)

        element = SoupElement(bs)
        siblings = element.find_subsequent_siblings(limit=2)

        assert all(isinstance(element, SoupElement) for element in siblings)
        assert [strip(str(x)) for x in siblings] == [
            "<span><h1>World</h1></span>",
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
                <span><h1>World</h1></span>
            </div>
            <span>Hi</span>
        """
        bs = BeautifulSoup(text, features="html.parser")
        element = SoupElement(bs)
        result = element.find_all()

        assert all(isinstance(element, SoupElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<div><p class="widget">Hello</p><span><h1>World</h1></span></div>""",
            """<p class="widget">Hello</p>""",
            """<span><h1>World</h1></span>""",
            """<h1>World</h1>""",
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
                <span><h1>World</h1></span>
            </div>
            <span>Hi</span>
        """
        bs = BeautifulSoup(text, features="html.parser")
        element = SoupElement(bs)
        result = element.find_all(recursive=False)

        assert all(isinstance(element, SoupElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<div><p class="widget">Hello</p><span><h1>World</h1></span></div>""",
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
                <span><h1>World</h1></span>
            </div>
            <span>Hi</span>
        """
        bs = BeautifulSoup(text, features="html.parser")
        element = SoupElement(bs)
        result = element.find_all(limit=3)

        assert all(isinstance(element, SoupElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<div><p class="widget">Hello</p><span><h1>World</h1></span></div>""",
            """<p class="widget">Hello</p>""",
            """<span><h1>World</h1></span>""",
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
        bs = BeautifulSoup(text, features="html.parser")
        element = SoupElement(bs)
        result = element.find_all(limit=2, recursive=False)

        assert all(isinstance(element, SoupElement) for element in result)
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
        bs = BeautifulSoup(text, features="lxml")
        element = SoupElement(bs)
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
        bs = BeautifulSoup(text, features="html.parser")
        element = SoupElement(bs)
        result = element.find_all(name="h2", recursive=False)
        assert result == []

    def test_finds_all_elements_with_specific_name(self):
        """
        Tests if `find_all` method returns all descendant elements with specific name.
        """
        text = """
            <div>
                <p class="widget">Hello</p>
                <span><h1>World</h1></span>
            </div>
            <span>Hi</span>
        """
        bs = BeautifulSoup(text, features="lxml")
        element = SoupElement(bs)
        result = element.find_all(name="span")

        assert all(isinstance(element, SoupElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<span><h1>World</h1></span>""",
            """<span>Hi</span>""",
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
        bs = BeautifulSoup(text, features="html.parser")
        element = SoupElement(bs)
        result = element.find_all(name="span", recursive=False)

        assert all(isinstance(element, SoupElement) for element in result)
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
                <span><h1>World</h1></span>
            </div>
            <span class="widget menu">Hi</span>
        """
        bs = BeautifulSoup(text, features="lxml")
        element = SoupElement(bs)
        result = element.find_all(attrs={"class": "widget"})

        assert all(isinstance(element, SoupElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<p class="widget">Hello</p>""",
            """<span class="widget menu">Hi</span>""",
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
        bs = BeautifulSoup(text, features="lxml")
        element = SoupElement(bs)
        result = element.find_all(attrs={"class": re.compile("widget")})

        assert all(isinstance(element, SoupElement) for element in result)
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
        bs = BeautifulSoup(text, features="lxml")
        element = SoupElement(bs)
        result = element.find_all(attrs={"class": "widget", "name": "menu"})

        assert all(isinstance(element, SoupElement) for element in result)
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
        bs = BeautifulSoup(text, features="lxml")
        element = SoupElement(bs)
        result = element.find_all(name="span", attrs={"class": "widget"})

        assert all(isinstance(element, SoupElement) for element in result)
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
        bs = BeautifulSoup(text, features="html.parser")
        element = SoupElement(bs)
        result = element.find_all(
            name="span",
            attrs={"class": "widget"},
            recursive=False,
            limit=1,
        )

        assert all(isinstance(element, SoupElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<span class="widget">Welcome</span>""",
        ]

    def test_get_attribute_returns_specific_attribute_value(self):
        """Tests if `get_attribute` method returns specific attribute value."""
        text = """
            <div name="menu">
                <p class="widget">Hello</p>
                <span><h1>World</h1></span>
            </div>
            <span class="widget">Hi</span>
        """
        bs = BeautifulSoup(text, features="lxml").div
        assert bs is not None

        element = SoupElement(bs)
        result = element.get_attribute("name")
        assert result == "menu"

    def test_get_attribute_returns_string_for_class(self):
        """
        Tests if `get_attribute` method returns string for class attribute.
        This is adjustment to bs4 behavior, which returns list of classes.
        The reason is unification across multiple implementations.
        """
        text = """
            <div class="menu widget">
                <p class="widget">Hello</p>
                <span><h1>World</h1></span>
            </div>
            <span class="widget">Hi</span>
        """
        bs = BeautifulSoup(text, features="lxml").div
        assert bs is not None

        element = SoupElement(bs)
        result = element.get_attribute("class")
        assert result == "menu widget"
