"""
Module with integration tests for BaseModel component.
Tests various ways user is expected to interact with BaseModel.
"""

# mypy: disable-error-code="attr-defined, arg-type"

from dataclasses import dataclass

import pydantic
import pytest
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

import soupsavvy.exceptions as exc
from soupsavvy.models import All, Default, Required
from soupsavvy.models.base import BaseModel, Field
from soupsavvy.models.wrappers import FieldList
from soupsavvy.operations import (
    Break,
    Continue,
    Href,
    IfElse,
    Operation,
    SkipNone,
    Suppress,
)
from soupsavvy.operations.serialization import JSON
from soupsavvy.selectors.general import SelfSelector
from tests.soupsavvy.conftest import (
    MockClassMenuSelector,
    MockClassWidgetSelector,
    MockDivSelector,
    MockIntOperation,
    MockLinkSelector,
    MockPlus10Operation,
    MockSpanSelector,
    MockTextOperation,
    ToElement,
)
from tests.soupsavvy.models.conftest import (
    PRICE_SELECTOR,
    TITLE_SELECTOR,
    Base,
    MockModel,
    MockModelTitleField,
    MockPydanticBook,
    MockSABook,
    MockTitle,
)


@pytest.mark.integration
@pytest.mark.model
class TestBaseModelIntegration:
    """
    Class with integration tests for BaseModel component.
    It tests its behavior with various field and operation wrappers.
    """

    def test_nested_models_work_with_self_selector_for_the_same_scope(
        self, to_element: ToElement
    ):
        """
        Tests if SelfSelector can be used as a scope selector in nested models
        for cases where change of scope is not necessary.
        """

        class MockTitle(BaseModel):
            __scope__ = SelfSelector()

            name = MockLinkSelector() | MockTextOperation()

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            title = MockTitle
            price = PRICE_SELECTOR

        text = """
            <div>
                <a>Title</a>
                <p class="widget">10</p>
            </div>
        """
        bs = to_element(text)
        selector = MockModel

        result = selector.find(bs)
        assert result == MockModel(title=MockTitle(name="Title"), price=10)

    @pytest.mark.parametrize(argnames="strict", argvalues=[True, False])
    def test_raises_error_if_required_field_is_none(
        self, strict: bool, to_element: ToElement
    ):
        """
        Tests if FieldExtractionException is raised when required field is None.
        Required field must be present in scope. It does not matter if strict was set
        to True or False (as it applies only to scope), exception is always raised.
        """

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            title = Required(MockLinkSelector() | SkipNone(MockTextOperation()))
            price = PRICE_SELECTOR

        text = """
            <div>
                <span>Title</span>
                <p class="widget">10</p>
            </div>
        """
        bs = to_element(text)
        selector = MockModel

        with pytest.raises(exc.FieldExtractionException, match="title"):
            selector.find(bs, strict=strict)

    @pytest.mark.parametrize(argnames="strict", argvalues=[True, False])
    def test_raises_error_if_required_model_field_is_none(
        self, strict: bool, to_element: ToElement
    ):
        """
        Tests if FieldExtractionException is raised when required model field is None.
        If scope of nested model is not found, and field is wrapped with Required,
        exception is raised. It does not matter if strict was set to True or False.
        """

        class MockInfo(BaseModel):
            __scope__ = MockSpanSelector()

            name = MockLinkSelector() | MockTextOperation()

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            title = TITLE_SELECTOR
            info = Required(MockInfo)

        text = """
            <div>
                <a>Title</a>
                <div>Nothing here</div>
            </div>
        """
        bs = to_element(text)
        selector = MockModel

        with pytest.raises(exc.FieldExtractionException, match="info"):
            selector.find(bs, strict=strict)

    def test_returns_default_if_extracted_model_field_is_none(
        self, to_element: ToElement
    ):
        """
        Tests if default value is returned if extracted model field is None.
        It happens when field scope is not found. Default model is returned.
        """

        class MockInfo(BaseModel):
            __scope__ = MockSpanSelector()

            name = MockLinkSelector() | MockTextOperation()

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            title = TITLE_SELECTOR
            info = Default(MockInfo, default=MockInfo(name="Not found"))

        text = """
            <div>
                <a>Title</a>
                <p class="widget">10</p>
            </div>
        """
        bs = to_element(text)
        selector = MockModel
        result = selector.find(bs)
        assert result == MockModel(title="Title", info=MockInfo(name="Not found"))

    def test_returns_default_if_extracted_field_is_none(self, to_element: ToElement):
        """
        Tests if default value is returned if extracted field, which selector is wrapped
        with Default, is None. If any error was raised by selector,
        it's propagated by Default, so any exception must be handled.
        """

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            title = Default(
                MockLinkSelector() | SkipNone(MockTextOperation()), "DefaultTitle"
            )
            price = PRICE_SELECTOR

        text = """
            <div>
                <span>Title</span>
                <p class="widget">10</p>
            </div>
        """
        bs = to_element(text)
        selector = MockModel
        result = selector.find(bs)
        assert result == MockModel(title="DefaultTitle", price=10)

    def test_default_propagates_errors_of_selector(self, to_element: ToElement):
        """
        Tests if Default propagates errors of selector, so if any exception was raised
        by selector, it raises FieldExtractionException. Default is only applied
        if selector did not raise any exception and returned None.
        In this case None is not handled in MockTextOperation, so it raises exception.
        """

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            title = Default(TITLE_SELECTOR, "DefaultTitle")
            price = PRICE_SELECTOR

        text = """
            <div>
                <span>Title</span>
                <p class="widget">10</p>
            </div>
        """
        bs = to_element(text)
        selector = MockModel

        with pytest.raises(exc.FieldExtractionException, match="title"):
            selector.find(bs)

    def test_default_does_not_overwrite_field_value_if_found(
        self, to_element: ToElement
    ):
        """
        Tests if Default does not overwrite field value if it was found by selector.
        Default is applied only if selector returned None.
        """

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            title = Default(TITLE_SELECTOR, "DefaultTitle")
            price = PRICE_SELECTOR

        text = """
            <div>
                <a>Title</a>
                <p class="widget">10</p>
            </div>
        """
        bs = to_element(text)
        selector = MockModel
        result = selector.find(bs)
        assert result == MockModel(title="Title", price=10)

    def test_failing_operation_is_cancelled_with_suppress_and_none_returned(
        self, to_element: ToElement
    ):
        """
        Tests if failing operation is cancelled with Suppress and None is returned.
        Suppress cancels any operation error and returns None instead. In this case,
        MockIntOperation raises error, but it's suppressed and price is None.
        """

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            title = TITLE_SELECTOR
            price = (
                MockClassWidgetSelector()
                | MockTextOperation()
                | Suppress(MockIntOperation())
            )

        text = """
            <div>
                <a>Title</a>
                <p class="widget">abc</p>
            </div>
        """
        bs = to_element(text)
        selector = MockModel
        result = selector.find(bs)
        assert result == MockModel(title="Title", price=None)

    def test_operation_is_cancelled_and_field_has_default(self, to_element: ToElement):
        """
        Tests if operation is cancelled with Suppress and field has default value,
        when selector is wrapped with Default. Suppress cancels MockIntOperation error,
        and returns None. Default is applied to None value and price is set to 0.
        """

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            title = TITLE_SELECTOR
            price = Default(
                MockClassWidgetSelector()
                | MockTextOperation()
                | Suppress(MockIntOperation()),
                0,
            )

        text = """
            <div>
                <a>Title</a>
                <p class="widget">abc</p>
            </div>
        """
        bs = to_element(text)
        selector = MockModel
        result = selector.find(bs)
        assert result == MockModel(title="Title", price=0)

    def test_skip_none_is_applied_to_skip_operation(self, to_element: ToElement):
        """
        Tests if SkipNone is applied to skip operation and None is returned.
        SkipNone is applied to MockPlus10Operation, which will raise error if previous
        step MockIntOperation failed.
        """

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            title = TITLE_SELECTOR
            price = (
                MockClassWidgetSelector()
                | MockTextOperation()
                | Suppress(MockIntOperation())
                | SkipNone(MockPlus10Operation())
            )

        text = """
            <div>
                <a>Title</a>
                <p class="widget">abc</p>
            </div>
        """
        bs = to_element(text)
        selector = MockModel
        result = selector.find(bs)
        assert result == MockModel(title="Title", price=None)

    def test_skip_none_propagates_value_if_not_none(self, to_element: ToElement):
        """
        Tests if SkipNone propagates value, and executes operation if value is not None.
        This way, operation can be optionally executed, if previous step did not fail.
        """

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            title = TITLE_SELECTOR
            price = (
                MockClassWidgetSelector()
                | MockTextOperation()
                | SkipNone(MockIntOperation())
            )

        text = """
            <div>
                <a>Title</a>
                <p class="widget">10</p>
            </div>
        """
        bs = to_element(text)
        selector = MockModel
        result = selector.find(bs)
        assert result == MockModel(title="Title", price=10)

    def test_all_returns_multiple_elements_in_list_for_field(
        self, to_element: ToElement
    ):
        """Tests if All returns multiple elements in list for field."""

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            title = TITLE_SELECTOR
            price = All(PRICE_SELECTOR)

        text = """
            <div>
                <a>Title</a>
                <p class="widget">10</p>
                <p class="widget">20</p>
                <a>Title2</a>
                <p>Hello</p>
                <p class="widget">30</p>
            </div>
        """
        bs = to_element(text)
        selector = MockModel
        result = selector.find(bs)

        assert result == MockModel(title="Title", price=[10, 20, 30])
        assert isinstance(result.price, FieldList)

    def test_all_returns_multiple_models_when_found(self, to_element: ToElement):
        """Tests if All returns list of models when wrapping model field."""

        class MockInfo(BaseModel):
            __scope__ = MockSpanSelector()

            name = MockLinkSelector() | MockTextOperation()

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            title = TITLE_SELECTOR
            info = All(MockInfo)

        text = """
            <div>
                <a>Title</a>
                <span><a>Walter</a></span>
                <span><a>White</a></span>
                <span><a>Heisenberg</a></span>
            </div>
        """
        bs = to_element(text)
        selector = MockModel
        result = selector.find(bs)

        assert result == MockModel(
            title="Title",
            info=[
                MockInfo(name="Walter"),
                MockInfo(name="White"),
                MockInfo(name="Heisenberg"),
            ],
        )
        assert isinstance(result.info, FieldList)

    def test_all_returns_empty_list_if_nothing_found_for_field(
        self, to_element: ToElement
    ):
        """
        Tests if All returns empty list if nothing found for field
        without raising any exception, as it wraps find_all method.
        """

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            title = TITLE_SELECTOR
            price = All(PRICE_SELECTOR)

        text = """
            <div>
                <a>Title</a>
                <a>Title2</a>
                <p>Hello</p>
            </div>
        """
        bs = to_element(text)
        selector = MockModel
        result = selector.find(bs)

        assert result == MockModel(title="Title", price=[])
        assert isinstance(result.price, FieldList)

    def test_ifelse_operation_evaluates_condition_properly(self, to_element: ToElement):
        """
        Tests if IfElse operation evaluates condition properly and applies
        correct operation to field. In this case, for title field, condition
        is True, so first operation is applied, for price field, condition is False,
        so second operation is applied.
        """

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            title = TITLE_SELECTOR | IfElse(
                lambda x: x == "Title",
                Operation(str.upper),
                Operation(str.lower),
            )
            price = PRICE_SELECTOR | IfElse(
                lambda x: x == 20,
                Operation(lambda x: x + 10),
                Operation(lambda x: x + 20),
            )

        text = """
            <div>
                <a>Title</a>
                <p class="widget">10</p>
            </div>
        """
        bs = to_element(text)
        selector = MockModel
        result = selector.find(bs)
        assert result == MockModel(title="TITLE", price=30)

    def test_ifelse_operation_conditionally_breaks_operation_pipeline(
        self, to_element: ToElement
    ):
        """
        Tests if IfElse operation conditionally breaks operation pipeline
        if Break operation is used and executed. In this case, only
        in title field Break is executed, so next operation is not executed.
        In price field, Break is not executed, so next operation is executed.
        """

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            title = (
                TITLE_SELECTOR
                | IfElse(
                    lambda x: x == "Title",
                    Break(),
                    Operation(str.lower),
                )
                | Operation(lambda x: x + "!")
            )
            price = (
                PRICE_SELECTOR
                | IfElse(
                    lambda x: x == 0,
                    Break(),
                    Operation(lambda x: x + 10),
                )
                | Operation(lambda x: 100 / x)
            )

        text = """
            <div>
                <a>Title</a>
                <p class="widget">10</p>
            </div>
        """
        bs = to_element(text)
        selector = MockModel
        result = selector.find(bs)
        assert result == MockModel(title="Title", price=5)

    def test_ifelse_operation_conditionally_skip_operation(self, to_element: ToElement):
        """
        Tests if IfElse operation conditionally skips operation if Continue
        operation is used. In this case, for title field, Continue is executed,
        so next pipeline skips to next operation. For price field, Continue is not
        executed, so else operation is executed, before next one in chain.
        """

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            title = (
                TITLE_SELECTOR
                | IfElse(
                    lambda x: x == "Title",
                    Continue(),
                    Operation(str.lower),
                )
                | Operation(lambda x: x + "!")
            )
            price = (
                PRICE_SELECTOR
                | IfElse(
                    lambda x: x == 20,
                    Continue(),
                    Operation(lambda x: x + 10),
                )
                | Operation(lambda x: x * 2)
            )

        text = """
            <div>
                <a>Title</a>
                <p class="widget">10</p>
            </div>
        """
        bs = to_element(text)
        selector = MockModel
        result = selector.find(bs)
        assert result == MockModel(title="Title!", price=40)

    def test_migration_to_pydantic_model(self):
        """
        Tests if model can be migrated to Pydantic model. If validation passes,
        Pydantic model is returned.
        """
        model = MockModel(title="Title", price=10)
        migrated = model.migrate(MockPydanticBook)

        assert isinstance(migrated, MockPydanticBook)
        assert migrated.title == "Title"
        assert migrated.price == 10

    def test_migration_to_pydantic_model_raises_error(self):
        """
        Tests if migration to Pydantic model raises error if validation fails.
        In this case, title is integer, but Pydantic model expects string.
        """
        model = MockModel(title=123, price=10)

        with pytest.raises(pydantic.ValidationError):
            model.migrate(MockPydanticBook)

    def test_migration_to_pydantic_model_with_model_fields(self):
        """
        Tests if model can be migrated to Pydantic model with model fields.
        Providing mapping for model fields to migrate them to another pydantic models.
        """

        class MockPydanticTitle(pydantic.BaseModel):
            name: str

        class MockPydanticBook(pydantic.BaseModel):
            title: MockPydanticTitle
            price: int

        model = MockModelTitleField(title=MockTitle(name="Title"), price=10)
        migrated = model.migrate(
            MockPydanticBook, mapping={MockTitle: MockPydanticTitle}
        )

        assert isinstance(migrated, MockPydanticBook)
        assert migrated.title == MockPydanticTitle(name="Title")
        assert migrated.price == 10

    def test_model_migration_to_sqlalchemy_model(self):
        """Tests migration of model to SQLAlchemy model."""
        model = MockModel(title="Title", price=10)
        migrated = model.migrate(MockSABook)

        assert isinstance(migrated, MockSABook)
        assert migrated.title == "Title"  # type: ignore
        assert migrated.price == 10  # type: ignore

    def test_migration_to_sqlalchemy_model_with_model_fields(self):
        """
        Tests if model can be migrated to SQLAlchemy model with model fields.
        Providing mapping for model fields to migrate them to another sqla models.
        """

        class MockSATitle(Base):
            __tablename__ = "title"

            id = Column(Integer, primary_key=True)
            name = Column(String, nullable=False)

        class MockSABookTitle(Base):
            __tablename__ = "book_title"

            id = Column(Integer, primary_key=True)
            title_id = Column(Integer, ForeignKey("title.id"), nullable=False)
            price = Column(Integer, nullable=True)

            title = relationship(MockSATitle.__name__, backref="book_title")

        model = MockModelTitleField(title=MockTitle(name="Title"), price=10)
        migrated = model.migrate(MockSABookTitle, mapping={MockTitle: MockSATitle})

        assert isinstance(migrated, MockSABookTitle)
        assert isinstance(migrated.title, MockSATitle)
        assert migrated.title.name == "Title"  # type: ignore
        assert migrated.price == 10  # type: ignore

    def test_works_with_soupsavvy_operations_as_fields(self, to_element: ToElement):
        """
        Tests if model works with soupsavvy operations as fields.
        Operations are operation-searcher mixins and can be used as fields
        to perform operation directly on scope element.
        """

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            title = TITLE_SELECTOR
            link = Href()
            id_ = Operation(lambda x: x.get_attribute("id"))
            name = Operation(lambda x: x.get_attribute("name")) | Operation(
                lambda x: x.upper()
            )

        text = """
            <div id="book1" href="www.book.com" name="Joe">
                <a>Title</a><p>Hello</p>
            </div>
        """
        bs = to_element(text)
        selector = MockModel
        result = selector.find(bs)
        assert result == MockModel(
            title="Title",
            link="www.book.com",
            id_="book1",
            name="JOE",
        )

    def test_field_with_compare_false_is_not_compared(self):
        """
        Tests if field with compare=False is ignored when comparing instances.
        This also applies to computing hash of the instance.
        """

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()
            __frozen__ = True

            title = TITLE_SELECTOR
            price = Field(PRICE_SELECTOR, compare=False)

        assert MockModel(title="Title", price=10) == MockModel(title="Title", price=20)
        assert hash(MockModel(title="Title", price=10)) == hash(
            MockModel(title="Title", price=20)
        )
        assert (
            MockModel(title="Title", price=10)
            != MockModel(title="Title2", price=10)
            != MockTitle(name="Title")
        )
        assert hash(MockModel(title="Title", price=10)) != hash(
            MockModel(title="Title2", price=10)
        )

    def test_field_with_repr_false_is_not_in_representation(self):
        """
        Tests if field with repr=False is ignored when creating representation
        of the instance. It also applies to string representation.
        """

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            title = TITLE_SELECTOR
            price = Field(PRICE_SELECTOR, repr=False)

        instance = MockModel(title="Title", price=10)
        assert repr(instance) == "MockModel(title='Title')" == str(instance)

    def test_field_with_migrate_false_is_not_migrated(self):
        """
        Tests if field with migrate=False is ignored when migrating instance
        to another class. It is not passed to constructor of target class.
        """

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            title = TITLE_SELECTOR
            price = Field(PRICE_SELECTOR, migrate=False)

        @dataclass
        class MockMigrationModel:
            title: str

        instance = MockModel(title="Title", price=10)
        migrated = instance.migrate(MockMigrationModel)

        assert isinstance(migrated, MockMigrationModel)
        assert migrated == MockMigrationModel(title="Title")

    def test_model_works_properly_when_all_fields_has_all_parameters_false(self):
        """
        Tests if model behaves properly when all its fields has all parameters
        set to False. Comparison checks only model class, representation has only
        class name, migration is without passing any parameters.
        """

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()
            __frozen__ = True

            title = Field(TITLE_SELECTOR, repr=False, compare=False, migrate=False)
            price = Field(PRICE_SELECTOR, repr=False, compare=False, migrate=False)

        @dataclass
        class MockMigrationModel: ...

        instance = MockModel(title="Title", price=10)

        assert repr(instance) == "MockModel()" == str(instance)
        assert (
            instance
            == MockModel(title="Title2", price=20)
            == MockModel(title="Title", price=10)
        )
        assert instance != MockTitle(name="Title")

        assert (
            hash(instance)
            == hash(MockModel(title="Title2", price=20))
            == hash(MockModel(title="Title", price=10))
        )

        migrated = instance.migrate(MockMigrationModel)
        assert isinstance(migrated, MockMigrationModel)
        assert migrated == MockMigrationModel()

    def test_find_methods_work_properly_on_field(self, to_element: ToElement):
        """
        Tests if find and find_all methods work properly when model field
        is directly defined as Field.
        """

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            title = Field(TITLE_SELECTOR, repr=False)
            price = Field(PRICE_SELECTOR, compare=False, migrate=False)

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
        bs = to_element(text)
        selector = MockModel
        result_find = selector.find(bs)
        assert result_find == MockModel(title="Title", price=10)

        result_all = selector.find_all(bs)
        assert result_all == [
            MockModel(title="Title", price=10),
            MockModel(title="Title2", price=20),
        ]

    def test_json_serialization_when_model_found(self, to_element: ToElement):
        """
        Tests if model combined with JSON operation works properly with find methods
        when models can be found in element.
        """
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
        bs = to_element(text)
        selector = MockModel

        pipe = selector | JSON()
        result = pipe.find(bs)
        assert result == {"title": "Title", "price": 10}

        result_all = pipe.find_all(bs)
        assert result_all == [
            {"title": "Title", "price": 10},
            {"title": "Title2", "price": 20},
        ]

    def test_raises_error_when_any_field_is_not_serializable(
        self, to_element: ToElement
    ):
        """
        Tests if pipeline raises FailedOperationExecution when any field
        of the model is not serializable to JSON. JSON operation fails
        and raises the exception.
        """

        class MockNotSerializable:
            pass

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            title = TITLE_SELECTOR | Operation(lambda x: MockNotSerializable())
            price = PRICE_SELECTOR

        text = """
            <div>
                <a>Title</a>
                <p class="widget">10</p>
            </div>
        """
        bs = to_element(text)
        pipe = MockModel | JSON()

        with pytest.raises(exc.FailedOperationExecution):
            pipe.find(bs)

    def test_json_serialization_when_model_not_found(self, to_element: ToElement):
        """
        Tests if model combined with JSON operation handles not found model as expected:
        - when strict is False, FailedOperationExecution is raised, as None
        object does not have `json` method.
        - when strict is True, ModelNotFoundException is raised, selector raises
        exception before operation is executed.
        - when using find_all, empty list is returned.
        """
        text = """
            <span>
                <a>Title2</a>
                <p class="widget">20</p>
            </span>
        """
        bs = to_element(text)
        selector = MockModel

        pipe = selector | JSON()

        with pytest.raises(exc.FailedOperationExecution):
            pipe.find(bs)

        with pytest.raises(exc.ModelNotFoundException):
            pipe.find(bs, strict=True)

        result_all = pipe.find_all(bs)
        assert result_all == []

    def test_json_serialization_for_nested_models(self, to_element: ToElement):
        """
        Tests if model combined with JSON operation works properly with nested models,
        where multiple models are serialized into nested dictionary.
        """

        class MockInfoModel(BaseModel):
            __scope__ = MockSpanSelector()

            title = TITLE_SELECTOR
            author = MockClassMenuSelector() | MockTextOperation()

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            info = MockInfoModel
            price = PRICE_SELECTOR

        text = """
            <div>
                <span>
                    <a>Hello</a>
                    <h1 class="menu">World</h1>
                </span>
                <p class="widget">20</p>
            </div>
            <div>
                <span>
                    <a>Hello2</a>
                    <h1 class="menu">World2</h1>
                </span>
                <p class="widget">200</p>
            </div>
        """
        bs = to_element(text)

        selector = MockModel
        pipe = selector | JSON()
        result = pipe.find(bs)

        assert result == {
            "info": {
                "title": "Hello",
                "author": "World",
            },
            "price": 20,
        }

        result_all = pipe.find_all(bs)
        assert result_all == [
            {
                "info": {
                    "title": "Hello",
                    "author": "World",
                },
                "price": 20,
            },
            {
                "info": {
                    "title": "Hello2",
                    "author": "World2",
                },
                "price": 200,
            },
        ]

    def test_json_serialization_for_nested_models_with_json_in_field(
        self, to_element: ToElement
    ):
        """
        Tests if model combined with JSON operation works properly with nested models,
        where JSON operation is used directly in field definition.
        selector.find() should return dict, json() should not change structure.
        """

        class MockInfoModel(BaseModel):
            __scope__ = MockSpanSelector()

            title = TITLE_SELECTOR
            author = MockClassMenuSelector() | MockTextOperation()

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            info = MockInfoModel | JSON()
            price = PRICE_SELECTOR

        text = """
            <div>
                <span>
                    <a>Hello</a>
                    <h1 class="menu">World</h1>
                </span>
                <p class="widget">20</p>
            </div>
        """
        bs = to_element(text)

        selector = MockModel

        model = selector.find(bs)
        assert isinstance(model, MockModel)
        assert model == MockModel(info={"title": "Hello", "author": "World"}, price=20)

        pipe = selector | JSON()
        result = pipe.find(bs)

        assert result == {
            "info": {
                "title": "Hello",
                "author": "World",
            },
            "price": 20,
        }

    def test_all_serialization_with_json_and_standard_objects(
        self, to_element: ToElement
    ):
        """
        Tests if pipeline with JSON operation works properly when All is used
        to extract multiple standard objects (int, str, etc.) in list.
        """

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            title = TITLE_SELECTOR
            price = All(PRICE_SELECTOR)

        text = """
            <div>
                <a>Title</a>
                <p class="widget">10</p>
                <p class="widget">20</p>
                <a>Title2</a>
                <p>Hello</p>
                <p class="widget">30</p>
            </div>
        """
        bs = to_element(text)

        pipe = MockModel | JSON()
        result = pipe.find(bs)
        expected = {"title": "Title", "price": [10, 20, 30]}
        assert result == expected

    def test_all_serialization_with_json_and_nested_models(self, to_element: ToElement):
        """
        Tests if pipeline with JSON operation works properly when All is used
        to extract multiple nested models. It should return serialized list of models
        in dictionary.
        """

        class MockInfoModel(BaseModel):
            __scope__ = MockSpanSelector()

            title = TITLE_SELECTOR
            author = MockClassMenuSelector() | MockTextOperation()

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            info = All(MockInfoModel)
            price = PRICE_SELECTOR

        text = """
            <div>
                <span>
                    <a>Hello</a>
                    <h1 class="menu">World</h1>
                </span>
                <span>
                    <a>Hello2</a>
                    <h1 class="menu">World2</h1>
                </span>
                <p class="widget">20</p>
            </div>
        """
        bs = to_element(text)

        pipe = MockModel | JSON()
        result = pipe.find(bs)

        assert result == {
            "info": [
                {"title": "Hello", "author": "World"},
                {"title": "Hello2", "author": "World2"},
            ],
            "price": 20,
        }
