import pytest

from soupsavvy.exceptions import InvalidCSSSelector
from soupsavvy.implementation.bs4 import SoupElement
from soupsavvy.implementation.lxml import LXMLElement
from soupsavvy.implementation.playwright import PlaywrightElement
from soupsavvy.implementation.selenium import SeleniumElement
from soupsavvy.selectors.css.api import (
    CSSSelectApi,
    PlaywrightCSSApi,
    SeleniumCSSApi,
    SoupsieveApi,
)
from tests.soupsavvy.conftest import ToElement, strip

# TODO: clean up repetitive tests


@pytest.mark.lxml
class TestCSSSelectApi:
    """Class with unit tests for CSSSelectApi."""

    def test_raises_exception_when_invalid_selector(self):
        """
        Tests if InvalidCSSSelector exception is raised when initializing
        with invalid css selector.
        """
        with pytest.raises(InvalidCSSSelector):
            CSSSelectApi("div[1]")

    def test_selects_all_elements_matching_selector(self, to_element: ToElement):
        """Tests if all elements matching selector are selected."""
        text = """
            <div></div>
            <div class="widget123"></div>
            <a class="widget"></a>
            <div class="widget">1</div>
            <span>
                <div id="widget"></div>
                <div class="widget">2</div>
            </span>
            <div class="widget"><p>3</p></div>
        """
        bs = to_element(text)
        api = CSSSelectApi("div.widget")

        result = api.select(bs)

        assert all(isinstance(x, LXMLElement) for x in result)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div class="widget">1</div>"""),
            strip("""<div class="widget">2</div>"""),
            strip("""<div class="widget"><p>3</p></div>"""),
        ]

    def test_returns_empty_list_if_no_element_matches_selector(
        self, to_element: ToElement
    ):
        """Tests if empty list is returned when no element matches selector."""
        text = """
            <div></div>
            <div class="widget123"></div>
            <a class="widget"></a>
            <span>
                <div id="widget"></div>
            </span>
            <span class="widget"></span>
        """
        bs = to_element(text)
        api = CSSSelectApi("div.widget")
        result = api.select(bs)
        assert result == []


@pytest.mark.bs4
class TestSoupsieveApi:
    """Class with unit tests for SoupsieveApi."""

    def test_raises_exception_when_invalid_selector(self):
        """
        Tests if InvalidCSSSelector exception is raised when initializing
        with invalid css selector.
        """
        with pytest.raises(InvalidCSSSelector):
            SoupsieveApi("div[1]")

    def test_selects_all_elements_matching_selector(self, to_element: ToElement):
        """Tests if all elements matching selector are selected."""
        text = """
            <div></div>
            <div class="widget123"></div>
            <a class="widget"></a>
            <div class="widget">1</div>
            <span>
                <div id="widget"></div>
                <div class="widget">2</div>
            </span>
            <div class="widget"><p>3</p></div>
        """
        bs = to_element(text)
        api = SoupsieveApi("div.widget")

        result = api.select(bs)

        assert all(isinstance(x, SoupElement) for x in result)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div class="widget">1</div>"""),
            strip("""<div class="widget">2</div>"""),
            strip("""<div class="widget"><p>3</p></div>"""),
        ]

    def test_returns_empty_list_if_no_element_matches_selector(
        self, to_element: ToElement
    ):
        """Tests if empty list is returned when no element matches selector."""
        text = """
            <div></div>
            <div class="widget123"></div>
            <a class="widget"></a>
            <span>
                <div id="widget"></div>
            </span>
            <span class="widget"></span>
        """
        bs = to_element(text)
        api = SoupsieveApi("div.widget")
        result = api.select(bs)
        assert result == []


@pytest.mark.selenium
class TestSeleniumCSSApi:
    """Class with unit tests for SeleniumCSSApi."""

    def test_raises_exception_when_invalid_selector(self, to_element: ToElement):
        """
        Tests if InvalidCSSSelector exception is raised when selecting elements
        with invalid css selector.
        """
        text = """
            <div></div>
            <a class="widget"></a>
        """
        bs = to_element(text)
        api = SeleniumCSSApi("div[1]")

        with pytest.raises(InvalidCSSSelector):
            api.select(bs)

    def test_selects_all_elements_matching_selector(self, to_element: ToElement):
        """Tests if all elements matching selector are selected."""
        text = """
            <div></div>
            <div class="widget123"></div>
            <a class="widget"></a>
            <div class="widget">1</div>
            <span>
                <div id="widget"></div>
                <div class="widget">2</div>
            </span>
            <div class="widget"><p>3</p></div>
        """
        bs = to_element(text)
        api = SeleniumCSSApi("div.widget")

        result = api.select(bs)

        assert all(isinstance(x, SeleniumElement) for x in result)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div class="widget">1</div>"""),
            strip("""<div class="widget">2</div>"""),
            strip("""<div class="widget"><p>3</p></div>"""),
        ]

    def test_returns_empty_list_if_no_element_matches_selector(
        self, to_element: ToElement
    ):
        """Tests if empty list is returned when no element matches selector."""
        text = """
            <div></div>
            <div class="widget123"></div>
            <a class="widget"></a>
            <span>
                <div id="widget"></div>
            </span>
            <span class="widget"></span>
        """
        bs = to_element(text)
        api = SeleniumCSSApi("div.widget")
        result = api.select(bs)
        assert result == []


@pytest.mark.playwright
class TestPlaywrightCSSApi:
    """Class with unit tests for PlaywrightCSSApi."""

    def test_raises_exception_when_invalid_selector(self, to_element: ToElement):
        """
        Tests if InvalidCSSSelector exception is raised when selecting elements
        with invalid css selector.
        """
        text = """
            <div></div>
            <a class="widget"></a>
        """
        bs = to_element(text)
        api = PlaywrightCSSApi("div[1]")

        with pytest.raises(InvalidCSSSelector):
            api.select(bs)

    def test_selects_all_elements_matching_selector(self, to_element: ToElement):
        """Tests if all elements matching selector are selected."""
        text = """
            <div></div>
            <div class="widget123"></div>
            <a class="widget"></a>
            <div class="widget">1</div>
            <span>
                <div id="widget"></div>
                <div class="widget">2</div>
            </span>
            <div class="widget"><p>3</p></div>
        """
        bs = to_element(text)
        api = PlaywrightCSSApi("div.widget")

        result = api.select(bs)

        assert all(isinstance(x, PlaywrightElement) for x in result)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div class="widget">1</div>"""),
            strip("""<div class="widget">2</div>"""),
            strip("""<div class="widget"><p>3</p></div>"""),
        ]

    def test_returns_empty_list_if_no_element_matches_selector(
        self, to_element: ToElement
    ):
        """Tests if empty list is returned when no element matches selector."""
        text = """
            <div></div>
            <div class="widget123"></div>
            <a class="widget"></a>
            <span>
                <div id="widget"></div>
            </span>
            <span class="widget"></span>
        """
        bs = to_element(text)
        api = PlaywrightCSSApi("div.widget")
        result = api.select(bs)
        assert result == []
