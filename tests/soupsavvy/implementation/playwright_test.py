"""
Module with unit tests for playwright implementation of IElement and IBrowser.
Tests `PlaywrightElement` and `PlaywrightBrowser` components
and the way they interact with soupsavvy.
"""

import re

import pytest
from playwright.sync_api import Error, Page, TimeoutError

import soupsavvy.exceptions as exc
from soupsavvy.implementation.playwright import PlaywrightBrowser, PlaywrightElement
from soupsavvy.selectors.css.api import PlaywrightCSSApi
from soupsavvy.selectors.xpath.api import PlaywrightXPathApi
from tests.soupsavvy.conftest import strip


@pytest.mark.playwright
@pytest.mark.implementation
class TestPlaywrightElement:
    """Class with unit tests for `PlaywrightElement` component."""

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
            PlaywrightElement(text)  # type: ignore

    def test_node_is_wrapped_by_element(self, playwright_page: Page):
        """
        Tests if node passed to constructor is wrapped by element and can be accessed
        with `node` attribute or `get` method. This should be the same object.
        """
        text = """
            <div>Hello</div>
            <p>World</p>
        """
        playwright_page.set_content(text)
        node = playwright_page.query_selector("body")
        assert node is not None
        element = PlaywrightElement(node)

        assert element.node is node
        assert element.get() is node

    def test_can_be_constructed_with_from_node_class_method(
        self, playwright_page: Page
    ):
        """
        Tests if element can be constructed with `from_node` class method.
        This achieves the same result as init method.
        """
        text = """
            <div>Hello</div>
            <p>World</p>
        """
        playwright_page.set_content(text)
        node = playwright_page.query_selector("body")
        assert node is not None
        element = PlaywrightElement.from_node(node)

        assert element.node is node
        assert element.get() is node

    def test_str_and_repr_are_correct(self, playwright_page: Page):
        """
        Tests if `str` and `repr` methods return correct values.
        Repr should be a string with class name and wrapped node repr.
        str is constructed from outerHTML attribute of the node.
        """
        text = """
            <div>Hello</div>
            <p>World</p>
        """
        playwright_page.set_content(text)
        node = playwright_page.query_selector("html")
        assert node is not None
        element = PlaywrightElement(node)

        assert str(element) == node.evaluate("el => el.outerHTML")
        assert repr(element) == f"PlaywrightElement({node!r})"

    def test_hashes_of_two_elements_with_same_node_are_equal(
        self, playwright_page: Page
    ):
        """
        Tests if hashes of two elements with the same node are equal.
        Playwright does not guarantee the same identity for DOM elements
        from different queries, so PlaywrightElement handles it internally.
        """
        text = """
            <div>Hello</div>
            <p>World</p>
        """
        playwright_page.set_content(text)
        node = playwright_page.query_selector("html")
        assert node is not None

        node1 = node.query_selector("div")
        node2 = node.query_selector("div")
        node3 = node.query_selector("p")

        assert node1 is not None
        assert node2 is not None
        assert node3 is not None

        element1 = PlaywrightElement(node1)
        element2 = PlaywrightElement(node2)
        element3 = PlaywrightElement(node3)

        assert hash(element1) == hash(element1)
        assert hash(element1) == hash(element2)
        assert hash(element1) != hash(element3)
        assert hash(element1) != hash(node1)

    def test_equality_is_implemented_correctly(self, playwright_page: Page):
        """
        Tests if only two element objects with the same wrapped node element are equal,
        even when they are results of different searches.
        """
        text = """
            <div><p>Hello</p></div>
        """
        playwright_page.set_content(text)

        node1 = playwright_page.query_selector("html")
        node2 = playwright_page.query_selector("html")
        node3 = playwright_page.query_selector("div")

        assert node1 is not None
        assert node2 is not None
        assert node3 is not None

        element1 = PlaywrightElement(node1)
        element2 = PlaywrightElement(node2)
        element3 = PlaywrightElement(node3)

        assert element1 == element1
        assert element1 == element2
        assert element1 != element3
        assert element1 != node1

    def test_name_attribute_has_correct_value(self, playwright_page: Page):
        """Tests if `name` attribute returns name of the node element."""
        text = """
            <div>Hello</div>
            <p>World</p>
        """
        playwright_page.set_content(text)
        node = playwright_page.query_selector("div")
        assert node is not None
        element = PlaywrightElement(node)

        assert element.name == "div"

    @pytest.mark.parametrize(
        argnames="text, expected",
        argvalues=[
            ("<div>Hello</div>", "Hello"),
            ("<div> Hello\n</div>", " Hello"),  # playwright does not remove whitespaces
            ("<div>Hello<p>World</p> </div>", "HelloWorld "),
            ("Before<div>Hello<p>World</p>.</div>After", "HelloWorld."),
        ],
    )
    def test_text_return_expected_value(
        self, text: str, expected: str, playwright_page: Page
    ):
        """
        Tests if `text` property returns expected value.
        It uses `text` attribute of the node element.
        With this selenium implementation, text is stripped, it does not contain
        any leading or trailing whitespace.
        It can contain additional new line characters, which are removed for testing.
        """
        playwright_page.set_content(text)
        node = playwright_page.query_selector("div")
        assert node is not None
        element = PlaywrightElement(node)

        assert element.text.replace("\n", "") == expected

    def test_children_returns_iterator_of_child_elements_in_order(
        self, playwright_page: Page
    ):
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
        playwright_page.set_content(text)
        node = playwright_page.query_selector("div")
        assert node is not None
        element = PlaywrightElement(node)

        children = list(element.children)

        assert all(isinstance(child, PlaywrightElement) for child in children)
        assert [strip(str(child)) for child in children] == [
            "<p>Hello</p>",
            "<p>World</p>",
            "<span><p>Hi</p><a>Earth</a></span>",
        ]

    def test_children_returns_empty_iterator_if_no_children_of_element(
        self, playwright_page: Page
    ):
        """
        Tests if `children` property returns empty iterator if element has no children.
        Text node are not included in children.
        """
        text = """
            <div>Hello</div>
        """
        playwright_page.set_content(text)
        node = playwright_page.query_selector("div")
        assert node is not None
        element = PlaywrightElement(node)

        children = list(element.children)
        assert children == []

    def test_descendants_returns_iterator_of_descendant_elements_in_order(
        self, playwright_page: Page
    ):
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
        playwright_page.set_content(text)
        node = playwright_page.query_selector("div")
        assert node is not None
        element = PlaywrightElement(node)

        descendants = list(element.descendants)

        assert all(isinstance(child, PlaywrightElement) for child in descendants)
        assert [strip(str(child)) for child in descendants] == [
            "<p>Hello</p>",
            "<p>World</p>",
            "<span><span><h1>Hi</h1><h2>Hi</h2></span><a>Earth</a></span>",
            "<span><h1>Hi</h1><h2>Hi</h2></span>",
            "<h1>Hi</h1>",
            "<h2>Hi</h2>",
            "<a>Earth</a>",
        ]

    def test_descendants_returns_empty_iterator_if_no_descendants_of_element(
        self, playwright_page: Page
    ):
        """
        Tests if `descendants` property returns empty iterator
        if element has no descendants.
        """
        text = """
            <div>Hello</div>
        """
        playwright_page.set_content(text)
        node = playwright_page.query_selector("div")
        assert node is not None
        element = PlaywrightElement(node)

        descendants = list(element.descendants)
        assert descendants == []

    def test_parent_return_element_wrapping_soup_parent(self, playwright_page: Page):
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
        playwright_page.set_content(text)
        node = playwright_page.query_selector("div")
        assert node is not None
        element = PlaywrightElement(node)

        parent = element.parent
        assert isinstance(parent, PlaywrightElement)
        # selenium returns different objects every time find_element is called
        parent_node = parent.get()
        assert parent_node.evaluate("el => el.tagName").lower() == "body"

    def test_parent_return_none_when_root_node(self, playwright_page: Page):
        """Tests if `parent` property returns None if element is root node."""
        text = """
            <div>
                <p>Hello</p>
                <p>World</p>
                <span><p>Hi</p><a>Earth</a></span>
            </div>
        """
        playwright_page.set_content(text)
        root = playwright_page.query_selector("html")
        assert root is not None
        element = PlaywrightElement(root)

        parent = element.parent
        assert parent is None

    @pytest.mark.integration
    def test_css_api_works_properly(self, playwright_page: Page):
        """
        Tests if `css` method returns `SeleniumCSSApi` object correctly initialized
        which select elements properly returning list of `PlaywrightElement` objects.
        """
        text = """
            <div>
                <p class="widget">Hello</p>
                <p class="menu">World</p>
                <span><p>Hi</p><a>Earth</a></span>
            </div>
            <p class="widget">Hi</p>
        """
        playwright_page.set_content(text)
        node = playwright_page.query_selector("html")
        assert node is not None
        element = PlaywrightElement(node)

        api = element.css("p.widget")
        assert isinstance(api, PlaywrightCSSApi)

        result = api.select(element)
        assert all(isinstance(element, PlaywrightElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<p class="widget">Hello</p>""",
            """<p class="widget">Hi</p>""",
        ]

    @pytest.mark.integration
    def test_xpath_api_works_properly(self, playwright_page: Page):
        """
        Tests if `xpath` method returns `SeleniumXPathApi` object correctly initialized
        which select elements properly returning list of `PlaywrightElement` objects.
        """
        text = """
            <div>
                <p class="widget">Hello</p>
                <span><span>Hi</span><a>Earth</a></span>
            </div>
            <p class="widget">Hi</p>
        """
        playwright_page.set_content(text)
        node = playwright_page.query_selector("html")
        assert node is not None
        element = PlaywrightElement(node)

        api = element.xpath(".//p")
        assert isinstance(api, PlaywrightXPathApi)

        result = api.select(element)
        assert all(isinstance(element, PlaywrightElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<p class="widget">Hello</p>""",
            """<p class="widget">Hi</p>""",
        ]

    def test_finds_all_ancestors_of_element_in_order(self, playwright_page: Page):
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
        playwright_page.set_content(text)
        node = playwright_page.query_selector("a")
        assert node is not None
        element = PlaywrightElement(node)
        ancestors = element.find_ancestors()

        assert all(isinstance(element, PlaywrightElement) for element in ancestors)
        # selenium adds head elements arbitrarily
        assert [strip(str(x)).replace("<head></head>", "") for x in ancestors] == [
            "<p><a>Hello</a></p>",
            "<span><p><a>Hello</a></p></span>",
            """<div><p class="widget">Hello</p><span><p><a>Hello</a></p></span></div>""",
            """<body><div><p class="widget">Hello</p><span><p><a>Hello</a></p></span></div></body>""",
            """<html><body><div><p class="widget">Hello</p><span><p><a>Hello</a></p></span></div></body></html>""",
        ]

    def test_finds_ancestors_with_limit(self, playwright_page: Page):
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
        playwright_page.set_content(text)
        node = playwright_page.query_selector("a")
        assert node is not None
        element = PlaywrightElement(node)
        ancestors = element.find_ancestors(limit=2)

        assert all(isinstance(element, PlaywrightElement) for element in ancestors)
        assert [strip(str(x)) for x in ancestors] == [
            "<p><a>Hello</a></p>",
            "<span><p><a>Hello</a></p></span>",
        ]

    def test_find_ancestors_returns_empty_list_if_root_element(
        self, playwright_page: Page
    ):
        """Tests if `find_ancestors` method returns empty list if element is root."""
        text = """
            <div>
                <p class="widget">Hello</p>
                <span><p><a>Hello</a></p></span>
            </div>
        """
        playwright_page.set_content(text)
        node = playwright_page.query_selector("html")
        assert node is not None
        element = PlaywrightElement(node)
        assert element.find_ancestors() == []

    def test_finds_all_subsequent_siblings_of_element(self, playwright_page: Page):
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
        playwright_page.set_content(text)
        node = playwright_page.query_selector("span")
        assert node is not None
        element = PlaywrightElement(node)
        siblings = element.find_subsequent_siblings()

        assert all(isinstance(element, PlaywrightElement) for element in siblings)
        assert [strip(str(x)) for x in siblings] == [
            "<p><a>World</a></p>",
            "<span>Earth</span>",
            "<h1>Nice</h1>",
        ]

    def test_finds_all_subsequent_returns_empty_list_if_last_child(
        self, playwright_page: Page
    ):
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
        playwright_page.set_content(text)
        node = playwright_page.query_selector("span")
        assert node is not None
        element = PlaywrightElement(node)
        assert element.find_subsequent_siblings() == []

    def test_finds_all_subsequent_with_limit(self, playwright_page: Page):
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
        playwright_page.set_content(text)
        node = playwright_page.query_selector("span")
        assert node is not None
        element = PlaywrightElement(node)
        siblings = element.find_subsequent_siblings(limit=2)

        assert all(isinstance(element, PlaywrightElement) for element in siblings)
        assert [strip(str(x)) for x in siblings] == [
            "<p><a>World</a></p>",
            "<span>Earth</span>",
        ]

    def test_finds_all_elements_when_no_specifications(self, playwright_page: Page):
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
        playwright_page.set_content(text)
        node = playwright_page.query_selector("body")
        assert node is not None
        element = PlaywrightElement(node)
        result = element.find_all()

        assert all(isinstance(element, PlaywrightElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<div><p class="widget">Hello</p><p><a>World</a></p></div>""",
            """<p class="widget">Hello</p>""",
            """<p><a>World</a></p>""",
            """<a>World</a>""",
            """<span>Hi</span>""",
        ]

    def test_finds_all_returns_list_of_children_when_recursive_false(
        self, playwright_page: Page
    ):
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
        playwright_page.set_content(text)
        node = playwright_page.query_selector("body")
        assert node is not None
        element = PlaywrightElement(node)
        result = element.find_all(recursive=False)

        assert all(isinstance(element, PlaywrightElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<div><p class="widget">Hello</p><p><a>World</a></p></div>""",
            """<span>Hi</span>""",
        ]

    def test_finds_all_elements_with_limit(self, playwright_page: Page):
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
        playwright_page.set_content(text)
        node = playwright_page.query_selector("body")
        assert node is not None
        element = PlaywrightElement(node)
        result = element.find_all(limit=3)

        assert all(isinstance(element, PlaywrightElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<div><p class="widget">Hello</p><p><a>World</a></p></div>""",
            """<p class="widget">Hello</p>""",
            """<p><a>World</a></p>""",
        ]

    def test_finds_all_elements_with_limit_and_recursive_false(
        self, playwright_page: Page
    ):
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
        playwright_page.set_content(text)
        node = playwright_page.query_selector("body")
        assert node is not None
        element = PlaywrightElement(node)
        result = element.find_all(limit=2, recursive=False)

        assert all(isinstance(element, PlaywrightElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<div><p class="widget">Hello</p><span><h1>World</h1></span></div>""",
            """<span>Hi</span>""",
        ]

    def test_finds_all_returns_empty_list_if_nothing_matches(
        self, playwright_page: Page
    ):
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
        playwright_page.set_content(text)
        node = playwright_page.query_selector("html")
        assert node is not None
        element = PlaywrightElement(node)

        result = element.find_all(name="h2")
        assert result == []

    def test_finds_all_returns_empty_list_if_nothing_matches_and_recursive_false(
        self, playwright_page: Page
    ):
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
        playwright_page.set_content(text)
        node = playwright_page.query_selector("html")
        assert node is not None
        element = PlaywrightElement(node)

        result = element.find_all(name="h2", recursive=False)
        assert result == []

    def test_finds_all_elements_with_specific_name(self, playwright_page: Page):
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
        playwright_page.set_content(text)
        node = playwright_page.query_selector("html")
        assert node is not None
        element = PlaywrightElement(node)
        result = element.find_all(name="p")

        assert all(isinstance(element, PlaywrightElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<p class="widget">Hello</p>""",
            """<p><a>World</a></p>""",
        ]

    def test_finds_all_elements_with_specific_name_and_recursive_false(
        self, playwright_page: Page
    ):
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
        playwright_page.set_content(text)
        node = playwright_page.query_selector("body")
        assert node is not None
        element = PlaywrightElement(node)
        result = element.find_all(name="span", recursive=False)

        assert all(isinstance(element, PlaywrightElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<span>Hi</span>""",
            """<span><p>World</p></span>""",
        ]

    def test_finds_all_elements_with_exact_attribute_match(self, playwright_page: Page):
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
        playwright_page.set_content(text)
        node = playwright_page.query_selector("html")
        assert node is not None
        element = PlaywrightElement(node)
        result = element.find_all(attrs={"class": "widget"})

        assert all(isinstance(element, PlaywrightElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<p class="widget">Hello</p>""",
            """<span class="widget">Hi</span>""",
        ]

    def test_finds_all_elements_with_regex_attribute_match(self, playwright_page: Page):
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
        playwright_page.set_content(text)
        node = playwright_page.query_selector("html")
        assert node is not None
        element = PlaywrightElement(node)
        result = element.find_all(attrs={"class": re.compile("widget")})

        assert all(isinstance(element, PlaywrightElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<p class="widget123">Hello</p>""",
            """<span class="widget menu">Hi</span>""",
            """<span class="menu your_widget">Hello</span>""",
        ]

    def test_finds_all_elements_with_matching_multiple_attributes(
        self, playwright_page: Page
    ):
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
        playwright_page.set_content(text)
        node = playwright_page.query_selector("html")
        assert node is not None
        element = PlaywrightElement(node)
        result = element.find_all(attrs={"class": "widget", "name": "menu"})

        assert all(isinstance(element, PlaywrightElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<h1 class="widget" name="menu">Welcome</h1>"""
        ]

    def test_finds_all_elements_with_matching_attributes_and_name(
        self, playwright_page: Page
    ):
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
        playwright_page.set_content(text)
        node = playwright_page.query_selector("html")
        assert node is not None
        element = PlaywrightElement(node)
        result = element.find_all(name="span", attrs={"class": "widget"})

        assert all(isinstance(element, PlaywrightElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<span class="widget">Hi</span>""",
            """<span class="widget">Hello</span>""",
        ]

    def test_finds_all_elements_with_matching_attributes_and_name_with_limit_and_recursive_false(
        self, playwright_page: Page
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
        playwright_page.set_content(text)
        node = playwright_page.query_selector("body")
        assert node is not None
        element = PlaywrightElement(node)
        result = element.find_all(
            name="span",
            attrs={"class": "widget"},
            recursive=False,
            limit=1,
        )

        assert all(isinstance(element, PlaywrightElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<span class="widget">Welcome</span>""",
        ]

    def test_get_attribute_returns_specific_attribute_value(
        self, playwright_page: Page
    ):
        """Tests if `get_attribute` method returns specific attribute value."""
        text = """
            <div name="menu">
                <p class="widget">Hello</p>
                <p><a>World</a></p>
            </div>
            <span class="widget">Hi</span>
        """
        playwright_page.set_content(text)
        node = playwright_page.query_selector("div")
        assert node is not None
        element = PlaywrightElement(node)
        result = element.get_attribute("name")
        assert result == "menu"

    def test_get_attribute_returns_string_for_class(self, playwright_page: Page):
        """Tests if `get_attribute` method returns string for class attribute."""
        text = """
            <div class="menu widget">
                <p class="widget">Hello</p>
                <p><a>World</a></p>
            </div>
            <span class="widget">Hi</span>
        """
        playwright_page.set_content(text)
        node = playwright_page.query_selector("div")
        assert node is not None
        element = PlaywrightElement(node)
        result = element.get_attribute("class")
        assert result == "menu widget"

    def test_get_attribute_prefers_property_over_attribute(self, playwright_page: Page):
        """
        Tests that the property value returned by evaluate() - js live property
        takes precedence over the static HTML attribute when both exist.
        """
        text = """<input type="text" value="attr_value">"""
        playwright_page.set_content(text)

        node = playwright_page.query_selector("input")
        assert node is not None
        element = PlaywrightElement(node)

        # JS property should be same as attribute initially
        assert element.get_attribute("value") == "attr_value"
        # Change the value property dynamically
        node.evaluate("el => el.value = 'property_value'")
        assert element.get_attribute("value") == "property_value"

    def test_get_attribute_returns_empty_string_for_empty_property(
        self, playwright_page: Page
    ):
        """
        Tests that an empty string property does not fallback to get_attribute()
        and is returned as-is (not None).
        """
        text = """<input type="text" />"""
        playwright_page.set_content(text)

        node = playwright_page.query_selector("input")
        assert node is not None
        element = PlaywrightElement(node)

        assert element.get_attribute("value") == ""

    def test_get_attribute_returns_none_when_not_present(self, playwright_page: Page):
        """Tests that a non-existent property/attribute returns None."""
        text = """<div></div>"""
        playwright_page.set_content(text)

        node = playwright_page.query_selector("div")
        assert node is not None
        element = PlaywrightElement(node)

        assert element.get_attribute("nonexistent") is None


class FakeDriver:
    """A fake Page for simulating errors & redirects."""

    def __init__(self):
        self._url = None
        self.closed = False

    def goto(self, url: str):
        if url == "http://bad-url":
            raise Error("Connection error")
        if url == "http://redirect":
            self._url = "http://final-url"
        else:
            self._url = url

    def close(self):
        self.closed = True

    @property
    def url(self):
        return self._url

    def query_selector(self, selector: str):
        return None


@pytest.fixture
def fake_driver() -> FakeDriver:
    """Provides a fake Page instance for testing."""
    return FakeDriver()


@pytest.mark.playwright
@pytest.mark.implementation
@pytest.mark.browser
class TestPlaywrightBrowser:

    def test_initializes_with_driver(self, playwright_page: Page):
        """Tests if `PlaywrightBrowser` can be initialized with playwright Page."""
        browser = PlaywrightBrowser(playwright_page)
        assert browser.browser is playwright_page
        assert browser.get() is playwright_page

    def test_str_and_repr_are_correct(self, playwright_page: Page):
        """
        Tests if `str` and `repr` methods return correct values.
        Repr should be a string with class name and wrapped page representation.
        str is constructed from the wrapped page's str.
        """
        browser = PlaywrightBrowser(playwright_page)

        assert str(browser) == str(browser.browser)
        assert repr(browser) == f"PlaywrightBrowser({browser.browser!r})"

    def test_navigate_success(self, fake_driver: FakeDriver):
        """Simulates navigation working normally."""

        browser = PlaywrightBrowser(fake_driver)  # type: ignore
        browser.navigate("http://ok")
        assert browser.get_current_url() == "http://ok"

    def test_navigate_redirect(self, fake_driver: FakeDriver):
        """Simulates a redirect after navigation."""
        browser = PlaywrightBrowser(fake_driver)  # type: ignore
        browser.navigate("http://redirect")
        assert browser.get_current_url() == "http://final-url"

    def test_navigate_connection_error(self, fake_driver: FakeDriver):
        """Simulates a connection error during navigation."""
        browser = PlaywrightBrowser(fake_driver)  # type: ignore

        with pytest.raises(Error):
            browser.navigate("http://bad-url")

    def test_keys_are_send_properly(self, playwright_page: Page):
        """
        Tests if `send_keys` method sends keys properly to the element
        and value of the element is changed accordingly.
        """
        to_insert = "Hello World"
        text = """<input id="editable" type="text" />"""
        playwright_page.set_content(text)

        browser = PlaywrightBrowser(playwright_page)
        node = playwright_page.query_selector("#editable")
        assert node is not None
        element = PlaywrightElement(node)

        browser.send_keys(element=element, value=to_insert)
        assert element.get_attribute("value") == to_insert

    def test_keys_are_not_cleared_when_clear_false(self, playwright_page: Page):
        """
        Tests if `send_keys` method does not clear the element before sending keys
        when `clear` parameter is set to False.
        """
        text = """<input id="editable" type="text" value="original" />"""
        playwright_page.set_content(text)

        browser = PlaywrightBrowser(playwright_page)
        node = playwright_page.query_selector("#editable")
        assert node is not None
        element = PlaywrightElement(node)

        browser.send_keys(element=element, value="Hello")
        assert element.get_attribute("value") == "Hello"

        browser.send_keys(element=element, value=" World", clear=False)
        assert element.get_attribute("value") == "Hello World"

    def test_sends_key_only_to_specified_element(self, playwright_page: Page):
        """
        Tests if `send_keys` method sends keys only to the specified element.
        Other elements are not affected.
        """
        text = """
            <input id="one" type="text" />
            <input id="two" type="text" />
        """
        playwright_page.set_content(text)

        node1 = playwright_page.query_selector("#one")
        node2 = playwright_page.query_selector("#two")
        assert node1 and node2

        el1 = PlaywrightElement(node1)
        el2 = PlaywrightElement(node2)

        browser = PlaywrightBrowser(playwright_page)
        browser.send_keys(el1, "First")

        assert el1.get_attribute("value") == "First"
        assert el2.get_attribute("value") == ""

    def test_raises_error_when_element_is_not_editable(self, playwright_page: Page):
        """
        Tests if `send_keys` method raises an error when the element is not editable.
        """
        text = """
            <div>Hello</div>
            <p>World</p>
        """
        playwright_page.set_content(text)

        node = playwright_page.query_selector("div")
        assert node is not None
        element = PlaywrightElement(node)
        browser = PlaywrightBrowser(playwright_page)

        with pytest.raises(Error):
            browser.send_keys(element, "First")

    def test_closes_browser_properly(self, fake_driver: FakeDriver):
        """
        Tests if `close` method calls `close` on the Page.
        Uses mock driver to avoid actually closing the browser during tests.
        """
        browser = PlaywrightBrowser(fake_driver)  # type: ignore
        assert fake_driver.closed is False
        browser.close()
        assert fake_driver.closed is True

    def test_clicks_element_properly(self, playwright_page: Page):
        """
        Tests if `click` method clicks the element properly
        and the click event is reflected in the page.
        """
        text = """
            <button id="myButton" onclick="this.innerText='Clicked'">Not clicked</button>
        """
        playwright_page.set_content(text)
        browser = PlaywrightBrowser(playwright_page)

        node = playwright_page.query_selector("#myButton")
        assert node is not None
        element = PlaywrightElement(node)

        assert element.text == "Not clicked"
        browser.click(element)
        assert element.text == "Clicked"

    def test_click_element_covered_by_other(self, playwright_page: Page):
        """
        Tests that `click` method works even when the element
        is visually covered by another element, hidden or off-screen.
        It uses js script instead of click command.
        """
        html = """
            <style>
                #cover {
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 200px;
                    height: 200px;
                    background: rgba(0, 0, 0, 0.5);
                    z-index: 10;
                }
            </style>
            <button id="target" onclick="this.innerText='Clicked'">Not clicked</button>
            <div id="cover"></div>
        """
        playwright_page.set_content(html)

        browser = PlaywrightBrowser(playwright_page)
        node = playwright_page.query_selector("#target")
        assert node is not None

        element = PlaywrightElement(node)
        assert element.text == "Not clicked"

        with pytest.raises(TimeoutError):
            node.click(timeout=10)

        # Click method bypasses visibility
        browser.click(element)
        assert element.text == "Clicked"

    def test_click_triggers_navigation(self, playwright_page: Page):
        """Tests if `click` method triggers navigation when clicking a link."""
        text = """<a id="myLink" href="about:blank">Go</a>"""
        playwright_page.set_content(text)

        browser = PlaywrightBrowser(playwright_page)
        node = playwright_page.query_selector("#myLink")
        assert node is not None
        element = PlaywrightElement(node)

        browser.click(element)
        assert browser.get_current_url() == "about:blank"

    def test_multiple_clicks_work_properly(self, playwright_page: Page):
        """
        Tests if `click` method can be called multiple times on the same element.
        """
        text = """<button id="counter" onclick="this.innerText=parseInt(this.innerText)+1">0</button>"""
        playwright_page.set_content(text)

        browser = PlaywrightBrowser(playwright_page)
        node = playwright_page.query_selector("#counter")
        assert node is not None
        element = PlaywrightElement(node)

        for _ in range(3):
            browser.click(element)

        assert element.text == "3"

    def test_get_html_returns_html_element(self, playwright_page: Page):
        """
        Tests if `get_html` method returns html element of the page
        wrapped in `PlaywrightElement`.
        """
        text = """
            <div>Hello</div>
            <p>World</p>
        """
        playwright_page.set_content(text)
        browser = PlaywrightBrowser(playwright_page)
        body = browser.get_document()

        assert isinstance(body, PlaywrightElement)
        assert body.name == "html"

    def test_get_html_raises_error_if_not_found(self, fake_driver: FakeDriver):
        """
        Tests if `get_html` method raises `TagNotFoundException`
        if <html> element is not found.
        """
        browser = PlaywrightBrowser(fake_driver)  # type: ignore

        with pytest.raises(exc.TagNotFoundException):
            browser.get_document()

    def test_hash_is_based_on_instance_id(self):
        """
        Tests if `__hash__` method returns hash based on instance id.
        """
        driver1 = FakeDriver()
        driver2 = FakeDriver()

        browser1 = PlaywrightBrowser(driver1)  # type: ignore
        browser2 = PlaywrightBrowser(driver1)  # type: ignore
        browser3 = PlaywrightBrowser(driver2)  # type: ignore

        assert hash(browser1) == hash(browser1)
        assert hash(browser1) == hash(browser2)
        assert hash(browser1) != hash(browser3)

    def test_instances_are_equal_if_they_have_the_same_driver(self):
        """
        Tests if `__eq__` method returns True if two instances
        have the same Page instance.
        """
        driver1 = FakeDriver()
        driver2 = FakeDriver()

        browser1 = PlaywrightBrowser(driver1)  # type: ignore
        browser2 = PlaywrightBrowser(driver1)  # type: ignore
        browser3 = PlaywrightBrowser(driver2)  # type: ignore

        assert browser1 == browser1
        assert browser1 == browser2
        assert browser1 != browser3
