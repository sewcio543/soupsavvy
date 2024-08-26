"""
Module with unit tests for BaseModel component,
which is parent class of all user-defined models.
"""

import pytest

from soupsavvy.exceptions import (
    FieldExtractionException,
    FieldsNotDefinedException,
    MissingFieldsException,
    ModelScopeNotFoundException,
    NotSoupSelectorException,
    ScopeNotDefinedException,
)
from soupsavvy.models.base import BaseModel
from tests.soupsavvy.operations.conftest import MockIntOperation, MockTextOperation
from tests.soupsavvy.selectors.conftest import (
    MockClassWidgetSelector,
    MockDivSelector,
    MockLinkSelector,
    find_body_element,
    to_bs,
)

SCOPE = MockDivSelector()
TITLE_SELECTOR = MockLinkSelector() | MockTextOperation()
PRICE_SELECTOR = MockClassWidgetSelector() | MockTextOperation() | MockIntOperation()


class MockModel(BaseModel):
    __scope__ = SCOPE

    title = TITLE_SELECTOR
    price = PRICE_SELECTOR


class TestBaseModel:
    def test_isssssnit(self):
        assert MockModel.__scope__ == MockDivSelector()

    def test_isssnit(self):
        with pytest.raises(ScopeNotDefinedException):

            class MockModel(BaseModel):
                title = MockLinkSelector() | MockTextOperation()

    def test_isssni11t(self):
        with pytest.raises(FieldsNotDefinedException):

            class MockModel(BaseModel):
                __scope__ = MockDivSelector()

    def test_isyssnit(self):
        with pytest.raises(MissingFieldsException):
            MockModel(title="Title")

    def test_isssnisst(self):
        with pytest.raises(NotSoupSelectorException):

            class MockModel(BaseModel):
                __scope__ = MockTextOperation()

                title = TITLE_SELECTOR

    def test_isssnisst2(self):
        assert MockModel.fields == {"title": TITLE_SELECTOR, "price": PRICE_SELECTOR}

    def test_isssnisst3(self):
        name_selector = MockClassWidgetSelector() | MockTextOperation()

        class ChildModel(MockModel):
            name = name_selector

        assert ChildModel.fields == {
            "title": TITLE_SELECTOR,
            "price": PRICE_SELECTOR,
            "name": name_selector,
        }

    def test_isssn2isst3(self):
        class ChildModel(MockModel):
            def __post_init__(self) -> None:
                self.title = self.title + "!"

        model = ChildModel(title="Title", price=10)

        assert model.title == "Title!"
        assert model.price == 10

    def test_isssnisst4(self):
        name_selector = MockClassWidgetSelector() | MockTextOperation()

        class ChildModel(MockModel):
            __inherit_fields__ = False

            name = name_selector

        assert ChildModel.fields == {"name": name_selector}

    def test_init(self):
        text = """
            <div>
                <a>Title</a>
                <p class="widget">10</p>
            </div>
        """
        bs = to_bs(text)
        selector = MockModel
        result = selector.find(bs)

        assert result == MockModel(title="Title", price=10)
        assert result.title == "Title"
        assert result.price == 10

    def test_init1111(self):
        text = """
            <span>
                <div>
                    <a>Title</a>
                    <p class="widget">10</p>
                </div>
            </span>
        """
        bs = find_body_element(to_bs(text))
        selector = MockModel
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_init11121(self):
        text = """
            <span>
                <div>
                    <a>Title</a>
                    <p class="widget">10</p>
                </div>
            </span>
        """
        bs = find_body_element(to_bs(text))
        selector = MockModel

        with pytest.raises(ModelScopeNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_init11(self):
        text = """
            <span>
                <div>
                    <a>Title</a>
                    <p class="widget">10</p>
                </div>
            </span>
            <div>
                <a>Title2</a>
                <p class="widget">20</p>
            </div>
        """
        bs = find_body_element(to_bs(text))
        selector = MockModel
        result = selector.find(bs, recursive=False)
        assert result == MockModel(title="Title2", price=20)

    def test_ss_inist(self):
        text = """
            <span>
                <a>Title</a>
                <p class="widget">10</p>
            </span>
        """
        bs = to_bs(text)
        selector = MockModel
        result = selector.find(bs)
        assert result is None

    def test_inist(self):
        text = """
            <span>
                <a>Title</a>
                <p class="widget">10</p>
            </span>
        """
        bs = to_bs(text)
        selector = MockModel

        with pytest.raises(ModelScopeNotFoundException):
            selector.find(bs, strict=True)

    def test_inisst(self):
        text = """
            <div>
                <a>Title</a>
                <p class="widget">10</p>
            </div>
            <div>
                <a>Title2</a>
                <p class="widget">20</p>
            </div>
        """
        bs = to_bs(text)
        selector = MockModel
        result = selector.find(bs)
        assert result == MockModel(title="Title", price=10)

    def test_iniseeest(self):
        text = """
            <div>
                <a>Title</a>
                <p class="widget">abc</p>
            </div>
        """
        bs = to_bs(text)
        selector = MockModel

        with pytest.raises(FieldExtractionException, match="price"):
            selector.find(bs)

    def test_iniseeestaa(self):
        text = """
            <div>
                <p class="widget">10</p>
            </div>
        """
        bs = to_bs(text)
        selector = MockModel

        with pytest.raises(FieldExtractionException, match="title"):
            selector.find(bs, strict=True)

    def test_iniseeest11aa(self):
        text = """
            <div>
                <p class="widget">10</p>
            </div>
        """
        bs = to_bs(text)
        selector = MockModel
        result = selector.find(bs)
        assert result == MockModel(title=None, price=10)
        assert result.title is None

    def test_inissst(self):
        text = """
            <div>
                <a>Title</a>
                <p class="widget">10</p>
            </div>
            <div>
                <a>Title2</a>
                <p class="widget">20</p>
            </div>
        """
        bs = to_bs(text)
        selector = MockModel
        result = selector.find_all(bs)
        assert result == [
            MockModel(title="Title", price=10),
            MockModel(title="Title2", price=20),
        ]

    def test_inisss11t(self):
        text = """
            <span>
                <div>
                    <a>Title</a>
                    <p class="widget">10</p>
                </div>
            </span>
            <div>
                <a>Title2</a>
                <p class="widget">20</p>
            </div>
            <div>
                <a>Title3</a>
                <p class="widget">30</p>
            </div>
        """
        bs = find_body_element(to_bs(text))
        selector = MockModel
        result = selector.find_all(bs, recursive=False)
        assert result == [
            MockModel(title="Title2", price=20),
            MockModel(title="Title3", price=30),
        ]

    def test_inisssas11t(self):
        text = """
            <span>
                <div>
                    <a>Title</a>
                    <p class="widget">10</p>
                </div>
            </span>
            <div>
                <a>Title2</a>
                <p class="widget">20</p>
            </div>
            <div>
                <a>Title3</a>
                <p class="widget">30</p>
            </div>
            <div>
                <a>Title4</a>
                <p class="widget">40</p>
            </div>
        """
        bs = find_body_element(to_bs(text))
        selector = MockModel
        result = selector.find_all(bs, recursive=False, limit=2)
        assert result == [
            MockModel(title="Title2", price=20),
            MockModel(title="Title3", price=30),
        ]

    def test_inisssas11t1(self):
        text = """
            <span>
                <div>
                    <a>Title</a>
                    <p class="widget">10</p>
                </div>
            </span>
            <div>
                <a>Title2</a>
                <p class="widget">20</p>
            </div>
            <div>
                <a>Title3</a>
                <p class="widget">30</p>
            </div>
        """
        bs = find_body_element(to_bs(text))
        selector = MockModel
        result = selector.find_all(bs, limit=2)
        assert result == [
            MockModel(title="Title", price=10),
            MockModel(title="Title2", price=20),
        ]

    def test_iniswsst(self):
        text = """
            <span>
                <a>Title</a>
                <p class="widget">10</p>
            </div>
        """
        bs = to_bs(text)
        selector = MockModel
        result = selector.find_all(bs)
        assert result == []

    @pytest.mark.parametrize(
        "models",
        [
            (MockModel(title="Title", price=10), MockModel(title="Title", price=10)),
        ],
    )
    def test_isssn2isst33(self, models):
        assert (models[0] == models[1]) is True

    @pytest.mark.parametrize(
        "models",
        [
            (MockModel(title="Title", price=10), MockModel(title="Title2", price=20)),
            (MockModel(title="Title", price=10), MockModel(title="Title2", price=10)),
            (MockModel(title="Title", price=10), MockModel(title="Title", price=20)),
        ],
    )
    def test_isssn2iasst33(self, models):
        assert (models[0] == models[1]) is False
