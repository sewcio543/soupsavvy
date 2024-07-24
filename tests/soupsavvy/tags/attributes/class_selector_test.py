"""Testing module for ClassSelector class."""

import re

import pytest

from soupsavvy.exceptions import TagNotFoundException
from soupsavvy.tags.attributes import ClassSelector
from tests.soupsavvy.tags.conftest import find_body_element, strip, to_bs


@pytest.mark.soup
class TestClassSelector:
    """Class for ClassSelector unit test suite."""

    @pytest.mark.edge_case
    def test_find_matches_element_with_list_of_classes_if_one_matches(self):
        """
        Tests if find returns first tag with that has a list of classes
        and one of them matches the value.

        Example
        -------
        >>> <div class="menu widget"></div>

        In this case, the tag has two classes 'menu' and 'widget'.
        If selector looks for 'widget' or 'menu' class, it should match.
        """
        text = """
            <div href="menu"></div>
            <div class="widget_class menu"></div>
            <div class="it has a long list of widget classes"></div>
            <div class="another list of widget classes"></div>
        """
        bs = to_bs(text)
        selector = ClassSelector("widget")
        result = selector.find(bs)
        assert strip(str(result)) == strip(
            """<div class="it has a long list of widget classes"></div>"""
        )

    def test_find_returns_first_match_with_any_value(self):
        """
        Tests if find returns first tag with class attribute,
        when no value is specified.
        """
        text = """
            <div href="widget"></div>
            <span></span>
            <div class=""></div>
            <a class="menu"></a>
        """
        bs = to_bs(text)
        selector = ClassSelector()
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<div class=""></div>""")

    def test_find_returns_first_match_with_specific_value(self):
        """Tests if find returns first tag with class attribute with specific value."""
        text = """
            <div href="widget"></div>
            <span class=""></span>
            <div class="menu"></div>
            <a class="widget"></a>
            <div class="widget"></div>
        """
        bs = to_bs(text)
        selector = ClassSelector("widget")
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<a class="widget"></a>""")

    def test_find_returns_first_match_with_pattern(self):
        """
        Tests if find returns first tag with class attribute that matches
        specified regex pattern.
        """
        text = """
            <div class="menu widget 12"></div>
            <span class="widget"></span>
            <div href="widget 12"></div>
            <div class="widget 123"></div>
        """
        bs = to_bs(text)
        selector = ClassSelector(value=re.compile(r"^widget.?\d{1,3}$"))
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<div class="widget 123"></div>""")

    def test_find_returns_none_if_no_match_and_strict_false(self):
        """
        Tests if find returns None if no element matches the selector
        and strict is False.
        """
        text = """
            <div href="widget"></div>
            <span class=""></span>
            <div class="menu"></div>
            <div class="widget123"></div>
        """
        bs = to_bs(text)
        selector = ClassSelector("widget")
        result = selector.find(bs)
        assert result is None

    def test_find_raises_exception_if_no_match_and_strict_true(self):
        """
        Tests find raises TagNotFoundException if no element matches the selector
        and strict is True.
        """
        text = """
            <div href="widget"></div>
            <span class=""></span>
            <div class="menu"></div>
            <div class="widget123"></div>
        """
        bs = to_bs(text)
        selector = ClassSelector("widget")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_all_returns_all_matching_elements(self):
        """Tests if find_all returns a list of all matching elements."""
        text = """
            <div href="widget"></div>
            <div class="widget">1</div>
            <span class=""></span>
            <div class="menu"></div>
            <a class="widget">2</a>
            <div>
                <a class="widget">3</a>
                <a class="menu"></a>
            </div>
            <div class="widget"><span>4</span></div>
            <a id="widget"></a>
        """
        bs = to_bs(text)
        selector = ClassSelector("widget")

        result = selector.find_all(bs)
        excepted = [
            strip("""<div class="widget">1</div>"""),
            strip("""<a class="widget">2</a>"""),
            strip("""<a class="widget">3</a>"""),
            strip("""<div class="widget"><span>4</span></div>"""),
        ]
        assert list(map(lambda x: strip(str(x)), result)) == excepted

    def test_find_all_returns_empty_list_when_no_match(self):
        """Tests if find returns an empty list if no element matches the selector."""
        text = """
            <div href="widget"></div>
            <span class=""></span>
            <div class="menu"></div>
            <div class="widget123"></div>
        """
        bs = to_bs(text)
        selector = ClassSelector("widget")
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <div>
                <a class="widget">Hello</a>
            </div>
            <div href="widget"></div>
            <div class="menu"></div>
            <a class="widget"></a>
            <div class="widget"></div>
        """
        bs = find_body_element(to_bs(text))
        selector = ClassSelector("widget")
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<a class="widget"></a>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div>
                <a class="widget">Hello</a>
            </div>
            <div href="widget"></div>
            <div class="menu"></div>
            <a class="widget123">Hello</a>
        """
        bs = find_body_element(to_bs(text))
        selector = ClassSelector("widget")
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <div>
                <a class="widget">Hello</a>
            </div>
            <div href="widget"></div>
            <div class="menu"></div>
            <a class="widget123">Hello</a>
        """
        bs = find_body_element(to_bs(text))
        selector = ClassSelector("widget")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self,
    ):
        """
        Tests if find_all returns an empty list if no child element
        matches the selector and recursive is False.
        """
        text = """
            <div>
                <a class="widget">Hello</a>
            </div>
            <a class="widget123">Hello</a>
            <div href="widget"></div>
            <div class="menu"></div>
        """
        bs = find_body_element(to_bs(text))
        selector = ClassSelector("widget")
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <a class="widget" href="menu">1</a>
            <div>
                <a class="widget">Hello</a>
                <div class="widget"></div>
            </div>
            <div href="widget"></div>
            <div class="menu"></div>
            <div class="widget">2</div>
            <span class=""></span>
            <div class="widget"><span>3</span></div>
        """
        bs = find_body_element(to_bs(text))
        selector = ClassSelector("widget")
        result = selector.find_all(bs, recursive=False)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="widget" href="menu">1</a>"""),
            strip("""<div class="widget">2</div>"""),
            strip("""<div class="widget"><span>3</span></div>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <a class="widget" href="menu"></a>
            <div href="widget"></div>
            <div>
                <a class="widget">Hello</a>
            </div>
            <div class="menu"></div>
            <span class=""></span>
            <div class="widget"></div>
        """
        bs = find_body_element(to_bs(text))
        selector = ClassSelector("widget")
        result = selector.find_all(bs, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="widget" href="menu"></a>"""),
            strip("""<a class="widget">Hello</a>"""),
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
            <a class="widget" href="menu"></a>
            <div href="widget"></div>
            <div>
                <a class="widget">Hello</a>
            </div>
            <div class="menu"></div>
            <div class="widget"></div>
            <span class=""></span>
            <span class="widget"></span>
        """
        bs = find_body_element(to_bs(text))
        selector = ClassSelector("widget")
        result = selector.find_all(bs, recursive=False, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="widget" href="menu"></a>"""),
            strip("""<div class="widget"></div>"""),
        ]

    @pytest.mark.css_selector
    @pytest.mark.parametrize(
        argnames="selector, css",
        argvalues=[
            # class overrides default css selector with . syntax
            (ClassSelector("menu"), ".menu"),
            (ClassSelector(), "[class]"),
            # pattern is reduced to containment operator *=
            (
                ClassSelector(re.compile(r"^menu")),
                "[class*='^menu']",
            ),
        ],
    )
    def test_selector_is_correct(self, selector: ClassSelector, css: str):
        """Tests if css selector for AttributeSelector is constructed as expected."""
        assert selector.selector == css
