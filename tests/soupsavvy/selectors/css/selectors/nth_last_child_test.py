"""Module with unit tests for NthLastChild css tag selector."""

import pytest

from soupsavvy.exceptions import InvalidCSSSelector, TagNotFoundException
from soupsavvy.selectors.css.selectors import NthLastChild
from tests.soupsavvy.conftest import find_body_element, strip, to_element


@pytest.mark.css
@pytest.mark.selector
class TestNthLastChild:
    """Class with unit tests for NthLastChild tag selector."""

    def test_css_selector_is_correct(self):
        """Tests if selector property returns correct value."""
        assert NthLastChild("2n").css == ":nth-last-child(2n)"

    def test_find_all_returns_all_tags_for_selector_without_tag_name(self):
        """Tests if find_all method returns all tags for selector without tag name."""
        text = """
            <a class="widget">1</a>
            <div>
                <p>2</p>
                <p class="widget">Hello</p>
                <a><p>3</p></a>
                <span><a>4</a><p></p></span>
            </div>
            <div>5</div>
            <div><a>Hello</a></div>
        """
        bs = find_body_element(to_element(text))
        selector = NthLastChild("2n")
        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="widget">1</a>"""),
            strip("""<p>2</p>"""),
            strip("""<a><p>3</p></a>"""),
            strip("""<a>4</a>"""),
            strip("""<div>5</div>"""),
        ]

    def test_find_returns_first_tag_matching_selector(self):
        """Tests if find method returns first tag matching selector."""
        text = """
            <div></div>
            <div>1</div>
            <div>
                <a></a>
                <p><a>23</a><span></span></p>
                <span></span>
            </div>
            <span>4</span>
            <a class="widget"></a>
            <div><a>56</a><p></p></div>
            <span></span>
        """
        bs = to_element(text)
        selector = NthLastChild("2n")
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<div>1</div>""")

    def test_find_returns_none_if_no_match_and_strict_false(self):
        """
        Tests if find returns None if no element matches the selector
        and strict is False.
        """
        text = """
            <div></div>
            <div><p></p><a></a></div>
        """
        bs = to_element(text)
        selector = NthLastChild("3n")
        result = selector.find(bs)
        assert result is None

    def test_find_raises_exception_if_no_match_and_strict_true(self):
        """
        Tests if find raises TagNotFoundException if no element matches the selector
        and strict is True.
        """
        text = """
            <div></div>
            <div><p></p><a></a></div>
        """
        bs = to_element(text)
        selector = NthLastChild("3n")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_all_returns_empty_list_when_no_match(self):
        """Tests if find returns an empty list if no element matches the selector."""
        text = """
            <div></div>
            <div><p></p><a></a></div>
        """
        bs = to_element(text)
        selector = NthLastChild("3n")
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <div>
                <a></a>
                <p><a>Not child</a><span></span></p>
                <span></span>
            </div>
            <div>1</div>
            <a class="widget"></a>
            <div><a>23</a><p></p></div>
            <span></span>
        """
        bs = find_body_element(to_element(text))
        selector = NthLastChild("2n")
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<div>1</div>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div><p>Not child</p><a></a><p></p></div>
            <div></div>
        """
        bs = find_body_element(to_element(text))
        selector = NthLastChild("3n")
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <div><p>Not child</p><a></a><p></p></div>
            <div></div>
        """
        bs = find_body_element(to_element(text))
        selector = NthLastChild("3n")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self,
    ):
        """
        Tests if find_all returns an empty list if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div><p>Not child</p><a></a><p></p></div>
            <div></div>
        """
        bs = find_body_element(to_element(text))
        selector = NthLastChild("3n")
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <span>1</span>
            <div>
                <a></a>
                <p><a>Not child</a><span></span></p>
                <span></span>
            </div>
            <div>2</div>
            <a class="widget"></a>
            <div><a>3</a><p></p></div>
            <span></span>
        """
        bs = find_body_element(to_element(text))
        selector = NthLastChild("2n")
        result = selector.find_all(bs, recursive=False)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<span>1</span>"""),
            strip("""<div>2</div>"""),
            strip("""<div><a>3</a><p></p></div>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <a class="widget">1</a>
            <div>
                <p>2</p>
                <p class="widget">Hello</p>
                <a><p>3</p></a>
                <span><a>4</a><p></p></span>
            </div>
            <div>5</div>
            <div><a>Hello</a></div>
        """
        bs = to_element(text)
        selector = NthLastChild("2n")
        result = selector.find_all(bs, limit=2)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="widget">1</a>"""),
            strip("""<p>2</p>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set_and_recursive_false(
        self,
    ):
        """
        Tests if find_all returns only x elements when limit is set and recursive
        is False. In this case only 2 first in order children matching
        the selector are returned.
        """
        text = """
            <span>1</span>
            <div>
                <a></a>
                <p><a>Not child</a><span></span></p>
                <span></span>
            </div>
            <div>2</div>
            <a class="widget"></a>
            <div><a>3</a><p></p></div>
            <span></span>
        """
        bs = find_body_element(to_element(text))
        selector = NthLastChild("2n")
        result = selector.find_all(bs, recursive=False, limit=2)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<span>1</span>"""),
            strip("""<div>2</div>"""),
        ]

    def test_raises_exception_when_invalid_css_selector(self):
        """
        Tests if InvalidCSSSelector exception is raised in find methods,
        when invalid css selector is passed.
        """
        selector = NthLastChild("2x+1")
        bs = to_element("<div></div>")

        with pytest.raises(InvalidCSSSelector):
            selector.find(bs)

        with pytest.raises(InvalidCSSSelector):
            selector.find_all(bs)

    @pytest.mark.parametrize(
        argnames="nth, expected",
        argvalues=[
            ("2n", [1, 3, 5]),
            ("2n+1", [2, 4, 6]),
            # ignores whitespaces
            ("   2n +  1", [2, 4, 6]),
            ("-n+3", [4, 5, 6]),
            ("even", [1, 3, 5]),
            ("odd", [2, 4, 6]),
            ("3", [4]),
            ("-3n", []),
            ("-3n+10", [3, 6]),
        ],
    )
    def test_returns_elements_based_on_nth_selector(
        self, nth: str, expected: list[int]
    ):
        """Tests if find_all returns all elements matching various nth selectors."""
        text = """
            <div class="widget">1</div>
            <a class="widget">2</a>
            <div class="widget">3</div>
            <a class="widget">4</a>
            <div class="widget">5</div>
            <a class="widget">6</a>
        """
        bs = find_body_element(to_element(text))
        selector = NthLastChild(nth)
        results = selector.find_all(bs)

        assert list(map(lambda x: strip(str(x)), results)) == [
            (
                f"""<a class="widget">{i}</a>"""
                if (i % 2) == 0
                else f"""<div class="widget">{i}</div>"""
            )
            for i in expected
        ]
