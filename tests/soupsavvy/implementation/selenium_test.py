"""
Module with unit tests for selenium implementations of IElement and IBrowser.
Tests `SeleniumElement` and `SeleniumBrowser` components
and the way they interact with soupsavvy.
"""

import re

import pytest
import selenium.common.exceptions as selenium_exceptions
from pytest import MonkeyPatch
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver

from soupsavvy.implementation.selenium import SeleniumBrowser, SeleniumElement
from soupsavvy.selectors.css.api import SeleniumCSSApi
from soupsavvy.selectors.xpath.api import SeleniumXPathApi
from tests.soupsavvy.conftest import insert, strip


@pytest.mark.selenium
@pytest.mark.implementation
class TestSeleniumElement:
    """Class with unit tests for `SeleniumElement` component."""

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
            SeleniumElement(text)

    def test_node_is_wrapped_by_element(self, driver_selenium: WebDriver):
        """
        Tests if node passed to constructor is wrapped by element and can be accessed
        with `node` attribute or `get` method. This should be the same object.
        """
        text = """
            <div>Hello</div>
            <p>World</p>
        """
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "html")
        element = SeleniumElement(node)

        assert element.node is node
        assert element.get() is node

    def test_can_be_constructed_with_from_node_class_method(
        self, driver_selenium: WebDriver
    ):
        """
        Tests if element can be constructed with `from_node` class method.
        This achieves the same result as init method.
        """
        text = """
            <div>Hello</div>
            <p>World</p>
        """
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "html")
        element = SeleniumElement.from_node(node)

        assert element.node is node
        assert element.get() is node

    def test_str_and_repr_are_correct(self, driver_selenium: WebDriver):
        """
        Tests if `str` and `repr` methods return correct values.
        Repr should be a string with class name and wrapped node repr.
        str is constructed from outerHTML attribute of the node.
        """
        text = """
            <div>Hello</div>
            <p>World</p>
        """
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "html")
        element = SeleniumElement(node)

        assert str(element) == node.get_attribute("outerHTML")
        assert repr(element) == f"SeleniumElement({node!r})"

    def test_hashes_of_two_elements_with_same_node_are_equal(
        self, driver_selenium: WebDriver
    ):
        """
        Tests if hashes of two elements with the same node are equal.
        In selenium, hash is equal to the hash of the wrapped node element.
        """
        text = """
            <div>Hello</div>
            <p>World</p>
        """
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "html")
        element = SeleniumElement(node)

        div = node.find_element(By.TAG_NAME, "div")
        div2 = node.find_element(By.TAG_NAME, "div")

        assert hash(SeleniumElement(div)) == hash(SeleniumElement(div2))
        assert hash(element) == hash(node)

    def test_equality_is_implemented_correctly(self, driver_selenium: WebDriver):
        """
        Tests if only two element objects with the same wrapped node element are equal.
        """
        text = """
            <div><p>Hello</p></div>
        """
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "html")
        element = SeleniumElement(node)

        assert element == SeleniumElement(node)
        assert element != SeleniumElement(node.find_element(By.TAG_NAME, "div"))
        assert element != node

    def test_name_attribute_has_correct_value(self, driver_selenium: WebDriver):
        """Tests if `name` attribute returns name of the node element."""
        text = """
            <div>Hello</div>
            <p>World</p>
        """
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "div")
        element = SeleniumElement(node)

        assert element.name == "div"

    @pytest.mark.parametrize(
        argnames="text, expected",
        argvalues=[
            ("<div>Hello</div>", "Hello"),
            ("<div> Hello\n</div>", "Hello"),
            ("<div>Hello<p>World</p> </div>", "HelloWorld"),
            ("Before<div>Hello<p>World</p>.</div>After", "HelloWorld."),
        ],
    )
    def test_text_return_expected_value(
        self, text: str, expected: str, driver_selenium: WebDriver
    ):
        """
        Tests if `text` property returns expected value.
        It uses `text` attribute of the node element.
        With this selenium implementation, text is stripped, it does not contain
        any leading or trailing whitespace.
        It can contain additional new line characters, which are removed for testing.
        """
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "div")
        element = SeleniumElement(node)

        assert element.text.replace("\n", "") == expected

    def test_children_returns_iterator_of_child_elements_in_order(
        self, driver_selenium: WebDriver
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
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "div")
        element = SeleniumElement(node)

        children = list(element.children)

        assert all(isinstance(child, SeleniumElement) for child in children)
        assert [strip(str(child)) for child in children] == [
            "<p>Hello</p>",
            "<p>World</p>",
            "<span><p>Hi</p><a>Earth</a></span>",
        ]

    def test_children_returns_empty_iterator_if_no_children_of_element(
        self, driver_selenium: WebDriver
    ):
        """
        Tests if `children` property returns empty iterator if element has no children.
        Text node are not included in children.
        """
        text = """
            <div>Hello</div>
        """
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "div")
        element = SeleniumElement(node)

        children = list(element.children)
        assert children == []

    def test_descendants_returns_iterator_of_descendant_elements_in_order(
        self, driver_selenium: WebDriver
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
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "div")
        element = SeleniumElement(node)

        descendants = list(element.descendants)

        assert all(isinstance(child, SeleniumElement) for child in descendants)
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
        self, driver_selenium: WebDriver
    ):
        """
        Tests if `descendants` property returns empty iterator
        if element has no descendants.
        """
        text = """
            <div>Hello</div>
        """
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "div")
        element = SeleniumElement(node)

        descendants = list(element.descendants)
        assert descendants == []

    def test_parent_return_element_wrapping_soup_parent(
        self, driver_selenium: WebDriver
    ):
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
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "div")
        element = SeleniumElement(node)

        parent = element.parent
        assert isinstance(parent, SeleniumElement)
        # selenium returns different objects every time find_element is called
        parent_node = parent.get()
        assert parent_node.tag_name == "body"

    def test_parent_return_none_when_root_node(self, driver_selenium: WebDriver):
        """Tests if `parent` property returns None if element is root node."""
        text = """
            <div>
                <p>Hello</p>
                <p>World</p>
                <span><p>Hi</p><a>Earth</a></span>
            </div>
        """
        insert(text, driver=driver_selenium)
        node = driver_selenium.execute_script(
            "return arguments[0].parentNode;",
            driver_selenium.find_element(By.TAG_NAME, "html"),
        )
        element = SeleniumElement(node)

        parent = element.parent
        assert parent is None

    @pytest.mark.integration
    def test_css_api_works_properly(self, driver_selenium: WebDriver):
        """
        Tests if `css` method returns `SeleniumCSSApi` object correctly initialized
        which select elements properly returning list of `SeleniumElement` objects.
        """
        text = """
            <div>
                <p class="widget">Hello</p>
                <p class="menu">World</p>
                <span><p>Hi</p><a>Earth</a></span>
            </div>
            <p class="widget">Hi</p>
        """
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "html")
        element = SeleniumElement(node)

        api = element.css("p.widget")
        assert isinstance(api, SeleniumCSSApi)

        result = api.select(element)
        assert all(isinstance(element, SeleniumElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<p class="widget">Hello</p>""",
            """<p class="widget">Hi</p>""",
        ]

    @pytest.mark.integration
    def test_xpath_api_works_properly(self, driver_selenium: WebDriver):
        """
        Tests if `xpath` method returns `SeleniumXPathApi` object correctly initialized
        which select elements properly returning list of `SeleniumElement` objects.
        """
        text = """
            <div>
                <p class="widget">Hello</p>
                <span><span>Hi</span><a>Earth</a></span>
            </div>
            <p class="widget">Hi</p>
        """
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "html")
        element = SeleniumElement(node)

        api = element.xpath(".//p")
        assert isinstance(api, SeleniumXPathApi)

        result = api.select(element)
        assert all(isinstance(element, SeleniumElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<p class="widget">Hello</p>""",
            """<p class="widget">Hi</p>""",
        ]

    def test_finds_all_ancestors_of_element_in_order(self, driver_selenium: WebDriver):
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
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "a")

        element = SeleniumElement(node)
        ancestors = element.find_ancestors()

        assert all(isinstance(element, SeleniumElement) for element in ancestors)
        # selenium adds head elements arbitrarily
        assert [strip(str(x)).replace("<head></head>", "") for x in ancestors] == [
            "<p><a>Hello</a></p>",
            "<span><p><a>Hello</a></p></span>",
            """<div><p class="widget">Hello</p><span><p><a>Hello</a></p></span></div>""",
            """<body><div><p class="widget">Hello</p><span><p><a>Hello</a></p></span></div></body>""",
            """<html><body><div><p class="widget">Hello</p><span><p><a>Hello</a></p></span></div></body></html>""",
        ]

    def test_finds_ancestors_with_limit(self, driver_selenium: WebDriver):
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
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "a")

        element = SeleniumElement(node)
        ancestors = element.find_ancestors(limit=2)

        assert all(isinstance(element, SeleniumElement) for element in ancestors)
        assert [strip(str(x)) for x in ancestors] == [
            "<p><a>Hello</a></p>",
            "<span><p><a>Hello</a></p></span>",
        ]

    def test_find_ancestors_returns_empty_list_if_root_element(
        self, driver_selenium: WebDriver
    ):
        """Tests if `find_ancestors` method returns empty list if element is root."""
        text = """
            <div>
                <p class="widget">Hello</p>
                <span><p><a>Hello</a></p></span>
            </div>
        """
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.CSS_SELECTOR, ":root")

        element = SeleniumElement(node)
        assert element.find_ancestors() == []

    def test_finds_all_subsequent_siblings_of_element(self, driver_selenium: WebDriver):
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
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "span")

        element = SeleniumElement(node)
        siblings = element.find_subsequent_siblings()

        assert all(isinstance(element, SeleniumElement) for element in siblings)
        assert [strip(str(x)) for x in siblings] == [
            "<p><a>World</a></p>",
            "<span>Earth</span>",
            "<h1>Nice</h1>",
        ]

    def test_finds_all_subsequent_returns_empty_list_if_last_child(
        self, driver_selenium: WebDriver
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
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "span")

        element = SeleniumElement(node)
        assert element.find_subsequent_siblings() == []

    def test_finds_all_subsequent_with_limit(self, driver_selenium: WebDriver):
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
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "span")

        element = SeleniumElement(node)
        siblings = element.find_subsequent_siblings(limit=2)

        assert all(isinstance(element, SeleniumElement) for element in siblings)
        assert [strip(str(x)) for x in siblings] == [
            "<p><a>World</a></p>",
            "<span>Earth</span>",
        ]

    def test_finds_all_elements_when_no_specifications(
        self, driver_selenium: WebDriver
    ):
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
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "body")

        element = SeleniumElement(node)
        result = element.find_all()

        assert all(isinstance(element, SeleniumElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<div><p class="widget">Hello</p><p><a>World</a></p></div>""",
            """<p class="widget">Hello</p>""",
            """<p><a>World</a></p>""",
            """<a>World</a>""",
            """<span>Hi</span>""",
        ]

    def test_finds_all_returns_list_of_children_when_recursive_false(
        self, driver_selenium: WebDriver
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
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "body")

        element = SeleniumElement(node)
        result = element.find_all(recursive=False)

        assert all(isinstance(element, SeleniumElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<div><p class="widget">Hello</p><p><a>World</a></p></div>""",
            """<span>Hi</span>""",
        ]

    def test_finds_all_elements_with_limit(self, driver_selenium: WebDriver):
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
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "body")

        element = SeleniumElement(node)
        result = element.find_all(limit=3)

        assert all(isinstance(element, SeleniumElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<div><p class="widget">Hello</p><p><a>World</a></p></div>""",
            """<p class="widget">Hello</p>""",
            """<p><a>World</a></p>""",
        ]

    def test_finds_all_elements_with_limit_and_recursive_false(
        self, driver_selenium: WebDriver
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
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "body")

        element = SeleniumElement(node)
        result = element.find_all(limit=2, recursive=False)

        assert all(isinstance(element, SeleniumElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<div><p class="widget">Hello</p><span><h1>World</h1></span></div>""",
            """<span>Hi</span>""",
        ]

    def test_finds_all_returns_empty_list_if_nothing_matches(
        self, driver_selenium: WebDriver
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
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "html")
        element = SeleniumElement(node)

        result = element.find_all(name="h2")
        assert result == []

    def test_finds_all_returns_empty_list_if_nothing_matches_and_recursive_false(
        self, driver_selenium: WebDriver
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
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "html")
        element = SeleniumElement(node)

        result = element.find_all(name="h2", recursive=False)
        assert result == []

    def test_finds_all_elements_with_specific_name(self, driver_selenium: WebDriver):
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
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "html")
        element = SeleniumElement(node)
        result = element.find_all(name="p")

        assert all(isinstance(element, SeleniumElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<p class="widget">Hello</p>""",
            """<p><a>World</a></p>""",
        ]

    def test_finds_all_elements_with_specific_name_and_recursive_false(
        self, driver_selenium: WebDriver
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
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "body")

        element = SeleniumElement(node)
        result = element.find_all(name="span", recursive=False)

        assert all(isinstance(element, SeleniumElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<span>Hi</span>""",
            """<span><p>World</p></span>""",
        ]

    def test_finds_all_elements_with_exact_attribute_match(
        self, driver_selenium: WebDriver
    ):
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
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "html")
        element = SeleniumElement(node)
        result = element.find_all(attrs={"class": "widget"})

        assert all(isinstance(element, SeleniumElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<p class="widget">Hello</p>""",
            """<span class="widget">Hi</span>""",
        ]

    def test_finds_all_elements_with_regex_attribute_match(
        self, driver_selenium: WebDriver
    ):
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
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "html")
        element = SeleniumElement(node)
        result = element.find_all(attrs={"class": re.compile("widget")})

        assert all(isinstance(element, SeleniumElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<p class="widget123">Hello</p>""",
            """<span class="widget menu">Hi</span>""",
            """<span class="menu your_widget">Hello</span>""",
        ]

    def test_finds_all_elements_with_matching_multiple_attributes(
        self, driver_selenium: WebDriver
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
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "html")
        element = SeleniumElement(node)
        result = element.find_all(attrs={"class": "widget", "name": "menu"})

        assert all(isinstance(element, SeleniumElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<h1 class="widget" name="menu">Welcome</h1>"""
        ]

    def test_finds_all_elements_with_matching_attributes_and_name(
        self, driver_selenium: WebDriver
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
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "html")
        element = SeleniumElement(node)
        result = element.find_all(name="span", attrs={"class": "widget"})

        assert all(isinstance(element, SeleniumElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<span class="widget">Hi</span>""",
            """<span class="widget">Hello</span>""",
        ]

    def test_finds_all_elements_with_matching_attributes_and_name_with_limit_and_recursive_false(
        self, driver_selenium: WebDriver
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
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "body")
        assert node is not None

        element = SeleniumElement(node)
        result = element.find_all(
            name="span",
            attrs={"class": "widget"},
            recursive=False,
            limit=1,
        )

        assert all(isinstance(element, SeleniumElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<span class="widget">Welcome</span>""",
        ]

    def test_get_attribute_returns_specific_attribute_value(
        self, driver_selenium: WebDriver
    ):
        """Tests if `get_attribute` method returns specific attribute value."""
        text = """
            <div name="menu">
                <p class="widget">Hello</p>
                <p><a>World</a></p>
            </div>
            <span class="widget">Hi</span>
        """
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "div")

        element = SeleniumElement(node)
        result = element.get_attribute("name")
        assert result == "menu"

    def test_get_attribute_returns_string_for_class(self, driver_selenium: WebDriver):
        """Tests if `get_attribute` method returns string for class attribute."""
        text = """
            <div class="menu widget">
                <p class="widget">Hello</p>
                <p><a>World</a></p>
            </div>
            <span class="widget">Hi</span>
        """
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "div")

        element = SeleniumElement(node)
        result = element.get_attribute("class")
        assert result == "menu widget"

    def test_get_attribute_returns_changed_attribute(self, driver_selenium: WebDriver):
        """
        Tests if `get_attribute` method returns value after it is changed.
        Asserts that internally element uses `get_attribute` method
        and not `get_dom_attribute` which would not reflect changes.
        """
        text = """
            <input id="editable" type="text" value="original" />
        """
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.ID, "editable")
        element = SeleniumElement(node)

        assert element.get_attribute("value") == "original"

        node.clear()
        node.send_keys("changed")

        assert element.get_attribute("value") == "changed"


class FakeDriver:
    """A fake WebDriver for simulating errors & redirects."""

    def __init__(self):
        self._url = None
        self.closed = False

    def get(self, url: str):
        if url == "http://bad-url":
            raise selenium_exceptions.WebDriverException("Failed to connect")
        if url == "http://redirect":
            self._url = "http://final-url"
        else:
            self._url = url

    def quit(self):
        self.closed = True

    @property
    def current_url(self):
        return self._url


@pytest.fixture
def fake_driver(monkeypatch: MonkeyPatch) -> FakeDriver:
    """Provides a fake WebDriver instance for testing."""
    monkeypatch.setattr(SeleniumBrowser, "_BROWSER_TYPE", FakeDriver)
    return FakeDriver()


def get_driver() -> WebDriver:
    """Creates a basic selenium webdriver instance for testing."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    return driver


@pytest.mark.selenium
@pytest.mark.implementation
class TestSeleniumBrowser:

    def test_initializes_with_driver(self, driver_selenium: WebDriver):
        """Tests if `SeleniumBrowser` can be initialized with selenium webdriver."""
        browser = SeleniumBrowser(driver_selenium)
        assert browser.browser is driver_selenium
        assert browser.get() is driver_selenium

    def test_raises_exception_when_invalid_init_browser(self):
        """
        Tests if TypeError is raised when object of invalid type
        is passed to constructor.
        """
        with pytest.raises(TypeError):
            SeleniumBrowser("mouse")

    def test_navigate_success(self, fake_driver: FakeDriver):
        """Simulates navigation working normally."""

        browser = SeleniumBrowser(fake_driver)
        browser.navigate("http://ok")
        assert browser.get_current_url() == "http://ok"

    def test_navigate_redirect(self, fake_driver: FakeDriver):
        """Simulates a redirect after navigation."""
        browser = SeleniumBrowser(fake_driver)
        browser.navigate("http://redirect")
        assert browser.get_current_url() == "http://final-url"

    def test_navigate_connection_error(self, fake_driver: FakeDriver):
        """Simulates a connection error during navigation."""
        browser = SeleniumBrowser(fake_driver)

        with pytest.raises(selenium_exceptions.WebDriverException):
            browser.navigate("http://bad-url")

    def test_keys_are_send_properly(self, driver_selenium: WebDriver):
        """
        Tests if `send_keys` method sends keys properly to the element
        and value of the element is changed accordingly.
        """
        to_insert = "Hello World"
        text = """<input id="editable" type="text" />"""
        insert(text, driver=driver_selenium)

        browser = SeleniumBrowser(driver_selenium)
        element = SeleniumElement(driver_selenium.find_element(By.ID, "editable"))

        browser.send_keys(element=element, value=to_insert)
        assert element.get_attribute("value") == to_insert

    def test_keys_are_not_cleared_when_clear_false(self, driver_selenium: WebDriver):
        """
        Tests if `send_keys` method does not clear the element before sending keys
        when `clear` parameter is set to False.
        """
        text = """<input id="editable" type="text" value="original" />"""
        insert(text, driver=driver_selenium)

        browser = SeleniumBrowser(driver_selenium)
        element = SeleniumElement(driver_selenium.find_element(By.ID, "editable"))

        browser.send_keys(element=element, value="Hello")
        assert element.get_attribute("value") == "Hello"

        browser.send_keys(element=element, value=" World", clear=False)
        assert element.get_attribute("value") == "Hello World"

    def test_can_send_special_keys(self, driver_selenium: WebDriver):
        """
        Tests if `send_keys` method can send special keys like ENTER.
        """
        text = """<input id="editable" type="text" value="original" />"""
        insert(text, driver=driver_selenium)

        browser = SeleniumBrowser(driver_selenium)
        element = SeleniumElement(driver_selenium.find_element(By.ID, "editable"))

        browser.send_keys(element, "Hello" + Keys.ENTER)
        assert element.get_attribute("value") == "Hello"

    def test_sends_key_only_to_specified_element(self, driver_selenium: WebDriver):
        """
        Tests if `send_keys` method sends keys only to the specified element.
        Other elements are not affected.
        """
        text = """
            <input id="one" type="text" />
            <input id="two" type="text" />
        """
        insert(text, driver=driver_selenium)

        el1 = SeleniumElement(driver_selenium.find_element(By.ID, "one"))
        el2 = SeleniumElement(driver_selenium.find_element(By.ID, "two"))

        browser = SeleniumBrowser(driver_selenium)
        browser.send_keys(el1, "First")

        assert el1.get_attribute("value") == "First"
        assert el2.get_attribute("value") == ""

    def test_raises_error_when_element_is_not_editable(
        self, driver_selenium: WebDriver
    ):
        """
        Tests if `send_keys` method raises an error when the element is not editable.
        """
        text = """
            <div>Hello</div>
            <p>World</p>
        """
        insert(text, driver=driver_selenium)

        node = driver_selenium.find_element(By.TAG_NAME, "div")
        element = SeleniumElement(node)
        browser = SeleniumBrowser(driver_selenium)

        with pytest.raises(selenium_exceptions.InvalidElementStateException):
            browser.send_keys(element, "First")

    def test_closes_browser_properly(self, fake_driver: FakeDriver):
        """
        Tests if `close` method calls `quit` on the webdriver.
        Uses mock driver to avoid actually closing the browser during tests.
        """
        browser = SeleniumBrowser(fake_driver)
        assert fake_driver.closed is False
        browser.close()
        assert fake_driver.closed is True

    def test_clicks_element_properly(self, driver_selenium: WebDriver):
        """
        Tests if `click` method clicks the element properly
        and the click event is reflected in the page.
        """
        text = """
            <button id="myButton" onclick="this.innerText='Clicked'">Not clicked</button>
        """
        insert(text, driver=driver_selenium)
        browser = SeleniumBrowser(driver_selenium)
        element = SeleniumElement(driver_selenium.find_element(By.TAG_NAME, "button"))

        assert element.text == "Not clicked"
        browser.click(element)
        assert element.text == "Clicked"

    def test_click_element_covered_by_other(self, driver_selenium: WebDriver):
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
        insert(html, driver=driver_selenium)

        browser = SeleniumBrowser(driver_selenium)
        node = driver_selenium.find_element(By.ID, "target")

        element = SeleniumElement(node)
        assert element.text == "Not clicked"

        with pytest.raises(selenium_exceptions.ElementClickInterceptedException):
            node.click()

        # Your click method bypasses visibility
        browser.click(element)
        assert element.text == "Clicked"

    def test_click_triggers_navigation(self, driver_selenium: WebDriver):
        """Tests if `click` method triggers navigation when clicking a link."""
        text = """<a id="myLink" href="about:blank">Go</a>"""
        insert(text, driver=driver_selenium)

        browser = SeleniumBrowser(driver_selenium)
        element = SeleniumElement(driver_selenium.find_element(By.ID, "myLink"))

        browser.click(element)
        assert browser.get_current_url() == "about:blank"

    def test_multiple_clicks_work_properly(self, driver_selenium: WebDriver):
        """
        Tests if `click` method can be called multiple times on the same element.
        """
        text = """<button id="counter" onclick="this.innerText=parseInt(this.innerText)+1">0</button>"""
        insert(text, driver=driver_selenium)
        browser = SeleniumBrowser(driver_selenium)
        element = SeleniumElement(driver_selenium.find_element(By.ID, "counter"))

        for _ in range(3):
            browser.click(element)

        assert element.text == "3"

    def test_get_html_returns_html_element(self, driver_selenium: WebDriver):
        """
        Tests if `get_html` method returns html element of the page
        wrapped in `SeleniumElement`.
        """
        text = """
            <div>Hello</div>
            <p>World</p>
        """
        insert(text, driver=driver_selenium)
        browser = SeleniumBrowser(driver_selenium)
        body = browser.get_document()

        assert isinstance(body, SeleniumElement)
        assert body.name == "html"

    def test_hash_is_based_on_instance_id(self):
        """
        Tests if `__hash__` method returns hash based on instance id.
        """
        driver1 = get_driver()
        driver2 = get_driver()
        browser1 = SeleniumBrowser(driver1)
        browser2 = SeleniumBrowser(driver1)
        browser3 = SeleniumBrowser(driver2)

        assert hash(browser1) == hash(browser2)
        assert hash(browser1) != hash(browser3)

    def test_instances_are_equal_if_they_have_the_same_driver(self):
        """
        Tests if `__eq__` method returns True if two instances
        have the same webdriver instance.
        """
        driver1 = get_driver()
        driver2 = get_driver()
        browser1 = SeleniumBrowser(driver1)
        browser2 = SeleniumBrowser(driver1)
        browser3 = SeleniumBrowser(driver2)

        assert browser1 == browser2
        assert browser1 != browser3
