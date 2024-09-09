"""
Module with unit tests for BaseModel component,
which is parent class of all user-defined models.
"""

import pydantic
import pytest
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase

from soupsavvy.exceptions import (
    FieldExtractionException,
    FieldsNotDefinedException,
    MissingFieldsException,
    ModelNotFoundException,
    NotSoupSelectorException,
    ScopeNotDefinedException,
    UnknownModelFieldException,
)
from soupsavvy.models.base import BaseModel
from soupsavvy.models.wrappers import All, Default, Required, SkipNone, Suppress
from soupsavvy.operations import Href, Operation, Text
from tests.soupsavvy.operations.conftest import (
    MockIntOperation,
    MockPlus10Operation,
    MockTextOperation,
)
from tests.soupsavvy.selectors.conftest import (
    MockClassMenuSelector,
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
    """
    Mock model for testing user-defined model, which is subclass of BaseModel.
    Simple model with two fields: title and price and div scope.
    """

    __scope__ = SCOPE

    title = TITLE_SELECTOR
    price = PRICE_SELECTOR


class MockNotEqualModel(BaseModel):
    """
    Mock model for testing model equality, if two instances of models are of different type,
    they are never equal, even if they have the same attributes.
    """

    __scope__ = SCOPE

    title = TITLE_SELECTOR
    price = PRICE_SELECTOR


class MockAllowEmptyTitle(BaseModel):
    """
    Mock model for testing case, when title can be empty and it's handled properly.
    """

    __scope__ = MockDivSelector()

    title = MockLinkSelector() | MockTextOperation(skip_none=True)
    price = PRICE_SELECTOR


class MockMigrationModel:
    """Mock class for testing migration to any custom model."""

    def __init__(self, title: str, price: int, **kwargs) -> None:
        self.title = title
        self.price = price

        for key, value in kwargs.items():
            setattr(self, key, value)

        if "error" in kwargs:
            raise ValueError("Forbidden key in kwargs")


class MockPydanticBook(pydantic.BaseModel):
    """Mock model for testing migration to Pydantic model."""

    title: str
    price: int


class Base(DeclarativeBase): ...


class MockSABook(Base):
    """Mock model for testing migration to SQLAlchemy model."""

    __tablename__ = "book"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=True)
    price = Column(Integer, nullable=True)


@pytest.mark.model
class TestBaseModel:
    """Class with unit tests for BaseModel component."""

    def test_scope_is_properly_defined_in_model(self):
        """
        Tests if required class attribute __scope__ is properly defined in model.
        It should be stored both in __scope__ and scope attributes.
        """
        assert MockModel.__scope__ is SCOPE
        assert MockModel.scope is SCOPE

    def test_raises_error_when_creating_model_class_without_scope(self):
        """
        Tests if ScopeNotDefinedException is raised when __scope__ is not defined in model.
        It's mandatory attribute to define in model.
        """

        with pytest.raises(ScopeNotDefinedException):

            class MockModel(BaseModel):
                title = MockLinkSelector() | MockTextOperation()

    def test_raises_error_when_creating_model_class_without_fields(self):
        """
        Tests if FieldsNotDefinedException is raised when fields are not defined in model.
        At least one field must be defined in model to make sense and work properly.
        Fields is class attribute with value of instance `TagSearcher`.
        """

        with pytest.raises(FieldsNotDefinedException):

            class MockModel(BaseModel):
                __scope__ = MockDivSelector()

    def test_raises_error_on_init_if_field_missing_in_kwargs(self):
        """
        Tests if MissingFieldsException is raised when field is missing in kwargs
        during model initialization. All fields must be provided, only as keyword arguments.
        This is not usual way of creating models, which should be done with find methods.
        """

        with pytest.raises(MissingFieldsException):
            MockModel(title="Title")

    def test_raises_error_on_init_if_unknown_field(self):
        """
        Tests if UnknownModelFieldException is raised when unknown field is passed
        to model constructor. Only fields defined in model class are allowed.
        """

        with pytest.raises(UnknownModelFieldException):
            MockModel(title="Title", price=10, name="Name")

    def test_raises_error_when_scope_is_not_soup_selector(self):
        """
        Tests if NotSoupSelectorException is raised on creating class
        when __scope__ is not instance of SoupSelector.
        """

        with pytest.raises(NotSoupSelectorException):

            class MockModel(BaseModel):
                __scope__ = MockTextOperation()  # type: ignore

                title = TITLE_SELECTOR

    def test_class_attribute_fields_is_defined_correctly(self):
        """
        Tests if class attribute fields is defined correctly in model.
        It should be dictionary with field names as keys and provided selectors as values.
        """
        assert MockModel.fields == {"title": TITLE_SELECTOR, "price": PRICE_SELECTOR}

    def test_class_attribute_fields_contains_inherited_and_model_fields(self):
        """
        Tests if class attribute fields contains both inherited fields
        from base class and fields defined in model. Inheriting fields behavior is default,
        but can be overridden by setting __inherit_fields__ to False.
        """
        name_selector = MockClassWidgetSelector() | MockTextOperation()

        class ChildModel(MockModel):
            name = name_selector

        assert ChildModel.fields == {
            "title": TITLE_SELECTOR,
            "price": PRICE_SELECTOR,
            "name": name_selector,
        }

    def test_fields_are_not_inherited_from_base_class_if_explicitly_set(self):
        """
        Tests if fields are not inherited from base class
        if __inherit_fields__ is set to False.
        """
        name_selector = MockClassWidgetSelector() | MockTextOperation()

        class ChildModel(MockModel):
            __inherit_fields__ = False

            name = name_selector

        assert ChildModel.fields == {"name": name_selector}

    def test_custom_post_init_modifies_attributes(self):
        """
        Tests if custom __post_init__ method modifies attributes of model instance.
        This is inspired from python dataclasses, where __post_init__ method is executed
        after initialization of instance. Tests if attributes property
        contains modified values.
        """

        class ChildModel(MockModel):
            def __post_init__(self) -> None:
                self.title = self.title + "!"  # type: ignore

        model = ChildModel(title="Title", price=10)

        assert model.title == "Title!"
        assert model.price == 10
        assert model.attributes == {"title": "Title!", "price": 10}

    def test_attributes_returns_modified_field_values(self):
        """
        Tests if attributes property returns modified field values of model instance.
        If any field value was changed at any time,
        it should be reflected in attributes.
        """
        model = MockModel(title="Title", price=10)

        model.title = "Title!"  # type: ignore
        assert model.attributes == {"title": "Title!", "price": 10}

    def test_model_has_correct_string_representation(self):
        """
        Tests if every model has correct string representation. It should contain
        class name and all fields with their repr values.
        """
        model = MockModel(title="Title", price=10)
        expected = f"MockModel(title={repr(model.title)}, price={repr(model.price)})"
        assert str(model) == expected == repr(model)

    def test_find_returns_first_found_model_instance(self):
        """Tests if find method returns model instance within first found scope."""
        text = """
            <span>
                <a>Not matching scope</a>
                <p class="widget">10</p>
            </span>
            <div>
                <p>Extra information</p>
                <a>Title</a>
                <p class="widget">10</p>
                <a>Not first anchor element</p>
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
        assert result.title == "Title"
        assert result.price == 10
        assert result.attributes == {"title": "Title", "price": 10}

    def test_find_returns_none_if_no_scope_found_and_strict_false(self):
        """
        Tests if find method returns None if no scope is found in provided bs object
        and strict is set to False. It should not raise any exception.
        """
        text = """
            <span>
                <a>Title</a>
                <p class="widget">10</p>
            </span>
            <a>Title2</a>
            <p class="widget">20</p>
        """
        bs = to_bs(text)
        selector = MockModel
        result = selector.find(bs)
        assert result is None

    def test_find_raises_error_when_no_scope_found_and_strict_true(self):
        """
        Tests if ModelNotFoundException is raised when no scope is found
        in provided bs object and strict is set to True. Strict option works similar way
        as in selectors, when no match was found, exception is raised.
        """
        text = """
            <span>
                <a>Title</a>
                <p class="widget">10</p>
            </span>
            <a>Not in scope</a>
            <p class="widget">20</p>
        """
        bs = to_bs(text)
        selector = MockModel

        with pytest.raises(ModelNotFoundException):
            selector.find(bs, strict=True)

    def test_find_returns_none_if_no_scope_found_with_recursive_false_and_strict_false(
        self,
    ):
        """
        Tests if find method returns None if no scope is found in provided bs object,
        recursive is set to False and strict is set to False.
        """
        text = """
            <span>
                <div>
                    <a>Not a child</a>
                    <p class="widget">10</p>
                </div>
            </span>
            <a>Title</a>
            <p class="widget">20</p>
        """
        bs = find_body_element(to_bs(text))
        selector = MockModel
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_error_if_no_scope_found_with_recursive_false_and_strict_true(
        self,
    ):
        """
        Tests if ModelNotFoundException is raised when no scope is found
        in provided bs object, recursive is set to False and strict is set to True.
        """
        text = """
            <span>
                <div>
                    <a>Not a child</a>
                    <p class="widget">10</p>
                </div>
            </span>
            <a>Not in scope</a>
            <p class="widget">20</p>
        """
        bs = find_body_element(to_bs(text))
        selector = MockModel

        with pytest.raises(ModelNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_returns_first_matched_instance_with_recursive_false(self):
        """
        Tests if find method returns matched instance within first found scope
        when recursive is set to False.
        """
        text = """
            <a>Not in scope</a>
            <p class="widget">100</p>
            <span>
                <div>
                    <a>Not a child</a>
                    <p class="widget">10</p>
                </div>
            </span>
            <div>
                <a>Title</a>
                <p class="widget">20</p>
            </div>
        """
        bs = find_body_element(to_bs(text))
        selector = MockModel
        result = selector.find(bs, recursive=False)
        assert result == MockModel(title="Title", price=20)

    def test_find_uses_recursive_search_inside_scope_element_with_recursive_true(self):
        """
        Tests if find method of model uses recursive search inside scope element.
        Recursive parameter only applies to search for scope element. Once scope is found,
        search for fields is always recursive, unless specified otherwise
        with ex. relative selector.
        """
        text = """
            <span>
                <a>Not matching scope</a>
                <p class="widget">10</p>
            </span>
            <span>
                <div>
                    <div>
                        <span>
                            <a>Title</a>
                        </span>
                        <p class="widget">20</p>
                    </div>
                </div>
            </span>
        """
        bs = find_body_element(to_bs(text))
        selector = MockModel
        result = selector.find(bs)
        assert result == MockModel(title="Title", price=20)

    def test_find_uses_recursive_search_inside_scope_element_with_recursive_false(self):
        """
        Tests if find method of model uses recursive search inside scope element.
        Recursive is set to False, so only direct children are match for scope,
        as recursive option applies only to search for scope.
        """
        text = """
            <span>
                <div>
                    <span>
                        <a>Scope not child</a>
                    </span>
                    <p class="widget">10</p>
                </div>
            </span>
            <div>
                <span>
                    <span>
                        <a>Title</a>
                    </span>
                    <p class="widget">20</p>
                </span>
            </div>
        """
        bs = find_body_element(to_bs(text))
        selector = MockModel
        result = selector.find(bs, recursive=False)
        assert result == MockModel(title="Title", price=20)

    @pytest.mark.parametrize(argnames="strict", argvalues=[True, False])
    def test_find_raises_error_when_extraction_of_field_in_scope_failed(
        self, strict: bool
    ):
        """
        Tests if FieldExtractionException is raised when extraction of field in scope
        failed. When scope is found, it does not matter if strict is false or true,
        all exceptions are propagated (selector and operation exceptions) unless
        explicitly suppressed. It ensures model integrity and data consistency.
        """
        text = """
            <span>
                <a>Not matching scope</a>
                <p class="widget">10</p>
            </span>
            <div>
                <a>Title</a>
                <p class="widget">abc</p>
            </div>
            <div>
                <a>Not first</a>
                <p class="widget">20</p>
            </div>
        """
        bs = to_bs(text)
        selector = MockModel

        # first scope price - <p class="widget">abc</p> is found, text is extracted,
        # but conversion to int raises error.
        with pytest.raises(FieldExtractionException, match="price"):
            selector.find(bs, strict=strict)

    @pytest.mark.parametrize(argnames="strict", argvalues=[True, False])
    def test_find_raises_error_when_field_element_not_found_and_operation_failed(
        self, strict: bool
    ):
        """
        Tests if FieldExtractionException is raised when field element is not found
        by selector and subsequent operation failed as it expected Tag.
        If this case is not explicitly handled in selector by ex. Suppress or SkipNone,
        field extraction fails. This works the same way for both strict and non-strict mode
        to ensure integrity.
        """
        text = """
            <span>Hello</span>
            <div>
                <p class="widget">10</p>
            </div>
            <div>
                <a>Not first</a>
                <p class="widget">20</p>
            </div>
        """
        bs = to_bs(text)
        selector = MockModel

        with pytest.raises(FieldExtractionException, match="title"):
            selector.find(bs, strict=strict)

    @pytest.mark.parametrize(argnames="strict", argvalues=[True, False])
    def test_find_allows_empty_attributes_of_model_if_errors_handled_properly(
        self, strict: bool
    ):
        """
        Tests if find method allows empty attributes of model if fields are defined in a way,
        that it handles exceptions properly. MockTextOperation is set to skip None values,
        so if no title is found, it returns None. Strict option applies only to scope search,
        if scope is found, but field extractor returns None, it's not treated as error.
        """
        text = """
            <span>Hello</span>
            <div>
                <p class="widget">10</p>
            </div>
            <div>
                <a>Not first</a>
                <p class="widget">20</p>
            </div>
        """
        bs = to_bs(text)
        selector = MockAllowEmptyTitle
        result = selector.find(bs, strict=strict)
        assert result == MockAllowEmptyTitle(title=None, price=10)

    def test_find_all_returns_list_of_models_from_all_found_scopes(self):
        """
        Tests if find_all method returns a list of models extracted from all found scopes.
        """
        text = """
            <a>Not in scope</a>
            <p class="widget">100</p>
            <span>
                <div>
                    <p>Extra information</p>
                    <a>Title</a>
                    <p class="widget">10</p>
                    <a>Not first anchor element</a>
                </div>
            </span>
            <div>
                <a>Title2</a>
                <p class="widget">20</p>
            </div>
            <span>
                <a>Not in scope</a>
                <p class="widget">20</p>
            </span>
            <div>
                <span>
                    <p>Extra information</p>
                    <span><a>Title3</a></span>
                    <p class="widget">30</p>
                </span>
            </div>
        """
        bs = to_bs(text)
        selector = MockModel
        result = selector.find_all(bs)
        assert result == [
            MockModel(title="Title", price=10),
            MockModel(title="Title2", price=20),
            MockModel(title="Title3", price=30),
        ]

    def test_find_all_returns_empty_list_if_no_scope_was_found(self):
        """
        Tests if find_all method returns an empty list
        if no scope was found in provided bs object.
        """
        text = """
            <a>Not in scope</a>
            <p class="widget">10</p>
            <span>
                <a>Not in scope</a>
                <p class="widget">10</p>
            </span>
        """
        bs = to_bs(text)
        selector = MockModel
        result = selector.find_all(bs)
        assert result == []

    def test_find_all_returns_empty_list_if_no_scope_was_found_with_recursive_false(
        self,
    ):
        """
        Tests if find_all method returns an empty list
        if no scope was found in provided bs object and recursive is set to False.
        """
        text = """
            <a>Not in scope</a>
            <p class="widget">10</p>
            <span>
                <a>Not in scope</a>
                <p class="widget">10</p>
            </span>
            <span>
                <div>
                    <a>Scope not child</a>
                    <p class="widget">10</p>
                </div>
            </span>
        """
        bs = find_body_element(to_bs(text))
        selector = MockModel
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_list_of_models_from_all_found_scopes_with_recursive_false(
        self,
    ):
        """
        Tests if find_all method returns a list of models extracted from all found scopes
        when recursive is set to False. Recursive option applies only to scope search,
        so only models from scope elements, that are children of body element are extracted.
        """
        text = """
            <a>Not in scope</a>
            <p class="widget">100</p>
            <span>
                <div>
                    <a>Scope not child</a>
                    <p class="widget">10</p>
                </div>
            </span>
            <div>
                <p>Extra information</p>
                <a>Title</a>
                <p class="widget">10</p>
                <a>Not first anchor element</a>
            </div>
            <span>
                <a>Not in scope</a>
                <p class="widget">20</p>
            </span>
            <div>
                <span>
                    <p>Extra information</p>
                    <span><a>Title2</a></span>
                    <p class="widget">20</p>
                </span>
            </div>
        """
        bs = find_body_element(to_bs(text))
        selector = MockModel
        result = selector.find_all(bs, recursive=False)
        assert result == [
            MockModel(title="Title", price=10),
            MockModel(title="Title2", price=20),
        ]

    def test_find_all_returns_first_x_models_with_limit(self):
        """
        Tests if find_all method returns first x models from found scopes when
        limit is specified.
        """
        text = """
            <span>
                <a>Not in scope</a>
                <p class="widget">10</p>
            </span>
            <span>
                <div>
                    <span><a>Title</a><span>
                    <p class="widget">10</p>
                </div>
            </span>
            <div>
                <a>Title2</a>
                <p>Extra information</p>
                <p class="widget">20</p>
                <a>Not first anchor element</a>
            </div>
            <div>
                <a>Title3</a>
                <p class="widget">30</p>
            </div>
        """
        bs = to_bs(text)
        selector = MockModel
        result = selector.find_all(bs, limit=2)
        assert result == [
            MockModel(title="Title", price=10),
            MockModel(title="Title2", price=20),
        ]

    def test_find_all_returns_first_x_models_with_limit_and_recursive_false(self):
        """
        Tests if find_all method returns first x models from found scopes when
        limit is specified and recursive is set to False.
        """
        text = """
            <span>
                <a>Not in scope</a>
                <p class="widget">10</p>
            </span>
            <span>
                <div>
                    <a>Scope not child</a>
                    <p class="widget">10</p>
                </div>
            </span>
            <div>
                <span><a>Title</a></span>
                <p class="widget">10</p>
            </div>
            <div>
                <div>
                    <a>Title2</a>
                    <p>Extra information</p>
                    <p class="widget">20</p>
                </div>
            </div>
            <div>
                <a>Title3</a>
                <p class="widget">30</p>
            </div>
        """
        bs = find_body_element(to_bs(text))
        selector = MockModel
        result = selector.find_all(bs, recursive=False, limit=2)
        assert result == [
            MockModel(title="Title", price=10),
            MockModel(title="Title2", price=20),
        ]

    def test_find_all_raises_error_if_any_model_extraction_failed(self):
        """
        Tests if FieldExtractionException is raised when extraction of any model failed
        during find_all method.
        """
        text = """
            <div>
                <a>Title</a>
                <p class="widget">10</p>
            </div>
            <div>
                <a>Title2</a>
                <p class="widget">abc</p>
            </div>
        """
        bs = to_bs(text)
        selector = MockModel

        with pytest.raises(FieldExtractionException, match="price"):
            selector.find_all(bs)

    def test_find_all_allows_empty_attribute_if_handled_properly(self):
        """
        Tests if find_all method allows empty attributes of model if fields are defined
        in a way, that it handles exceptions properly.
        """
        text = """
            <div>
                <a>Title</a>
                <p class="widget">10</p>
            </div>
            <div>
                <p>Extra information</a>
                <p class="widget">20</p>
            </div>
        """
        bs = to_bs(text)
        selector = MockAllowEmptyTitle
        result = selector.find_all(bs)
        assert result == [
            MockAllowEmptyTitle(title="Title", price=10),
            MockAllowEmptyTitle(title=None, price=20),
        ]

    @pytest.mark.parametrize(
        "models",
        [
            (MockModel(title="Title", price=10), MockModel(title="Title", price=10)),
        ],
    )
    def test_two_models_are_equal(self, models):
        """
        Tests if two models are equal when they have the same attributes corresponding
        to fields and they are of the same type.
        """
        assert (models[0] == models[1]) is True

    @pytest.mark.parametrize(
        "models",
        [
            # both attributes are different
            (MockModel(title="Title", price=10), MockModel(title="Title2", price=20)),
            # one attribute is different
            (MockModel(title="Title", price=10), MockModel(title="Title", price=20)),
            # not BaseMode instance
            (MockModel(title="Title", price=10), MockLinkSelector()),
            # attributes the same, but different model type
            (
                MockModel(title="Title", price=10),
                MockNotEqualModel(title="Title", price=10),
            ),
        ],
    )
    def test_two_models_are_not_equal(self, models):
        """
        Tests if two models not equal when they have different attributes corresponding
        to fields or they are of different type.
        """
        assert (models[0] == models[1]) is False


@pytest.mark.integration
@pytest.mark.model
class TestBaseModelIntegration:
    """
    Class with integration tests for BaseModel component.
    It tests its behavior with various field and operation wrappers.
    """

    @pytest.mark.parametrize(argnames="strict", argvalues=[True, False])
    def test_raises_error_if_required_field_is_none(self, strict: bool):
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
        bs = to_bs(text)
        selector = MockModel

        with pytest.raises(FieldExtractionException, match="title"):
            selector.find(bs, strict=strict)

    def test_returns_default_if_extracted_field_is_none(self):
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
        bs = to_bs(text)
        selector = MockModel
        result = selector.find(bs)
        assert result == MockModel(title="DefaultTitle", price=10)

    def test_default_propagates_errors_of_selector(self):
        """
        Tests if Default propagates errors of selector, so if any exception was raised
        by selector, it raises FieldExtractionException. Default is only applied
        if selector did not raise any exception and returned None. In this case None is not
        handled in MockTextOperation, so it raises exception.
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
        bs = to_bs(text)
        selector = MockModel

        with pytest.raises(FieldExtractionException, match="title"):
            selector.find(bs)

    def test_default_does_not_overwrite_field_value_if_found(self):
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
        bs = to_bs(text)
        selector = MockModel
        result = selector.find(bs)
        assert result == MockModel(title="Title", price=10)

    def test_failing_operation_is_cancelled_with_suppress_and_none_returned(self):
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
        bs = to_bs(text)
        selector = MockModel
        result = selector.find(bs)
        assert result == MockModel(title="Title", price=None)

    def test_operation_is_cancelled_and_field_has_default(self):
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
        bs = to_bs(text)
        selector = MockModel
        result = selector.find(bs)
        assert result == MockModel(title="Title", price=0)

    def test_skip_none_is_applied_to_skip_operation(self):
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
        bs = to_bs(text)
        selector = MockModel
        result = selector.find(bs)
        assert result == MockModel(title="Title", price=None)

    def test_skip_none_propagates_value_if_not_none(self):
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
        bs = to_bs(text)
        selector = MockModel
        result = selector.find(bs)
        assert result == MockModel(title="Title", price=10)

    def test_all_returns_multiple_elements_in_list_for_field(self):
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
        bs = to_bs(text)
        selector = MockModel
        result = selector.find(bs)
        assert result == MockModel(title="Title", price=[10, 20, 30])

    def test_all_returns_empty_list_if_nothing_found_for_field(self):
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
        bs = to_bs(text)
        selector = MockModel
        result = selector.find(bs)
        assert result == MockModel(title="Title", price=[])

    def test_field_can_be_another_model_class(self):
        """
        Tests if field can be another model class, that inherits from BaseModel.
        It is allowed, as model is TagSearcher and can be used as field.
        """

        class MockInfoModel(BaseModel):
            __scope__ = MockDivSelector()

            title = TITLE_SELECTOR
            author = MockClassMenuSelector() | MockTextOperation()

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            info = MockInfoModel
            price = PRICE_SELECTOR

        text = """
            <div>
                <div>
                    <a>Title</a>
                    <p class="menu">Author</p>
                </div>
                <p class="widget">10</p>
            </div>
        """
        bs = to_bs(text)
        selector = MockModel
        result = selector.find(bs)
        assert result == MockModel(
            info=MockInfoModel(title="Title", author="Author"), price=10
        )

    def test_model_migration_to_other_class(self):
        """
        Tests if model can be migrated to other class, migrate calls constructor
        of provided class with all fields as keyword arguments and if successful,
        returns instance of provided class.
        """
        model = MockModel(title="Title", price=10)
        migrated = model.migrate(MockMigrationModel)

        assert isinstance(migrated, MockMigrationModel)
        assert migrated.title == "Title"
        assert migrated.price == 10

    def test_migrate_passes_keyword_arguments_to_model_init(self):
        """
        Tests if migrate method passes keyword arguments to model init method
        additionally to fields of model instance. It allows to pass additional
        data to model, that is not present in original model.
        """
        model = MockModel(title="Title", price=10)
        migrated = model.migrate(MockMigrationModel, hello="World", number=42)

        assert isinstance(migrated, MockMigrationModel)

        assert migrated.title == "Title"
        assert migrated.price == 10
        assert getattr(migrated, "hello", None) == "World"
        assert getattr(migrated, "number", None) == 42

    def test_migrate_propagates_errors_from_model_init(self):
        """
        Tests if migrate method propagates errors from model init method.
        In this case, MockMigrationModel raises ValueError.
        """
        model = MockModel(title="Title", price=10)

        with pytest.raises(ValueError):
            model.migrate(MockMigrationModel, hello="World", error="Error")

    @pytest.mark.integration
    def test_migration_to_pydantic_model(self):
        """
        Tests if model can be migrated to Pydantic model. If validation passes,
        Pydantic model is returned.
        """
        model = MockModel(title="Title", price=10)
        migrated = model.migrate(MockPydanticBook)
        assert isinstance(migrated, MockPydanticBook)

    @pytest.mark.integration
    def test_migration_to_pydantic_model_raises_error(self):
        """
        Tests if migration to Pydantic model raises error if validation fails.
        In this case, title is integer, but Pydantic model expects string.
        """
        model = MockModel(title=123, price=10)

        with pytest.raises(pydantic.ValidationError):
            model.migrate(MockPydanticBook)

    @pytest.mark.integration
    def test_model_migration_to_sqlalchemy_model(self):
        """Tests migration of model to SQLAlchemy model."""
        model = MockModel(title="Title", price=10)
        migrated = model.migrate(MockSABook)
        assert isinstance(migrated, MockSABook)

    @pytest.mark.integration
    def test_works_with_soupsavvy_operations_as_fields(self):
        """
        Tests if model works with soupsavvy operations as fields.
        Operations are operation-searcher mixins and can be used as fields
        to perform operation directly on scope element.
        """

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            title = TITLE_SELECTOR
            link = Href()
            id_ = Operation(lambda x: x.get("id"))
            name = Operation(lambda x: x.get("name")) | Operation(lambda x: x.upper())
            text = Text(strip=True, separator="--")

        text = """
            <div id="book1", href="www.book.com" name="Joe">
                <a>Title</a>
                <p>Hello</p>
            </div>
        """
        bs = to_bs(text)
        selector = MockModel
        result = selector.find(bs)
        assert result == MockModel(
            title="Title",
            link="www.book.com",
            id_="book1",
            name="JOE",
            text="Title--Hello",
        )
