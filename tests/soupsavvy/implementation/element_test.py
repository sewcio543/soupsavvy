import pytest
from bs4 import BeautifulSoup
from lxml.etree import fromstring
from pytest import MonkeyPatch
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from soupsavvy.implementation.bs4 import SoupElement
from soupsavvy.implementation.element import to_soupsavvy
from soupsavvy.implementation.lxml import LXMLElement
from soupsavvy.implementation.selenium import SeleniumElement
from tests.soupsavvy.conftest import insert


def mock_raise_import_error(name, *args, **kwargs):
    raise ImportError


class TestToSoupsavvy:
    def test_returns_if_input_is_soup_element(self):
        text = "<html><body><p>Test</p></body></html>"
        soup = BeautifulSoup(text, parser="lxml")
        element = SoupElement(soup)
        result = to_soupsavvy(element)
        assert result is element

    def test_returns_if_input_is_lxml_element(self):
        text = "<html><body><p>Test</p></body></html>"
        node = fromstring(text)
        element = LXMLElement(node)
        result = to_soupsavvy(element)
        assert result is element

    def test_returns_if_input_is_selenium_element(self, driver: WebDriver):
        text = "<html><body><p>Test</p></body></html>"
        insert(text, driver=driver)
        node = driver.find_element(By.TAG_NAME, "html")
        element = SeleniumElement(node)
        result = to_soupsavvy(element)
        assert result is element

    def test_converts_to_soup_element(self):
        text = "<html><body><p>Test</p></body></html>"
        soup = BeautifulSoup(text, parser="lxml")
        element = to_soupsavvy(soup)
        assert isinstance(element, SoupElement)

    def test_converts_to_lxml_element(self):
        text = "<html><body><p>Test</p></body></html>"
        node = fromstring(text)
        element = to_soupsavvy(node)
        assert isinstance(element, LXMLElement)

    def test_converts_to_selenium_element(self, driver: WebDriver):
        text = "<html><body><p>Test</p></body></html>"
        insert(text, driver=driver)
        node = driver.find_element(By.TAG_NAME, "html")
        element = to_soupsavvy(node)
        assert isinstance(element, SeleniumElement)

    def test_raises_error_if_no_bs4_dependency(self, monkeypatch: MonkeyPatch):
        monkeypatch.setattr("importlib.import_module", mock_raise_import_error)

        text = "<html><body><p>Test</p></body></html>"
        soup = BeautifulSoup(text, parser="lxml")

        with pytest.raises(TypeError):
            to_soupsavvy(soup)

    def test_raises_error_if_no_lxml_dependency(self, monkeypatch: MonkeyPatch):
        monkeypatch.setattr("importlib.import_module", mock_raise_import_error)

        text = "<html><body><p>Test</p></body></html>"
        node = fromstring(text)

        with pytest.raises(TypeError):
            to_soupsavvy(node)

    def test_raises_error_if_no_selenium_dependency(
        self, driver: WebDriver, monkeypatch: MonkeyPatch
    ):
        monkeypatch.setattr("importlib.import_module", mock_raise_import_error)

        text = "<html><body><p>Test</p></body></html>"
        insert(text, driver=driver)
        node = driver.find_element(By.TAG_NAME, "html")

        with pytest.raises(TypeError):
            to_soupsavvy(node)

    def test_raises_error_when_invalid_input(self):
        text = "<html><body><p>Test</p></body></html>"

        with pytest.raises(TypeError):
            to_soupsavvy(text)
