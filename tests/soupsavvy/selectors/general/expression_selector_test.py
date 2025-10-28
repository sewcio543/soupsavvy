"""Testing module for ExpressionSelector class."""

import pytest

from soupsavvy.exceptions import TagNotFoundException
from soupsavvy.selectors.general import ExpressionSelector
from tests.soupsavvy.conftest import MockLinkSelector, ToElement, strip


def mock_predicate(x) -> bool:
    """Simple predicate for testing purposes, that returns True if tag name is 'a'."""
    return x.name == "a"


def mock_raise_error(x) -> bool:
    """Simple predicate for testing purposes, that only raises ValueError."""
    raise ValueError("Error")


@pytest.mark.selector
class TestExpressionSelector:
    """Class for ExpressionSelector unit test suite."""

    def test_find_returns_first_element_matching_selector(self, to_element: ToElement):
        """Tests if find method returns first element matching selector."""
        text = """
            <div href="github"></div>
            <h1 class="widget">1</h1>
            <h1><p>2</p></h1>
            <span>
                <h1>3</h1>
            </span>
        """
        bs = to_element(text)
        selector = ExpressionSelector(lambda x: x.name == "h1")
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<h1 class="widget">1</h1>""")

    def test_find_returns_none_if_no_match_and_strict_false(
        self, to_element: ToElement
    ):
        """
        Tests if find returns None if no element matches the selector
        and strict is False.
        """
        text = """
            <div href="github"></div>
            <span class="widget"></span>
            <div><p>Hello</p></div>
            <span>
                <div>Hello</div>
            </span>
        """
        bs = to_element(text)
        selector = ExpressionSelector(mock_predicate)
        result = selector.find(bs)
        assert result is None

    def test_find_raises_exception_if_no_match_and_strict_true(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find raises TagNotFoundException if no element matches the selector
        and strict is True.
        """
        text = """
            <div href="github"></div>
            <span class="widget"></span>
            <div><p>Hello</p></div>
            <span>
                <div>Hello</div>
            </span>
        """
        bs = to_element(text)
        selector = ExpressionSelector(mock_predicate)

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_all_returns_empty_list_when_no_match(self, to_element: ToElement):
        """Tests if find returns an empty list if no element matches the selector."""
        text = """
            <div href="github"></div>
            <span class="widget"></span>
            <div><p>Hello</p></div>
            <span>
                <div>Hello</div>
            </span>
        """
        bs = to_element(text)
        selector = ExpressionSelector(mock_predicate)
        result = selector.find_all(bs)
        assert result == []

    def test_find_all_returns_all_matching_elements(self, to_element: ToElement):
        """Tests if find_all returns a list of all matching elements."""
        text = """
            <div href="github"></div>
            <a class="widget">1</a>
            <a><p>2</p></a>
            <span>
                <a>3</a>
            </span>
        """
        bs = to_element(text)
        selector = ExpressionSelector(mock_predicate)
        result = selector.find_all(bs)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="widget">1</a>"""),
            strip("""<a><p>2</p></a>"""),
            strip("""<a>3</a>"""),
        ]

    def test_find_returns_first_matching_child_if_recursive_false(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <div class="google">
                <a href="github">Not child</a>
            </div>
            <a href="github">1</a>
            <div><a>Not child</a></div>
            <a><p>2</p></a>
            <span>Hello</span>
            <a>3</a>
        """
        bs = to_element(text)
        selector = ExpressionSelector(mock_predicate)
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<a href="github">1</a>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div class="google">
                <a href="github">Not child</a>
            </div>
            <div><a>Not child</a></div>
            <span>Hello</span>
        """
        bs = to_element(text)
        selector = ExpressionSelector(mock_predicate)
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <div class="google">
                <a href="github">Not child</a>
            </div>
            <div><a>Not child</a></div>
            <span>Hello</span>
        """
        bs = to_element(text)
        selector = ExpressionSelector(mock_predicate)

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_all_returns_all_matching_children_when_recursive_false(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <div class="google">
                <a href="github">Not child</a>
            </div>
            <a href="github">1</a>
            <div><a>Not child</a></div>
            <a><p>2</p></a>
            <span>Hello</span>
            <a>3</a>
        """
        bs = to_element(text)
        selector = ExpressionSelector(mock_predicate)
        result = selector.find_all(bs, recursive=False)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a href="github">1</a>"""),
            strip("""<a><p>2</p></a>"""),
            strip("""<a>3</a>"""),
        ]

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find_all returns an empty list if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div class="google">
                <a href="github">Not child</a>
            </div>
            <div><a>Not child</a></div>
            <span>Hello</span>
        """
        bs = to_element(text)
        selector = ExpressionSelector(mock_predicate)
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_only_x_elements_when_limit_is_set(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <div href="github"></div>
            <a class="widget">1</a>
            <a><p>2</p></a>
            <span>
                <a>3</a>
            </span>
        """
        bs = to_element(text)
        selector = ExpressionSelector(mock_predicate)
        result = selector.find_all(bs, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="widget">1</a>"""),
            strip("""<a><p>2</p></a>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set_and_recursive_false(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find_all returns only x elements when limit is set and recursive
        is False. In this case only 2 first in order children matching
        the selector are returned.
        """
        text = """
            <div class="google">
                <a href="github">Not child</a>
            </div>
            <a href="github">1</a>
            <div><a>Not child</a></div>
            <a><p>2</p></a>
            <span>Hello</span>
            <a>3</a>
        """
        bs = to_element(text)
        selector = ExpressionSelector(mock_predicate)
        result = selector.find_all(bs, recursive=False, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a href="github">1</a>"""),
            strip("""<a><p>2</p></a>"""),
        ]

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            (ExpressionSelector(mock_predicate), ExpressionSelector(mock_predicate))
        ],
    )
    def test_two_tag_selectors_are_equal(self, selectors: tuple):
        """Tests if selector is equal to ExpressionSelector."""
        assert (selectors[0] == selectors[1]) is True

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            (
                ExpressionSelector(mock_predicate),
                ExpressionSelector(lambda x: x.name == "a"),
            ),
            (ExpressionSelector(mock_predicate), MockLinkSelector()),
        ],
    )
    def test_two_tag_selectors_are_not_equal(self, selectors: tuple):
        """Tests if selector is not equal to ExpressionSelector."""
        assert (selectors[0] == selectors[1]) is False

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            (
                ExpressionSelector(mock_predicate),
                MockLinkSelector(),
            ),
        ],
    )
    def test_equality_check_returns_not_implemented(self, selectors: tuple):
        """Tests if equality check returns NotImplemented for non comparable types."""
        result = selectors[0].__eq__(selectors[1])
        assert result is NotImplemented

    def test_propagates_exception_raised_inside_predicate(self, to_element: ToElement):
        """Tests if exception raised inside predicate is propagated to the caller."""
        text = """
            <div href="github"></div>
            <h1 class="widget">1</h1>
            <h1><p>2</p></h1>
            <span>
                <h1>3</h1>
            </span>
        """
        bs = to_element(text)
        selector = ExpressionSelector(mock_raise_error)

        with pytest.raises(ValueError):
            selector.find(bs)

    @pytest.mark.parametrize(
        argnames="f",
        argvalues=[lambda x, y: True, lambda: True],
        ids=["more_than_two_args", "no_args"],
    )
    def test_raises_type_error_if_function_does_not_take_one_argument(
        self, to_element: ToElement, f
    ):
        """
        Tests if TypeError is raised if provided function
        does not take exactly one argument.
        """
        text = """
            <div href="github"></div>
            <h1 class="widget">1</h1>
            <h1><p>2</p></h1>
            <span>
                <h1>3</h1>
            </span>
        """
        bs = to_element(text)
        selector = ExpressionSelector(f)

        with pytest.raises(TypeError):
            selector.find(bs)
