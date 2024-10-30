import pytest
from lxml.etree import XPath

from soupsavvy.exceptions import InvalidXPathSelector
from soupsavvy.implementation.lxml import LXMLElement
from soupsavvy.selectors.xpath.api import LXMLXpathApi, SeleniumXPathApi
from tests.soupsavvy.conftest import ToElement, strip


@pytest.mark.selenium
class TestSeleniumXPathApi:
    def test(self, to_element: ToElement):
        text = """
            <div></div>
            <div class="widget123">
                <span><a>Not child</a></span>
            </div>
            <a class="widget"></a>
            <div><a>1</a></div>
            <span>
                <a class="widget"></a>
                <div><a><h1>2</h1></a><h1>Hello</h1></div>
            </span>
            <div class="widget123"><a>3</a></div>
            <div class="widget"><p>Hello</p></div>
        """
        bs = to_element(text)
        api = SeleniumXPathApi("//div/a")
        result = api.select(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a>1</a>"""),
            strip("""<a><h1>2</h1></a>"""),
            strip("""<a>3</a>"""),
        ]


@pytest.mark.lxml
class TestLXMLXPathApi:
    """Class with unit tests for LXMLXpathApi."""

    def test_raises_exception_when_invalid_selector(self):
        """
        Tests if InvalidXPathSelector exception is raised when initializing
        with invalid xpath selector.
        """
        with pytest.raises(InvalidXPathSelector):
            LXMLXpathApi("div.menu ? a")

    def test_selects_all_elements_matching_selector(self, to_element: ToElement):
        """Tests if all elements matching selector are selected."""
        text = """
            <div></div>
            <div class="widget123">
                <span><a>Not child</a></span>
            </div>
            <a class="widget"></a>
            <div><a>1</a></div>
            <span>
                <a class="widget"></a>
                <div><a><h1>2</h1></a><h1>Hello</h1></div>
            </span>
            <div class="widget123"><a>3</a></div>
            <div class="widget"><p>Hello</p></div>
        """
        bs = to_element(text)
        api = LXMLXpathApi("//div/a")
        result = api.select(bs)

        assert all(isinstance(x, LXMLElement) for x in result)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a>1</a>"""),
            strip("""<a><h1>2</h1></a>"""),
            strip("""<a>3</a>"""),
        ]

    def test_works_correctly_with_compiled_xpath(self, to_element: ToElement):
        """
        Tests if selector works correctly with compiled XPath expression
        passed to initializer and returns first matching element.
        """
        text = """
            <div></div>
            <div class="widget123">
                <span><a>Not child</a></span>
            </div>
            <a class="widget"></a>
            <div><a>1</a></div>
            <span>
                <a class="widget"></a>
                <div><a><h1>2</h1></a><h1>Hello</h1></div>
            </span>
            <div class="widget123"><a>3</a></div>
            <div class="widget"><p>Hello</p></div>
        """
        bs = to_element(text)
        api = LXMLXpathApi(XPath("//div/a"))
        result = api.select(bs)

        assert all(isinstance(x, LXMLElement) for x in result)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a>1</a>"""),
            strip("""<a><h1>2</h1></a>"""),
            strip("""<a>3</a>"""),
        ]

    def test_expression_not_targeting_elements_does_not_find_elements(
        self, to_element: ToElement
    ):
        """
        Tests if find methods do not find any results if provided expression does not
        target elements, but attributes or text content.
        In such case, matching with corresponding bs4 elements is not possible.
        Appropriate user warning is raised.
        """
        text = """
            <div><a href="www.example.com">Hello</a></div>
        """
        bs = to_element(text)
        api = LXMLXpathApi("//div/a/@href")

        with pytest.warns(
            UserWarning,
            match="XPath expression does not target elements",
        ):
            result = api.select(bs)

        assert result == []

    def test_returns_empty_list_if_no_element_matches_selector(
        self, to_element: ToElement
    ):
        """Tests if empty list is returned when no element matches selector."""
        text = """
            <div></div>
            <div class="widget123">
                <span><a>Not child</a></span>
            </div>
            <a class="widget"></a>
            <span>
                <a class="widget"></a>
                <div><h1></h1><h1>Hello</h1></div>
            </span>
            <div class="widget"><p>Hello</p></div>
        """
        bs = to_element(text)
        api = LXMLXpathApi("//div/a")
        result = api.select(bs)
        assert result == []
