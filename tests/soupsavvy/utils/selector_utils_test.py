"""Module for testing utilities for tag selectors."""

import pytest

from soupsavvy.interfaces import IElement
from soupsavvy.utils.selector_utils import TagIterator, TagResultSet, UniqueTag
from tests.soupsavvy.conftest import find_body_element, strip, to_element


@pytest.fixture(scope="module")
def mock_tag() -> IElement:
    """Fixture for creating a mock bs4.Tag."""
    text = """
        <div>
            <a class="link"></a>
            <div class="link">
                <a class="menu"></a>
                <a class="menu"></a>
            </div>
        </div>
        <span class="widget"></span>
    """
    return to_element(text)


@pytest.mark.selector
class TestUniqueTag:
    """Class with unit tests for UniqueTag class."""

    def test_hashes_tag_by_its_hash(self, mock_tag: IElement) -> None:
        """Tests that UniqueTag hashes tag by its hash."""
        tag = UniqueTag(mock_tag)
        assert hash(tag) == hash(mock_tag)

    def test_is_equal_to_unique_tag_with_the_same_tag(self, mock_tag: IElement) -> None:
        """
        Tests that UniqueTag is equal to another UniqueTag object with the same bs4.Tag.
        """
        tag1 = UniqueTag(mock_tag)
        tag2 = UniqueTag(mock_tag)
        assert tag1 == tag2

    def test_is_not_equal_to_bs4_tag_it_wraps(self, mock_tag: IElement) -> None:
        """
        Tests that UniqueTag is not equal to bs4.Tag object it wraps
        as they have different hashes.
        """
        tag1 = UniqueTag(mock_tag)
        assert tag1 != mock_tag

    def test_different_tags_with_same_content_have_different_hash(self):
        """
        Tests that two bs4.Tag objects with the same content wrapped by UniqueTag
        have different hashes and can be stored in set as different objects.
        """
        text = """<div class="menu"></div>"""
        tag1 = UniqueTag(to_element(text))
        tag2 = UniqueTag(to_element(text))

        assert hash(tag1) != hash(tag2)
        assert len({tag1, tag2}) == 2

    def test_is_not_equal_to_other_bs4_tag(self, mock_tag: IElement) -> None:
        """
        Tests that UniqueTag is not equal to other bs4.Tag then the one it wraps.
        """
        tag1 = UniqueTag(mock_tag)
        assert tag1 != mock_tag.find_all("div")[0]

    @pytest.mark.parametrize(
        argnames="other",
        argvalues=[1, "string"],
        ids=["int", "str"],
    )
    def test_is_not_equal_to_not_unique_tag_instance(
        self, mock_tag: IElement, other
    ) -> None:
        """
        Tests that UniqueTag is not equal to other objects then UniqueTag.
        Testing for int and str.
        """
        tag1 = UniqueTag(mock_tag)
        assert tag1 != other


class TestTagIterator:
    """Class with unit tests for TagIterator class."""

    def test_iterates_correctly_over_descendants_by_default(self, mock_tag: IElement):
        """
        Tests that TagIterator iterates over descendants by default
        and returns all tags in order of appearance.
        """
        tag = find_body_element(mock_tag)
        tag_iterator = TagIterator(tag)
        expected = [
            strip(
                """
                <div>
                    <a class="link"></a>
                    <div class="link">
                        <a class="menu"></a>
                        <a class="menu"></a>
                    </div>
                </div>
                """
            ),
            strip("""<a class="link"></a>"""),
            strip(
                """
                <div class="link">
                    <a class="menu"></a>
                    <a class="menu"></a>
                </div>
                """
            ),
            strip("""<a class="menu"></a>"""),
            strip("""<a class="menu"></a>"""),
            strip("""<span class="widget"></span>"""),
        ]
        assert [strip(str(tag)) for tag in tag_iterator] == expected

    def test_iterates_correctly_over_children_if_recursive_set_to_false(
        self, mock_tag: IElement
    ):
        """
        Tests that TagIterator iterates over children if recursive is set to False.
        """
        tag = find_body_element(mock_tag)
        tag_iterator = TagIterator(tag, recursive=False)
        expected = [
            strip(
                """
                <div>
                    <a class="link"></a>
                    <div class="link">
                        <a class="menu"></a>
                        <a class="menu"></a>
                    </div>
                </div>
                """
            ),
            strip("""<span class="widget"></span>"""),
        ]
        assert [strip(str(tag)) for tag in tag_iterator] == expected

    def test_iterator_resets_when_called_again(self, mock_tag: IElement):
        """
        Tests that iterator resets when called again.
        Calling __iter__ method of TagIterator resets the iterator to the beginning.
        """
        tag = find_body_element(mock_tag)
        tag_iterator = TagIterator(tag)

        iter_ = iter(tag_iterator)
        # first tag
        expected = strip(
            """
                <div>
                    <a class="link"></a>
                    <div class="link">
                        <a class="menu"></a>
                        <a class="menu"></a>
                    </div>
                </div>
            """
        )
        assert strip(str(next(iter_))) == expected

        iter_ = iter(tag_iterator)
        assert strip(str(next(iter_))) == expected

    def test_iterates_over_no_elements_iterable(self, mock_tag: IElement):
        """
        Tests that TagIterator iterates over no elements if tag has no children.
        In this case expected result is an empty list.
        """
        # span element has no children
        tag = mock_tag.find_all("span")[0]
        tag_iterator = TagIterator(tag)  # type: ignore
        assert list(tag_iterator) == []

    def test_skips_elements_that_are_not_tags(self, mock_tag: IElement):
        """
        Tests that TagIterator skips all elements that are not bs4.Tag.
        Iterators over elements implemented in bs4.Tag contain strings, which need
        to be skipped.
        """

        class TagWrapper:
            def __init__(self, tag):
                self._tag = tag

            def __getattr__(self, attr):
                if attr == "descendants":
                    return iter(["string", "string2", 12])
                return getattr(self._tag, attr)

        tag = TagWrapper(mock_tag)
        tag_iterator = TagIterator(tag)  # type: ignore
        assert list(tag_iterator) == []

    def test_includes_provided_tag_and_descendants_if_include_self_true(
        self, mock_tag: IElement
    ):
        """
        Tests that TagIterator iterates over descendants and includes the tag itself
        at the beginning if include_self is set to True.
        """
        tag = find_body_element(mock_tag)
        tag_iterator = TagIterator(tag, include_self=True)
        expected = [
            strip(
                """
                <body>
                    <div>
                        <a class="link"></a>
                        <div class="link">
                            <a class="menu"></a>
                            <a class="menu"></a>
                        </div>
                    </div>
                    <span class="widget"></span>
                </body>
                """
            ),
            strip(
                """
                <div>
                    <a class="link"></a>
                    <div class="link">
                        <a class="menu"></a>
                        <a class="menu"></a>
                    </div>
                </div>
                """
            ),
            strip("""<a class="link"></a>"""),
            strip(
                """
                <div class="link">
                    <a class="menu"></a>
                    <a class="menu"></a>
                </div>
                """
            ),
            strip("""<a class="menu"></a>"""),
            strip("""<a class="menu"></a>"""),
            strip("""<span class="widget"></span>"""),
        ]
        assert [strip(str(tag)) for tag in tag_iterator] == expected

    def test_includes_provided_tag_and_children_if_include_self_true(
        self, mock_tag: IElement
    ):
        """
        Tests that TagIterator iterates over children and includes the tag itself
        at the beginning if include_self is set to True and recursive is False.
        """
        tag = find_body_element(mock_tag)
        tag_iterator = TagIterator(tag, recursive=False, include_self=True)
        expected = [
            strip(
                """
                <body>
                    <div>
                        <a class="link"></a>
                        <div class="link">
                            <a class="menu"></a>
                            <a class="menu"></a>
                        </div>
                    </div>
                    <span class="widget"></span>
                </body>
                """
            ),
            strip(
                """
                <div>
                    <a class="link"></a>
                    <div class="link">
                        <a class="menu"></a>
                        <a class="menu"></a>
                    </div>
                </div>
                """
            ),
            strip("""<span class="widget"></span>"""),
        ]
        assert [strip(str(tag)) for tag in tag_iterator] == expected


class TestTagResultSet:
    """Class with unit tests for TagResultSet class."""

    @pytest.fixture(scope="class")
    def mock_tags(self) -> list[IElement]:
        text = """
            <a class="menu"></a>
            <a class="menu"></a>
            <a class="menu1"></a>
            <a class="menu2"></a>
        """
        return to_element(text).find_all("body")[0].find_all()

    def test_result_set_can_be_initialized_with_empty_collection(self):
        """
        Tests that TagResultSet can be initialized with empty collection.
        When initialized with no arguments, result set is empty
        and fetch method returns an empty list.
        """
        result = TagResultSet().fetch()
        assert result == []

    def test_fetch_returns_all_tags_if_they_are_unique(self, mock_tags: list[IElement]):
        """
        Tests that fetch method returns all tags if they are unique.
        When all tags have unique id, there is no repetition and all tags are returned.
        """
        results_set = TagResultSet(mock_tags)
        result = results_set.fetch()

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="menu"></a>"""),
            strip("""<a class="menu"></a>"""),
            strip("""<a class="menu1"></a>"""),
            strip("""<a class="menu2"></a>"""),
        ]

    def test_fetch_returns_n_tags_when_limit_is_set(self, mock_tags: list[IElement]):
        """Tests that fetch method returns n first unique tags when limit is set."""
        results_set = TagResultSet(mock_tags)
        result = results_set.fetch(3)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="menu"></a>"""),
            strip("""<a class="menu"></a>"""),
            strip("""<a class="menu1"></a>"""),
        ]

    def test_fetch_returns_all_unique_tags_when_duplicated(
        self, mock_tags: list[IElement]
    ):
        """
        Tests that fetch method returns all unique tags when there are duplicates.
        Initial collection has duplicated tags, but fetch should filter them out
        and return only unique tags in order of appearance.
        """
        results_set = TagResultSet(mock_tags + mock_tags)
        result = results_set.fetch()

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="menu"></a>"""),
            strip("""<a class="menu"></a>"""),
            strip("""<a class="menu1"></a>"""),
            strip("""<a class="menu2"></a>"""),
        ]

    def test_updates_return_new_result_set_with_updated_collection(
        self, mock_tags: list[IElement]
    ):
        """
        Tests that | operator updates collection and returns new result set.
        New collection is a union of two collections with first as a base,
        which means that all new tags should be appended at the end in order
        of their appearance in the second collection.

        To test this assumption, second collection is reversed to have
        different order of common tags then the base collection.
        """
        base = TagResultSet(mock_tags[:2])
        right = TagResultSet(list(reversed(mock_tags[1:3])))

        new = base | right
        result = new.fetch()

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="menu"></a>"""),
            strip("""<a class="menu"></a>"""),
            strip("""<a class="menu1"></a>"""),
        ]

    def test_updates_when_one_result_set_is_empty(self, mock_tags: list[IElement]):
        """
        Tests that | operator updates collection and returns new result set
        when one of the collections is empty, whether base or right.
        """
        base = TagResultSet()
        right = TagResultSet(mock_tags)

        expected = [
            strip("""<a class="menu"></a>"""),
            strip("""<a class="menu"></a>"""),
            strip("""<a class="menu1"></a>"""),
            strip("""<a class="menu2"></a>"""),
        ]

        new = base | right
        result = new.fetch()
        assert list(map(lambda x: strip(str(x)), result)) == expected

        new = right | base
        result = new.fetch()
        assert list(map(lambda x: strip(str(x)), result)) == expected

    def test_updates_when_collections_are_the_same_return_base_collection(
        self, mock_tags: list[IElement]
    ):
        """
        Tests that | operator updates collection and returns base collection
        when both collections are the same.

        In this case testing on reversed collection to have different order of tags
        and asserting that result set is in the same order as the base collection.
        """
        base = TagResultSet(mock_tags)
        right = TagResultSet(list(reversed(mock_tags)))

        new = base | right
        result = new.fetch()

        expected = [
            strip("""<a class="menu"></a>"""),
            strip("""<a class="menu"></a>"""),
            strip("""<a class="menu1"></a>"""),
            strip("""<a class="menu2"></a>"""),
        ]
        assert list(map(lambda x: strip(str(x)), result)) == expected

    def test_and_return_new_result_set_with_intersection_of_collections(
        self, mock_tags: list[IElement]
    ):
        """
        Tests that & operator returns new result set with intersection of collections.
        New collection is an intersection of two collections with first as a base,
        which preserves the order of first collection in the result.

        To test this assumption, second collection is reversed to have
        different order of common tags then the base collection.
        """
        base = TagResultSet(mock_tags[:3])
        right = TagResultSet(list(reversed(mock_tags[1:])))

        new = base & right
        result = new.fetch()

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="menu"></a>"""),
            strip("""<a class="menu1"></a>"""),
        ]

    def test_and_returns_empty_result_set_when_no_difference(
        self, mock_tags: list[IElement]
    ):
        """
        Tests that - operator returns empty result set when there is no difference.
        All elements from base collection are in the right collection.
        In that case, result set should be empty.
        """
        base = TagResultSet(mock_tags[:2])
        right = TagResultSet(mock_tags)

        new = base - right
        result = new.fetch()
        assert result == []

    def test_and_return_new_result_set_with_difference_of_collections(
        self, mock_tags: list[IElement]
    ):
        """
        Tests that - operator returns new result set with difference of collections.
        New collection is a difference between base and right collections,
        output set should contain only tags that are in the base collection
        but not in the right collection with base collection initial order preserved.
        """
        base = TagResultSet(mock_tags)
        right = TagResultSet(list(reversed(mock_tags[:2])))

        new = base - right
        result = new.fetch()

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="menu1"></a>"""),
            strip("""<a class="menu2"></a>"""),
        ]

    def test_and_returns_empty_result_set_when_no_intersection(
        self, mock_tags: list[IElement]
    ):
        """
        Tests that & operator returns empty result set when there is no intersection.
        In that case, result set should be empty.
        """
        base = TagResultSet(mock_tags[:2])
        right = TagResultSet(mock_tags[2:])

        new = base & right
        result = new.fetch()
        assert result == []

    def test_len_returns_number_of_tags_in_collection(self, mock_tags: list[IElement]):
        """Tests that len method returns number of tags in collection."""
        assert len(TagResultSet(mock_tags)) == 4
        assert len(TagResultSet(mock_tags[:2])) == 2
        assert len(TagResultSet()) == 0

    def test_bool_returns_true_if_collection_not_empty(self, mock_tags: list[IElement]):
        """Tests that bool method returns True if collection is not empty."""
        assert bool(TagResultSet(mock_tags)) is True
        assert bool(TagResultSet(mock_tags[:2])) is True
        assert bool(TagResultSet()) is False

    def test_symmetric_difference_with_result_from_both_sets(
        self, mock_tags: list[IElement]
    ):
        """
        Tests that symmetric_difference returns new result set
        with symmetric difference of collections, in case when both collections
        have tags that are not in the other collection.
        Tags form base collection precede tags from right collection.
        """
        base = TagResultSet(mock_tags[:3])
        right = TagResultSet(mock_tags[1:])

        new = base.symmetric_difference(right)
        result = new.fetch()

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="menu"></a>"""),
            strip("""<a class="menu2"></a>"""),
        ]

    def test_symmetric_difference_returns_empty_list(self, mock_tags: list[IElement]):
        """
        Tests that symmetric_difference returns empty result set when intersection
        of two collection is equal to their union.
        """
        base = TagResultSet(mock_tags[:2])
        right = TagResultSet(mock_tags[:2])

        new = base.symmetric_difference(right)
        result = new.fetch()
        assert result == []

    def test_symmetric_difference_with_results_from_right(
        self, mock_tags: list[IElement]
    ):
        """
        Tests that symmetric_difference returns new result set with extra tags
        appear only in the right collection.
        """
        base = TagResultSet(mock_tags[:2])
        right = TagResultSet(mock_tags[:3])

        new = base.symmetric_difference(right)
        result = new.fetch()

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="menu1"></a>"""),
        ]

    def test_symmetric_difference_with_results_from_base(
        self, mock_tags: list[IElement]
    ):
        """
        Tests that symmetric_difference returns new result set with extra tags
        appear only in the base collection.
        """
        base = TagResultSet(mock_tags[:3])
        right = TagResultSet(mock_tags[1:3])

        new = base.symmetric_difference(right)
        result = new.fetch()

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="menu"></a>"""),
        ]

    def test_symmetric_difference_with_no_intersection(self, mock_tags: list[IElement]):
        """
        Tests that symmetric_difference returns new result set with all tags
        when there is no intersection between collections
        """
        base = TagResultSet(mock_tags[:2])
        right = TagResultSet(mock_tags[2:])

        new = base.symmetric_difference(right)
        result = new.fetch()

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="menu"></a>"""),
            strip("""<a class="menu"></a>"""),
            strip("""<a class="menu1"></a>"""),
            strip("""<a class="menu2"></a>"""),
        ]
