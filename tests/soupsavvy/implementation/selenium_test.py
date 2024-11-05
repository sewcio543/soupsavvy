import pytest
from selenium.webdriver.common.by import By

from soupsavvy.implementation.selenium import SeleniumElement
from soupsavvy.selectors.css.api import SeleniumCSSApi
from soupsavvy.selectors.xpath.api import SeleniumXPathApi
from tests.soupsavvy.conftest import get_driver, strip

driver = get_driver()


def insert(html):
    driver.execute_script("document.body.outerHTML = arguments[0];", html)


@pytest.mark.selenium
@pytest.mark.implementation
class TestSeleniumElement:
    def test_node(self):
        text = """
            <div>Hello</div>
        """
        insert(text)
        node = driver.find_element(By.TAG_NAME, "html")
        element = SeleniumElement(node)

        assert element.node is node
        assert element.get() is node

    def test_node1(self):
        text = """
            <div>Hello</div>
        """
        insert(text)
        node = driver.find_element(By.TAG_NAME, "html")
        element = SeleniumElement.from_node(node)

        assert element.node is node
        assert element.get() is node

    def test_node2(self):
        text = """
            <div>Hello</div>
        """
        insert(text)
        node = driver.find_element(By.TAG_NAME, "html")
        element = SeleniumElement(node)

        assert repr(element) == f"SeleniumElement({node!r})"

    def test_node3(self):
        text = """
            <div>Hello</div>
        """
        insert(text)
        node = driver.find_element(By.TAG_NAME, "html")
        element = SeleniumElement(node)

        assert hash(element) == hash(node)

    def test_eq(self):
        text = """
            <div><p>Hello</p></div>
        """
        insert(text)
        node = driver.find_element(By.TAG_NAME, "html")
        element = SeleniumElement(node)

        assert element == SeleniumElement(node)
        assert element != SeleniumElement(node.find_element(By.TAG_NAME, "body"))
        assert element != node

    def test_node4(self):
        text = """
            <div>Hello</div>
        """
        insert(text)
        div = driver.find_element(By.TAG_NAME, "div")
        element = SeleniumElement(div)

        assert element.name == "div"
        assert element.text == "Hello"

    def test_node5(self):
        text = """
            Before<div> Hello<p>\nWorld </p>.</div>After
        """
        insert(text)
        div = driver.find_element(By.TAG_NAME, "div")
        element = SeleniumElement(div)

        assert element.text == "Hello\nWorld\n."

    def test_node6(self):
        text = """
            <div>
                <p>Hello</p>
                <p>World</p>
                <span><p>Hi</p><a>Earth</a></span>
            </div>
        """
        insert(text)
        div = driver.find_element(By.TAG_NAME, "div")
        element = SeleniumElement(div)

        children = list(element.children)

        assert all(isinstance(child, SeleniumElement) for child in children)
        assert [strip(str(child)) for child in children] == [
            "<p>Hello</p>",
            "<p>World</p>",
            "<span><p>Hi</p><a>Earth</a></span>",
        ]

    def test_node7(self):
        text = """
            <div>
                <p>Hello</p>
                <p>World</p>
                <span><p><a>Hi</a><a>Hello</a></p><a>Earth</a></span>
            </div>
        """
        insert(text)
        div = driver.find_element(By.TAG_NAME, "div")
        element = SeleniumElement(div)

        descendants = list(element.descendants)

        assert all(isinstance(child, SeleniumElement) for child in descendants)
        assert [strip(str(child)) for child in descendants] == [
            "<p>Hello</p>",
            "<p>World</p>",
            "<span><p><a>Hi</a><a>Hello</a></p><a>Earth</a></span>",
            "<p><a>Hi</a><a>Hello</a></p>",
            "<a>Hi</a>",
            "<a>Hello</a>",
            "<a>Earth</a>",
        ]

    def test_node8(self):
        text = """
            <div>
                <p>Hello</p>
                <p>World</p>
                <span><p>Hi</p><a>Earth</a></span>
            </div>
        """
        insert(text)
        p = driver.find_element(By.TAG_NAME, "p")
        element = SeleniumElement(p)

        parent = element.parent

        assert isinstance(parent, SeleniumElement)
        assert (
            strip(str(parent))
            == "<div><p>Hello</p><p>World</p><span><p>Hi</p><a>Earth</a></span></div>"
        )

    def test_node9(self):
        text = """
            <div>
                <p class="widget">Hello</p>
                <p class="menu">World</p>
                <span><p>Hi</p><a>Earth</a></span>
            </div>
            <p class="widget">Hi</p>
        """
        insert(text)
        element = SeleniumElement(driver.find_element(By.TAG_NAME, "html"))
        api = element.css("p.widget")

        assert isinstance(api, SeleniumCSSApi)

        result = api.select(element)
        assert [strip(str(x)) for x in result] == [
            '<p class="widget">Hello</p>',
            '<p class="widget">Hi</p>',
        ]

    def test_xpath(self):
        text = """
            <div>
                <p class="widget">Hello</p>
                <span><p>Hi</p><a>Earth</a></span>
            </div>
            <a class="widget">Hi</a>
        """
        insert(text)
        element = SeleniumElement(driver.find_element(By.TAG_NAME, "html"))
        api = element.xpath(".//p")

        assert isinstance(api, SeleniumXPathApi)

        result = api.select(element)
        assert [strip(str(x)) for x in result] == [
            '<p class="widget">Hello</p>',
            "<p>Hi</p>",
        ]

    def test_node10(self):
        text = """
            <div>
                <p class="widget">Hello</p>
                <span><p><a>Hello</a></p></span>
            </div>
        """
        insert(text)
        element = SeleniumElement(driver.find_element(By.TAG_NAME, "a"))

        ancestors = element.find_ancestors()

        assert all(isinstance(element, SeleniumElement) for element in ancestors)
        assert [strip(str(x)) for x in ancestors][:-1] == [
            "<p><a>Hello</a></p>",
            "<span><p><a>Hello</a></p></span>",
            """<div><p class="widget">Hello</p><span><p><a>Hello</a></p></span></div>""",
            """<body><div><p class="widget">Hello</p><span><p><a>Hello</a></p></span></div></body>""",
        ]

    def test_node_limit(self):
        text = """
            <div>
                <p class="widget">Hello</p>
                <span><p><a>Hello</a></p></span>
            </div>
        """
        insert(text)
        element = SeleniumElement(driver.find_element(By.TAG_NAME, "a"))

        ancestors = element.find_ancestors(limit=2)

        assert all(isinstance(element, SeleniumElement) for element in ancestors)
        assert [strip(str(x)) for x in ancestors] == [
            "<p><a>Hello</a></p>",
            "<span><p><a>Hello</a></p></span>",
        ]

    def test_node11(self):
        text = """
            <div>
                <p class="widget">Hello</p>
                <span><p><a>Hello</a></p></span>
            </div>
        """
        insert(text)
        element = SeleniumElement(driver.find_element(By.TAG_NAME, "html"))

        assert element.find_ancestors() == []

    def test_node12(self):
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
        insert(text)
        element = SeleniumElement(driver.find_element(By.TAG_NAME, "span"))
        siblings = element.find_subsequent_siblings()

        assert all(isinstance(element, SeleniumElement) for element in siblings)
        assert [strip(str(x)) for x in siblings] == [
            "<p><a>World</a></p>",
            "<span>Earth</span>",
            "<h1>Nice</h1>",
        ]

    def test_node13(self):
        text = """
            <div>
                <p class="widget">Hello</p>
                <span class="anchor">Hello</span>
            </div>
            <span>Hi</span>
        """
        insert(text)
        element = SeleniumElement(driver.find_element(By.TAG_NAME, "span"))
        assert element.find_subsequent_siblings() == []

    def test_node14(self):
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
        insert(text)
        element = SeleniumElement(driver.find_element(By.TAG_NAME, "span"))
        siblings = element.find_subsequent_siblings(limit=2)

        assert all(isinstance(element, SeleniumElement) for element in siblings)
        assert [strip(str(x)) for x in siblings] == [
            "<p><a>World</a></p>",
            "<span>Earth</span>",
        ]

    def test_node15(self):
        text = """
            <div>
                <p class="widget">Hello</p>
                <p><a>World</a></p>
            </div>
            <span>Hi</span>
        """
        insert(text)
        body = driver.find_element(By.TAG_NAME, "body")
        element = SeleniumElement(body)

        result = element.find_all()

        assert all(isinstance(element, SeleniumElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<div><p class="widget">Hello</p><p><a>World</a></p></div>""",
            """<p class="widget">Hello</p>""",
            """<p><a>World</a></p>""",
            """<a>World</a>""",
            """<span>Hi</span>""",
        ]

    def test_node15_limit(self):
        text = """
            <div>
                <p class="widget">Hello</p>
                <p><a>World</a></p>
            </div>
            <span>Hi</span>
        """
        insert(text)
        body = driver.find_element(By.TAG_NAME, "body")
        element = SeleniumElement(body)

        result = element.find_all(limit=3)

        assert all(isinstance(element, SeleniumElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<div><p class="widget">Hello</p><p><a>World</a></p></div>""",
            """<p class="widget">Hello</p>""",
            """<p><a>World</a></p>""",
        ]

    def test_node16(self):
        text = """
            <div>
                <p class="widget">Hello</p>
                <p><a>World</a></p>
            </div>
            <span>Hi</span>
        """
        insert(text)
        body = driver.find_element(By.TAG_NAME, "body")
        element = SeleniumElement(body)

        result = element.find_all(recursive=False)

        assert all(isinstance(element, SeleniumElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<div><p class="widget">Hello</p><p><a>World</a></p></div>""",
            """<span>Hi</span>""",
        ]

    def test_node17(self):
        text = """
            <div>
                <p class="widget">Hello</p>
                <p><a>World</a></p>
            </div>
            <span>Hi</span>
        """
        insert(text)
        body = driver.find_element(By.TAG_NAME, "body")
        element = SeleniumElement(body)

        result = element.find_all(name="p")

        assert all(isinstance(element, SeleniumElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<p class="widget">Hello</p>""",
            """<p><a>World</a></p>""",
        ]

    def test_node18(self):
        text = """
            <div>
                <p class="widget">Hello</p>
                <p><a>World</a></p>
            </div>
            <span class="widget">Hi</span>
        """
        insert(text)
        body = driver.find_element(By.TAG_NAME, "body")
        element = SeleniumElement(body)

        result = element.find_all(attrs={"class": "widget"})

        assert all(isinstance(element, SeleniumElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<p class="widget">Hello</p>""",
            """<span class="widget">Hi</span>""",
        ]

    def test_attr(self):
        text = """
            <div name="menu">
                <p class="widget">Hello</p>
                <p><a>World</a></p>
            </div>
            <span class="widget">Hi</span>
        """
        insert(text)
        div = driver.find_element(By.TAG_NAME, "div")
        element = SeleniumElement(div)

        result = element.get_attribute("name")
        assert result == "menu"

    def test_attr2(self):
        text = """
            <div class="menu widget">
                <p class="widget">Hello</p>
                <p><a>World</a></p>
            </div>
            <span class="widget">Hi</span>
        """
        insert(text)
        div = driver.find_element(By.TAG_NAME, "div")
        element = SeleniumElement(div)

        result = element.get_attribute("class")
        assert result == "menu widget"
