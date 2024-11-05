import pytest
from bs4 import BeautifulSoup
from lxml.etree import _Element as HtmlElement
from lxml.etree import fromstring

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
    def test_node(self):
        text = """
            <div>Hello</div>
        """
        tree = to_lxml(text)
        assert tree is not None

        element = LXMLElement(tree)

        assert element.node is tree
        assert element.get() is tree

    def test_node1(self):
        text = """
            <div>Hello</div>
        """
        tree = to_lxml(text)
        element = LXMLElement.from_node(tree)

        assert element.node is tree
        assert element.get() is tree

    def test_node2(self):
        text = """
            <div>Hello</div>
        """
        tree = to_lxml(text)
        element = LXMLElement(tree)

        assert repr(element) == f"LXMLElement({tree!r})"

    def test_node3(self):
        text = """
            <div>Hello</div>
        """
        tree = to_lxml(text)
        element = LXMLElement(tree)

        assert hash(element) == hash(tree)

    def test_eq(self):
        text = """
            <div><p>Hello</p></div>
        """
        tree = to_lxml(text)
        element = LXMLElement(tree)

        assert element == LXMLElement(tree)
        assert element != LXMLElement(tree.find(".//p"))  # type: ignore
        assert element != tree

    def test_node4(self):
        text = """
            <div>Hello</div>
        """
        tree = to_lxml(text).find(".//div")
        assert tree is not None

        element = LXMLElement(tree)

        assert element.name == "div"
        assert element.text == "Hello"

    def test_node5(self):
        text = """
            Before<div> Hello<p>\nWorld </p>.</div>After
        """
        tree = to_lxml(text).find(".//div")
        assert tree is not None

        element = LXMLElement(tree)
        assert element.text == " Hello\nWorld ."

    def test_node6(self):
        text = """
            <div>
                <p>Hello</p>
                <p>World</p>
                <span><p>Hi</p><a>Earth</a></span>
            </div>
        """
        tree = to_lxml(text).find(".//div")
        assert tree is not None

        element = LXMLElement(tree)
        children = list(element.children)

        assert all(isinstance(child, LXMLElement) for child in children)
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
        tree = to_lxml(text).find(".//div")
        assert tree is not None

        element = LXMLElement(tree)
        descendants = list(element.descendants)

        assert all(isinstance(child, LXMLElement) for child in descendants)
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
        tree = to_lxml(text).find(".//p")
        assert tree is not None

        element = LXMLElement(tree)
        parent = element.parent

        assert isinstance(parent, LXMLElement)
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
        tree = to_lxml(text)
        element = LXMLElement(tree)
        api = element.css("p.widget")

        assert isinstance(api, CSSSelectApi)

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
        tree = to_lxml(text)
        element = LXMLElement(tree)
        api = element.xpath(".//p")

        assert isinstance(api, LXMLXpathApi)

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
        tree = to_lxml(text).find(".//a")
        assert tree is not None

        element = LXMLElement(tree)
        ancestors = element.find_ancestors()

        assert all(isinstance(element, LXMLElement) for element in ancestors)
        assert [strip(str(x)) for x in ancestors] == [
            "<p><a>Hello</a></p>",
            "<span><p><a>Hello</a></p></span>",
            """<div><p class="widget">Hello</p><span><p><a>Hello</a></p></span></div>""",
            """<body><div><p class="widget">Hello</p><span><p><a>Hello</a></p></span></div></body>""",
            """<html><body><div><p class="widget">Hello</p><span><p><a>Hello</a></p></span></div></body></html>""",
        ]

    def test_node_limit(self):
        text = """
            <div>
                <p class="widget">Hello</p>
                <span><p><a>Hello</a></p></span>
            </div>
        """
        tree = to_lxml(text).find(".//a")
        assert tree is not None

        element = LXMLElement(tree)
        ancestors = element.find_ancestors(limit=2)

        assert all(isinstance(element, LXMLElement) for element in ancestors)
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
        tree = to_lxml(text)

        element = LXMLElement(tree)
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
        tree = to_lxml(text).find(".//span")
        assert isinstance(tree, HtmlElement)

        element = LXMLElement(tree)
        siblings = element.find_subsequent_siblings()

        assert all(isinstance(element, LXMLElement) for element in siblings)
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
        tree = to_lxml(text).find(".//span")
        assert isinstance(tree, HtmlElement)

        element = LXMLElement(tree)
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
        tree = to_lxml(text).find(".//span")
        assert isinstance(tree, HtmlElement)

        element = LXMLElement(tree)
        siblings = element.find_subsequent_siblings(limit=2)

        assert all(isinstance(element, LXMLElement) for element in siblings)
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
        tree = to_lxml(text).find(".//body")
        assert tree is not None

        element = LXMLElement(tree)
        result = element.find_all()

        assert all(isinstance(element, LXMLElement) for element in result)
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
        tree = to_lxml(text).find(".//body")
        assert tree is not None

        element = LXMLElement(tree)
        result = element.find_all(limit=3)

        assert all(isinstance(element, LXMLElement) for element in result)
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
        tree = to_lxml(text).find(".//body")
        assert tree is not None

        element = LXMLElement(tree)
        result = element.find_all(recursive=False)

        assert all(isinstance(element, LXMLElement) for element in result)
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
        tree = to_lxml(text)
        element = LXMLElement(tree)
        result = element.find_all(name="p")

        assert all(isinstance(element, LXMLElement) for element in result)
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
        tree = to_lxml(text)
        element = LXMLElement(tree)
        result = element.find_all(attrs={"class": "widget"})

        assert all(isinstance(element, LXMLElement) for element in result)
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
        tree = to_lxml(text).find(".//div")
        assert tree is not None

        element = LXMLElement(tree)
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
        tree = to_lxml(text).find(".//div")
        assert tree is not None

        element = LXMLElement(tree)
        result = element.get_attribute("class")
        assert result == "menu widget"
