"""Module with unit tests for XPath selector."""

import pytest

from soupsavvy.exceptions import TagNotFoundException
from soupsavvy.selectors.xpath.selectors import XPathSelector
from tests.soupsavvy.conftest import MockLinkSelector, ToElement, strip


@pytest.mark.selector
@pytest.mark.skip_bs4
class TestXPathSelector:
    """
    Class with unit tests for XPathSelector selector.
    Idea for the tests is to check cases for simple selector, selection itself
    is delegates to appropriate api handled by implementation.
    """

    def test_find_returns_first_element_matching_selector(self, to_element: ToElement):
        """Tests if find method returns first element matching selector."""
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
        selector = XPathSelector("//div/a")
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<a>1</a>""")

    def test_find_returns_none_if_no_match_and_strict_false(
        self, to_element: ToElement
    ):
        """
        Tests if find returns None if no element matches the selector
        and strict is False.
        """
        text = """
            <div></div>
            <div class="widget123">
                <span><a>Not child</a></span>
            </div>
            <a class="widget"></a>
            <span><a class="widget"></a></span>
            <div class="widget"><p>Hello</p></div>
        """
        bs = to_element(text)
        selector = XPathSelector("//div/a")
        result = selector.find(bs)
        assert result is None

    def test_find_raises_exception_if_no_match_and_strict_true(
        self, to_element: ToElement
    ):
        """
        Tests if find raises TagNotFoundException if no element matches the selector
        and strict is True.
        """
        text = """
            <div></div>
            <div class="widget123">
                <span><a>Not child</a></span>
            </div>
            <a class="widget"></a>
            <span><a class="widget"></a></span>
            <div class="widget"><p>Hello</p></div>
        """
        bs = to_element(text)
        selector = XPathSelector("//div/a")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_all_returns_all_matching_elements(self, to_element: ToElement):
        """Tests if find_all returns a list of all matching elements."""
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
        selector = XPathSelector("//div/a")

        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a>1</a>"""),
            strip("""<a><h1>2</h1></a>"""),
            strip("""<a>3</a>"""),
        ]

    def test_find_all_returns_empty_list_when_no_match(self, to_element: ToElement):
        """Tests if find returns an XPathSelector list if no element matches the selector."""
        text = """
            <div></div>
            <div class="widget123">
                <span><a>Not child</a></span>
            </div>
            <a class="widget"></a>
            <span><a class="widget"></a></span>
            <div class="widget"><p>Hello</p></div>
        """
        bs = to_element(text)
        selector = XPathSelector("//div/a")
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(
        self, to_element: ToElement
    ):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <div class="widget123">
                <p>Not child</p>
            </div>
            <p>1</p>
            <a class="widget"></a>
            <p><span>2</span></p>
            <div><a>Hello</a></div>
            <p>3</p>
        """
        bs = to_element(text)
        selector = XPathSelector("//p")
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<p>1</p>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(
        self, to_element: ToElement
    ):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div class="widget123">
                <p>Not child</p>
            </div>
            <a class="widget"></a>
            <span><p>2</p></span>
            <div><p>Not child</p></div>
        """
        bs = to_element(text)
        selector = XPathSelector("//p")
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(
        self, to_element: ToElement
    ):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <div class="widget123">
                <p>Not child</p>
            </div>
            <a class="widget"></a>
            <span><p>2</p></span>
            <div><p>Not child</p></div>
        """
        bs = to_element(text)
        selector = XPathSelector("//p")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self, to_element: ToElement
    ):
        """
        Tests if find_all returns an XPathSelector list if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div class="widget123">
                <p>Not child</p>
            </div>
            <a class="widget"></a>
            <span><p>2</p></span>
            <div><p>Not child</p></div>
        """
        bs = to_element(text)
        selector = XPathSelector("//p")
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_all_matching_children_when_recursive_false(
        self, to_element: ToElement
    ):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <div class="widget123">
                <p>Not child</p>
            </div>
            <p>1</p>
            <a class="widget"></a>
            <p><span>2</span></p>
            <div><a>Hello</a></div>
            <p>3</p>
        """
        bs = to_element(text)
        selector = XPathSelector("//p")
        result = selector.find_all(bs, recursive=False)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<p>1</p>"""),
            strip("""<p><span>2</span></p>"""),
            strip("""<p>3</p>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set(
        self, to_element: ToElement
    ):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
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
        selector = XPathSelector("//div/a")
        result = selector.find_all(bs, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a>1</a>"""),
            strip("""<a><h1>2</h1></a>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set_and_recursive_false(
        self, to_element: ToElement
    ):
        """
        Tests if find_all returns only x elements when limit is set and recursive
        is False. In this case only 2 first in order children matching
        the selector are returned.
        """
        text = """
            <div class="widget123">
                <p>Not child</p>
            </div>
            <p>1</p>
            <a class="widget"></a>
            <p><span>2</span></p>
            <div><a>Hello</a></div>
            <p>3</p>
        """
        bs = to_element(text)
        selector = XPathSelector("//p")
        result = selector.find_all(bs, recursive=False, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<p>1</p>"""),
            strip("""<p><span>2</span></p>"""),
        ]

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[(XPathSelector("//a"), XPathSelector("//a"))],
    )
    def test_two_tag_selectors_are_equal(self, selectors: tuple):
        """Tests if selector is equal to TypeSelector."""
        assert (selectors[0] == selectors[1]) is True

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            (XPathSelector("//a"), XPathSelector("//div")),
            (XPathSelector("//a"), MockLinkSelector()),
        ],
    )
    def test_two_tag_selectors_are_not_equal(self, selectors: tuple):
        """Tests if selector is not equal to TypeSelector."""
        assert (selectors[0].__eq__(selectors[1])) is False
