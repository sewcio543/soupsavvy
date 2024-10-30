import pytest
from bs4 import BeautifulSoup, Tag

from soupsavvy.implementation.bs4 import SoupElement
from soupsavvy.selectors.css.api import SoupsieveApi
from tests.soupsavvy.conftest import strip


class TestSoupElement:
    def test_node(self):
        text = """
            <div>Hello</div>
        """
        bs = BeautifulSoup(text, "lxml")
        element = SoupElement(bs)

        assert element.node is bs
        assert element.get() is bs

    def test_node1(self):
        text = """
            <div>Hello</div>
        """
        bs = BeautifulSoup(text, "lxml")
        element = SoupElement.from_node(bs)

        assert element.node is bs
        assert element.get() is bs

    def test_node2(self):
        text = """
            <div>Hello</div>
        """
        bs = BeautifulSoup(text, "lxml")
        element = SoupElement(bs)

        assert str(element) == str(bs)
        assert repr(element) == f"SoupElement({bs!r})"

    def test_node3(self):
        text = """
            <div>Hello</div>
        """
        bs = BeautifulSoup(text, "lxml")
        element = SoupElement(bs)

        assert hash(element) == hash(id(bs))

    def test_eq(self):
        text = """
            <div><p>Hello</p></div>
        """
        bs = BeautifulSoup(text, "lxml")
        element = SoupElement(bs)

        assert element == SoupElement(bs)
        assert element != SoupElement(bs.p)  # type: ignore
        assert element != bs

    def test_node4(self):
        text = """
            <div>Hello</div>
        """
        bs = BeautifulSoup(text, "lxml").div
        assert bs is not None

        element = SoupElement(bs)

        assert element.name == bs.name == "div"
        assert element.text == bs.text == "Hello"
        assert element.prettify() == bs.prettify()

    def test_node5(self):
        text = """
            Before<div> Hello<p>\nWorld </p>.</div>After
        """
        bs = BeautifulSoup(text, "lxml").div
        assert bs is not None

        element = SoupElement(bs)

        assert element.text == bs.text == " Hello\nWorld ."
        assert element.prettify() == bs.prettify()

    def test_node6(self):
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
        assert [strip(str(child.get())) for child in children] == [
            "<p>Hello</p>",
            "<p>World</p>",
            "<span><p>Hi</p><a>Earth</a></span>",
        ]

    def test_node7(self):
        text = """
            <div>
                <p>Hello</p>
                <p>World</p>
                <span><p><h1>Hi</h1><h2>Hi</h2></p><a>Earth</a></span>
            </div>
        """
        bs = BeautifulSoup(text, "html.parser").div
        assert bs is not None

        element = SoupElement(bs)
        descendants = list(element.descendants)

        assert all(isinstance(child, SoupElement) for child in descendants)
        assert [strip(str(child.get())) for child in descendants] == [
            "<p>Hello</p>",
            "<p>World</p>",
            "<span><p><h1>Hi</h1><h2>Hi</h2></p><a>Earth</a></span>",
            "<p><h1>Hi</h1><h2>Hi</h2></p>",
            "<h1>Hi</h1>",
            "<h2>Hi</h2>",
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
        bs = BeautifulSoup(text, "html.parser").p
        assert bs is not None

        element = SoupElement(bs)
        parent = element.parent

        assert isinstance(parent, SoupElement)
        assert parent.get() is bs.parent
        assert (
            strip(str(parent.get()))
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
        bs = BeautifulSoup(text, "html.parser")
        element = SoupElement(bs)
        api = element.css("p.widget")

        assert isinstance(api, SoupsieveApi)

        result = api.select(element)
        assert [strip(str(x)) for x in result] == [
            '<p class="widget">Hello</p>',
            '<p class="widget">Hi</p>',
        ]

    def test_node10(self):
        text = """
            <div>
                <p class="widget">Hello</p>
                <span><p><h1>Hello</h1></p></span>
            </div>
        """
        bs = BeautifulSoup(text, "html.parser").h1
        assert bs is not None

        element = SoupElement(bs)
        ancestors = element.find_ancestors()

        assert all(isinstance(element, SoupElement) for element in ancestors)
        assert [strip(str(x)) for x in ancestors] == [
            "<p><h1>Hello</h1></p>",
            "<span><p><h1>Hello</h1></p></span>",
            """<div><p class="widget">Hello</p><span><p><h1>Hello</h1></p></span></div>""",
            # root - document
            """<div><p class="widget">Hello</p><span><p><h1>Hello</h1></p></span></div>""",
        ]

    def test_node_limit(self):
        text = """
            <div>
                <p class="widget">Hello</p>
                <span><p><h1>Hello</h1></p></span>
            </div>
        """
        bs = BeautifulSoup(text, "html.parser").h1
        assert bs is not None

        element = SoupElement(bs)
        ancestors = element.find_ancestors(limit=2)

        assert all(isinstance(element, SoupElement) for element in ancestors)
        assert [strip(str(x)) for x in ancestors] == [
            "<p><h1>Hello</h1></p>",
            "<span><p><h1>Hello</h1></p></span>",
        ]

    def test_node11(self):
        text = """
            <div>
                <p class="widget">Hello</p>
                <span><p><h1>Hello</h1></p></span>
            </div>
        """
        bs = BeautifulSoup(text, "html.parser")
        assert bs is not None

        element = SoupElement(bs)
        assert element.find_ancestors() == []

    def test_node12(self):
        text = """
            <div>
                <p class="widget">Hello</p>
                <span class="anchor">Hello</span>
                <p><h1>World</h1></p>
                <span>Earth</span>
                <h1>Nice</h1>
            </div>
            <span>Hi</span>
        """
        bs = BeautifulSoup(text, "html.parser").find(class_="anchor")
        assert isinstance(bs, Tag)

        element = SoupElement(bs)
        siblings = element.find_next_siblings()

        assert all(isinstance(element, SoupElement) for element in siblings)
        assert [strip(str(x)) for x in siblings] == [
            "<p><h1>World</h1></p>",
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
        bs = BeautifulSoup(text, "html.parser").find(class_="anchor")
        assert isinstance(bs, Tag)

        element = SoupElement(bs)
        assert element.find_next_siblings() == []

    def test_node14(self):
        text = """
            <div>
                <p class="widget">Hello</p>
                <span class="anchor">Hello</span>
                <p><h1>World</h1></p>
                <span>Earth</span>
                <h1>Nice</h1>
            </div>
            <span>Hi</span>
        """
        bs = BeautifulSoup(text, "html.parser").find(class_="anchor")
        assert isinstance(bs, Tag)

        element = SoupElement(bs)
        siblings = element.find_next_siblings(limit=2)

        assert all(isinstance(element, SoupElement) for element in siblings)
        assert [strip(str(x)) for x in siblings] == [
            "<p><h1>World</h1></p>",
            "<span>Earth</span>",
        ]

    def test_node15(self):
        text = """
            <div>
                <p class="widget">Hello</p>
                <p><h1>World</h1></p>
            </div>
            <span>Hi</span>
        """
        bs = BeautifulSoup(text, "html.parser")
        element = SoupElement(bs)
        result = element.find_all()

        assert all(isinstance(element, SoupElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<div><p class="widget">Hello</p><p><h1>World</h1></p></div>""",
            """<p class="widget">Hello</p>""",
            """<p><h1>World</h1></p>""",
            """<h1>World</h1>""",
            """<span>Hi</span>""",
        ]

    def test_node15_limit(self):
        text = """
            <div>
                <p class="widget">Hello</p>
                <p><h1>World</h1></p>
            </div>
            <span>Hi</span>
        """
        bs = BeautifulSoup(text, "html.parser")
        element = SoupElement(bs)
        result = element.find_all(limit=3)

        assert all(isinstance(element, SoupElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<div><p class="widget">Hello</p><p><h1>World</h1></p></div>""",
            """<p class="widget">Hello</p>""",
            """<p><h1>World</h1></p>""",
        ]

    def test_node16(self):
        text = """
            <div>
                <p class="widget">Hello</p>
                <p><h1>World</h1></p>
            </div>
            <span>Hi</span>
        """
        bs = BeautifulSoup(text, "html.parser")
        element = SoupElement(bs)
        result = element.find_all(recursive=False)

        assert all(isinstance(element, SoupElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<div><p class="widget">Hello</p><p><h1>World</h1></p></div>""",
            """<span>Hi</span>""",
        ]

    def test_node17(self):
        text = """
            <div>
                <p class="widget">Hello</p>
                <p><h1>World</h1></p>
            </div>
            <span>Hi</span>
        """
        bs = BeautifulSoup(text, "html.parser")
        element = SoupElement(bs)
        result = element.find_all(name="p")

        assert all(isinstance(element, SoupElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<p class="widget">Hello</p>""",
            """<p><h1>World</h1></p>""",
        ]

    def test_node18(self):
        text = """
            <div>
                <p class="widget">Hello</p>
                <p><h1>World</h1></p>
            </div>
            <span class="widget">Hi</span>
        """
        bs = BeautifulSoup(text, "html.parser")
        element = SoupElement(bs)
        result = element.find_all(attrs={"class": "widget"})

        assert all(isinstance(element, SoupElement) for element in result)
        assert [strip(str(x)) for x in result] == [
            """<p class="widget">Hello</p>""",
            """<span class="widget">Hi</span>""",
        ]

    def test_attr(self):
        text = """
            <div name="menu">
                <p class="widget">Hello</p>
                <p><h1>World</h1></p>
            </div>
            <span class="widget">Hi</span>
        """
        bs = BeautifulSoup(text, "html.parser").div
        assert bs is not None

        element = SoupElement(bs)
        result = element.get_attribute("name")
        assert result == "menu"

    def test_attr2(self):
        text = """
            <div class="menu widget">
                <p class="widget">Hello</p>
                <p><h1>World</h1></p>
            </div>
            <span class="widget">Hi</span>
        """
        bs = BeautifulSoup(text, "html.parser").div
        assert bs is not None

        element = SoupElement(bs)
        result = element.get_attribute("class")
        assert result == "menu widget"
