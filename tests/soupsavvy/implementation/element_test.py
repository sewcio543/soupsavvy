import pytest
from bs4 import BeautifulSoup
from lxml.etree import fromstring
from playwright.sync_api import Page
from pytest import MonkeyPatch
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from soupsavvy.implementation.bs4 import SoupElement
from soupsavvy.implementation.element import to_soupsavvy
from soupsavvy.implementation.lxml import LXMLElement
from soupsavvy.implementation.playwright import PlaywrightElement
from soupsavvy.implementation.selenium import SeleniumElement
from tests.soupsavvy.conftest import insert


def mock_raise_import_error(name, *args, **kwargs):
    raise ImportError


@pytest.mark.implementation
class TestToSoupsavvy:
    @pytest.mark.bs4
    def test_returns_if_input_is_soup_element(self):
        text = "<html><body><p>Test</p></body></html>"
        soup = BeautifulSoup(text, parser="lxml")
        element = SoupElement(soup)
        result = to_soupsavvy(element)
        assert result is element

    @pytest.mark.lxml
    def test_returns_if_input_is_lxml_element(self):
        text = "<html><body><p>Test</p></body></html>"
        node = fromstring(text)
        element = LXMLElement(node)
        result = to_soupsavvy(element)
        assert result is element

    @pytest.mark.selenium
    def test_returns_if_input_is_selenium_element(self, driver_selenium: WebDriver):
        text = "<html><body><p>Test</p></body></html>"
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "html")
        element = SeleniumElement(node)
        result = to_soupsavvy(element)
        assert result is element

    @pytest.mark.playwright
    def test_returns_if_input_is_playwright_element(self, playwright_page: Page):
        text = "<html><body><p>Test</p></body></html>"
        playwright_page.set_content(text)
        node = playwright_page.query_selector("html")
        assert node is not None

        element = PlaywrightElement(node)
        result = to_soupsavvy(element)
        assert result is element

    @pytest.mark.bs4
    def test_converts_to_soup_element(self):
        text = "<html><body><p>Test</p></body></html>"
        soup = BeautifulSoup(text, parser="lxml")
        element = to_soupsavvy(soup)
        assert isinstance(element, SoupElement)

    @pytest.mark.lxml
    def test_converts_to_lxml_element(self):
        text = "<html><body><p>Test</p></body></html>"
        node = fromstring(text)
        element = to_soupsavvy(node)
        assert isinstance(element, LXMLElement)

    @pytest.mark.selenium
    def test_converts_to_selenium_element(self, driver_selenium: WebDriver):
        text = "<html><body><p>Test</p></body></html>"
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "html")
        element = to_soupsavvy(node)
        assert isinstance(element, SeleniumElement)

    @pytest.mark.playwright
    def test_converts_to_playwright_element(self, playwright_page: Page):
        text = "<html><body><p>Test</p></body></html>"
        playwright_page.set_content(text)
        node = playwright_page.query_selector("html")
        assert node is not None

        element = to_soupsavvy(node)
        assert isinstance(element, PlaywrightElement)

    @pytest.mark.bs4
    def test_raises_error_if_no_bs4_dependency(self, monkeypatch: MonkeyPatch):
        monkeypatch.setattr("importlib.import_module", mock_raise_import_error)

        text = "<html><body><p>Test</p></body></html>"
        soup = BeautifulSoup(text, parser="lxml")

        with pytest.raises(TypeError):
            to_soupsavvy(soup)

    @pytest.mark.lxml
    def test_raises_error_if_no_lxml_dependency(self, monkeypatch: MonkeyPatch):
        monkeypatch.setattr("importlib.import_module", mock_raise_import_error)

        text = "<html><body><p>Test</p></body></html>"
        node = fromstring(text)

        with pytest.raises(TypeError):
            to_soupsavvy(node)

    @pytest.mark.selenium
    def test_raises_error_if_no_selenium_dependency(
        self, driver_selenium: WebDriver, monkeypatch: MonkeyPatch
    ):
        monkeypatch.setattr("importlib.import_module", mock_raise_import_error)

        text = "<html><body><p>Test</p></body></html>"
        insert(text, driver=driver_selenium)
        node = driver_selenium.find_element(By.TAG_NAME, "html")

        with pytest.raises(TypeError):
            to_soupsavvy(node)

    @pytest.mark.playwright
    def test_raises_error_if_no_playwright_dependency(
        self, playwright_page: Page, monkeypatch: MonkeyPatch
    ):
        monkeypatch.setattr("importlib.import_module", mock_raise_import_error)

        text = "<html><body><p>Test</p></body></html>"
        playwright_page.set_content(text)
        node = playwright_page.query_selector("html")
        assert node is not None

        with pytest.raises(TypeError):
            to_soupsavvy(node)

    def test_raises_error_when_invalid_input(self):
        text = "<html><body><p>Test</p></body></html>"

        with pytest.raises(TypeError):
            to_soupsavvy(text)
