"""Module with unit tests for OnlyOfType css tag selector."""

import pytest

from soupsavvy.exceptions import TagNotFoundException
from soupsavvy.tags.css.tag_selectors import OnlyOfType
from tests.soupsavvy.tags.conftest import find_body_element, strip, to_bs


@pytest.mark.css_selector
@pytest.mark.soup
class TestOnlyOfType:
    """Class with unit tests for OnlyOfType tag selector."""

    def test_selector_is_correct_without_tag(self):
        """Tests if selector property returns correct value without specifying tag."""
        assert OnlyOfType().selector == ":only-of-type"

    def test_selector_is_correct_with_tag(self):
        """Tests if selector property returns correct value when specifying tag."""
        assert OnlyOfType("div").selector == "div:only-of-type"

    def test_find_returns_none_if_tag_name_not_present(self):
        """
        Tests if find method returns None if specified tag is not present
        in the tag markup. In this case, 'span' is not present in the markup.
        """
        html = """
            <div>
                <p>text</p>
            </div>
            <div></div>
        """
        bs = find_body_element(to_bs(html))
        tag = OnlyOfType("span")
        result = tag.find(bs)
        assert result is None

    def test_find_returns_none_if_no_only_of_type_without_specified_tag(self):
        """
        Tests if find method returns None if no only-of-type elements are
        present in the tag markup and tag is not specified.
        """
        html = """
            <div>
                <p>text 1</p>
                <p>text 2</p>
            </div>
            <div></div>
        """
        bs = find_body_element(to_bs(html))
        tag = OnlyOfType()
        result = tag.find(bs)
        assert result is None

    def test_find_returns_none_if_no_only_of_type_with_specified_tag(self):
        """
        Tests if find method returns None if specified tag is not present
        as the only-of-type element in the tag markup. In this case, 'p' and 'a'
        are only-of-type elements, but they do not match the specified tag 'div'.
        """
        html = """
            <div>
                <p>text 1</p>
                <a>text 2</a>
            </div>
            <div></div>
        """
        bs = find_body_element(to_bs(html))
        tag = OnlyOfType("div")
        result = tag.find(bs)
        assert result is None

    def test_find_returns_first_only_element_without_tag(self):
        """
        Tests if find method returns first only element of type relative to its parent.
        Div elements in root are not only-of-type as well as p elements
        in th first div. 'p' and 'a' elements in second div are only-of-type,
        first of them is returned.
        """
        html = """
            <div>
                <p>text 1</p>
                <p>text 2</p>
            </div>
            <div>
                <p>text 3</p>
                <a>text 4</a>
            </div>
        """
        bs = find_body_element(to_bs(html))
        tag = OnlyOfType()
        result = tag.find(bs)
        assert strip(str(result)) == strip("<p>text 3</p>")

    def test_find_returns_first_only_element_of_type_with_tag(self):
        """
        Tests if find method returns first only element of type
        relative to its parent, which name matches the specified tag.
        In this case 'div', 'span' and 'p' in second div are only-of-type,
        but they are skipped as they do not match the specified tag 'a'.
        """
        html = """
            <div>
                <p>text 1</p>
                <p>text 2</p>
            </div>
            <span>
                <p>text 3</p>
                <a>text 4</a>
            </span>
        """
        bs = find_body_element(to_bs(html))
        tag = OnlyOfType("a")
        result = tag.find(bs)
        assert strip(str(result)) == strip("<a>text 4</a>")

    def test_find_raises_exception_without_specified_tag_if_not_found_in_strict_mode(
        self,
    ):
        """
        Tests if find method raises TagNotFoundException
        if no only-of-type element is found in strict mode when tag is not specified.
        """
        html = """
            <div>
                <p>text 1</p>
                <p>text 2</p>
            </div>
            <div>Hello</div>
        """
        bs = find_body_element(to_bs(html))
        tag = OnlyOfType()

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True)

    def test_find_raises_exception_with_specified_tag_if_not_found_in_strict_mode(self):
        """
        Tests if find method raises TagNotFoundException
        if no only-of-type element is found in strict mode when tag is specified.
        """
        html = """
            <div>
                <p>text 1</p>
                <p>text 2</p>
            </div>
            <span>Hello</span>
        """
        bs = find_body_element(to_bs(html))
        tag = OnlyOfType("p")

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True)

    def test_find_all_returns_empty_list_if_no_only_elements_found_without_tag(self):
        """
        Tests if find_all method returns empty list if no only-of-type elements
        are present in the tag markup and tag is not specified.
        """
        html = """
            <div>
                <p>text 1</p>
                <p>text 2</p>
            </div>
            <div></div>
        """
        bs = find_body_element(to_bs(html))
        tag = OnlyOfType()
        result = tag.find_all(bs)
        assert result == []

    def test_find_all_returns_empty_list_if_no_only_elements_found_with_tag(self):
        """
        Tests if find_all method returns empty list if no only-of-type elements
        of defined type are present in the tag markup. In this case, 'p' and 'a'
        are only-of-type elements, but they do not match the specified tag 'div'.
        """
        html = """
            <div>
                <p>text 1</p>
                <a>text 2</a>
            </div>
            <div></div>
        """
        bs = find_body_element(to_bs(html))
        tag = OnlyOfType("div")
        result = tag.find_all(bs)
        assert result == []

    def test_find_all_returns_all_only_of_type_elements_without_tag(self):
        """
        Tests if find_all method returns all only-of-type elements
        relative to their parent element when tag is not specified.
        """
        html = """
            <div>
                <p>text 1</p>
                <a>text 2</a>
            </div>
            <div>
                <p>text 3</p>
                <a>text 4</a>
                <a>text 5</a>
            </div>
            <span>text 6</span>
        """
        bs = find_body_element(to_bs(html))
        tag = OnlyOfType()
        result = tag.find_all(bs)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("<p>text 1</p>"),
            strip("<a>text 2</a>"),
            strip("<p>text 3</p>"),
            strip("<span>text 6</span>"),
        ]

    def test_find_all_returns_all_only_of_type_elements_with_tag(self):
        """
        Tests if find_all method returns all only-of-type elements
        of defined type when tag is specified.
        """
        html = """
            <div>
                <p>text 1</p>
                <a>text 2</a>
            </div>
            <div>
                <p>text 3</p>
                <a>text 4</a>
                <a>text 5</a>
            </div>
            <span>text 6</span>
        """
        bs = find_body_element(to_bs(html))
        tag = OnlyOfType("p")
        result = tag.find_all(bs)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("<p>text 1</p>"),
            strip("<p>text 3</p>"),
        ]
