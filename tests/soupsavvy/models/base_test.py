"""
Module with unit tests for BaseModel component,
which is parent class of all user-defined models.
"""

from dataclasses import dataclass

import pydantic
import pytest
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, relationship

import soupsavvy.exceptions as exc
from soupsavvy.models import All, Default, Required
from soupsavvy.models.base import BaseModel, Field, MigrationSchema, post
from soupsavvy.operations import (
    Break,
    Continue,
    Href,
    IfElse,
    Operation,
    SkipNone,
    Suppress,
    Text,
)
from tests.soupsavvy.conftest import (
    MockClassMenuSelector,
    MockClassWidgetSelector,
    MockDivSelector,
    MockIntOperation,
    MockLinkSelector,
    MockPlus10Operation,
    MockTextOperation,
    find_body_element,
    strip,
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


class MockTitle(BaseModel):
    """Mock model for testing migration with model as field."""

    __scope__ = MockLinkSelector()

    name = MockLinkSelector()


class MockAddress(BaseModel):
    """
    Mock model for testing migration with model as field.
    Used as redundant extra key in migration to test if it's ignored.
    """

    __scope__ = MockLinkSelector()

    street = MockLinkSelector()


class MockModelTitleField(BaseModel):
    """
    Mock model with field, which is instance of another model
    to test migration in such cases.
    """

    __scope__ = MockDivSelector()

    title = MockTitle
    price = PRICE_SELECTOR


class MockFrozenModel(BaseModel):
    """
    Mock model for testing frozen model instances.
    Setting attribute on them or computing hash.
    """

    __scope__ = MockDivSelector()
    __frozen__ = True

    title = TITLE_SELECTOR
    price = PRICE_SELECTOR


class MockMigrationTitle:
    """
    Mock class for testing migration of MockTitle model.
    This is target model, that instance of MockTitle, which is a field of model
    that is being migrated, should be migrated to.
    """

    def __init__(self, name, top: bool = True) -> None:
        """
        Initializes MockMigrationTitle with name and top attributes.
        Name is required, as it is field of MockTitle model.
        Top is optional, and is used for testing more complex migrations
        with additional attributes passed to model init.
        """
        self.name = name
        self.top = top

    def __eq__(self, other) -> bool:
        return self.name == other.name and self.top == other.top


class MockMigrationName:
    """
    Mock class for testing migration of MockName model, which is a field of model,
    that is used as field of migrated model. Tests recursive behavior of migrate method.
    """

    def __init__(self, name: str) -> None:
        """Initializes MockMigrationName with name attribute."""
        self.name = name

    def __eq__(self, other) -> bool:
        return self.name == other.name


class MockNotEqualModel(BaseModel):
    """
    Mock model for testing model equality,
    if two instances of models are of different type,
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

        with pytest.raises(exc.ScopeNotDefinedException):

            class MockModel(BaseModel):
                title = MockLinkSelector() | MockTextOperation()

    def test_raises_error_when_creating_model_class_without_fields(self):
        """
        Tests if FieldsNotDefinedException is raised
        when fields are not defined in model.
        At least one field must be defined in model to make sense and work properly.
        Fields is class attribute with value of instance `TagSearcher`.
        """

        with pytest.raises(exc.FieldsNotDefinedException):

            class MockModel(BaseModel):
                __scope__ = MockDivSelector()

    def test_raises_error_on_init_if_field_missing_in_kwargs(self):
        """
        Tests if MissingFieldsException is raised when field is missing in kwargs
        during model initialization. All fields must be provided,
        only as keyword arguments. This is not usual way of creating models,
        which should be done with find methods.
        """

        with pytest.raises(exc.MissingFieldsException):
            MockModel(title="Title")

    def test_raises_error_on_init_if_unknown_field(self):
        """
        Tests if UnknownModelFieldException is raised when unknown field is passed
        to model constructor. Only fields defined in model class are allowed.
        """

        with pytest.raises(exc.UnknownModelFieldException):
            MockModel(title="Title", price=10, name="Name")

    def test_raises_error_when_scope_is_not_soup_selector(self):
        """
        Tests if NotSoupSelectorException is raised on creating class
        when __scope__ is not instance of SoupSelector.
        """

        with pytest.raises(exc.NotSoupSelectorException):

            class MockModel(BaseModel):
                __scope__ = MockTextOperation()  # type: ignore

                title = TITLE_SELECTOR

    def test_class_attribute_fields_is_defined_correctly(self):
        """
        Tests if class attribute fields is defined correctly in model.
        It should be dictionary with field names as keys
        and provided selectors wrapped in Field with default parameters as values.
        """
        assert MockModel.fields == {
            "title": Field(TITLE_SELECTOR),
            "price": Field(PRICE_SELECTOR),
        }

    def test_class_attribute_fields_contains_inherited_and_model_fields(self):
        """
        Tests if class attribute fields contains both inherited fields
        from base class and fields defined in model.
        Inheriting fields behavior is default,
        but can be overridden by setting __inherit_fields__ to False.
        """
        name_selector = MockClassWidgetSelector() | MockTextOperation()

        class ChildModel(MockModel):
            name = name_selector

        assert ChildModel.fields == {
            "title": Field(TITLE_SELECTOR),
            "price": Field(PRICE_SELECTOR),
            "name": Field(name_selector),
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

        assert ChildModel.fields == {"name": Field(name_selector)}

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

    def test_custom_post_process_methods_are_applied(self):
        """
        Tests if custom post-process methods are applied to fields of model instance
        in initialization. It allows to modify field values after extraction.
        Every method, that is decorated with post, with valid field name
        is considered post-process method.
        """

        class ChildModel(MockModel):

            @post("title")
            def process_title(self, value: str) -> str:
                return value + "!"

            @post("price")
            def process_price(self, value: int) -> int:
                return value + 10

        model = ChildModel(title="Title", price=10)

        assert model.title == "Title!"
        assert model.price == 20
        assert model.attributes == {"title": "Title!", "price": 20}

    def test_custom_post_process_methods_are_applied_before_post_init(self):
        """
        Tests if custom post-process methods are applied to fields of model instance
        before custom __post_init__ method.
        """

        class ChildModel(MockModel):

            @post("title")
            def process_title(self, value: str) -> str:
                return value + "!"

            @post("price")
            def process_price(self, value: int) -> int:
                return value + 10

            def __post_init__(self) -> None:
                self.price = self.price + len(self.title)  # type: ignore

        model = ChildModel(title="Title", price=10)

        assert model.title == "Title!"
        assert model.price == 26

    def test_processors_of_the_same_field_are_overwritten(self):
        """
        Tests if processors of the same field are overwritten by the last one.
        Only last defined processor is applied to the field.
        """

        class ChildModel(MockModel):

            @post("title")
            def process_title(self, value: str) -> str:
                return value + "!"

            @post("title")
            def process_title2(self, value: str) -> str:
                return value + "!?"

        model = ChildModel(title="Title", price=10)

        assert model.title == "Title!?"
        assert model.price == 10

    def test_method_decorated_with_post_with_invalid_field_name_is_ignored(self):
        """
        Tests if method decorated with post with argument, that is not a field name
        is ignored and not applied to the model instance. The same way,
        any method not decorated with post is ignored.
        """

        class ChildModel(MockModel):

            @post("random")
            def process_title(self, value: str) -> str:
                return value + "!"

            def process_price(self, value: int) -> int:
                return value + 10

        model = ChildModel(title="Title", price=10)

        assert model.title == "Title"
        assert model.price == 10

    def test_custom_post_process_methods_are_inherited_and_overridden(self):
        """
        Tests if custom post-process methods are inherited from base class
        and can be overridden in child class.
        """

        class ChildModel(MockModel):

            @post("title")
            def process_title(self, value: str) -> str:
                return value + "!"

            @post("price")
            def process_price(self, value: int) -> int:
                return value + 10

        class GrandChildModel(ChildModel):

            @post("title")
            def process_title(self, value: str) -> str:
                return value + "!!"

        model = GrandChildModel(title="Title", price=10)

        assert model.title == "Title!!"
        assert model.price == 20

    def test_errors_in_post_process_methods_are_propagated(self):
        """
        Tests if any error raised in post-process method is propagated and not handled.
        """

        class ChildModel(MockModel):

            @post("title")
            def process_title(self, value: str) -> str:
                raise ValueError("Error")

        with pytest.raises(ValueError):
            ChildModel(title="Title", price=10)

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

    def test_model_with_model_as_field_has_correct_string_representation(self):
        """
        Tests if model with another model as field has correct string representation.
        It should use repr of instance of this model.
        """
        model = MockModelTitleField(title=MockTitle(name="Title"), price=10)
        expected = (
            f"MockModelTitleField(title={repr(model.title)}, price={repr(model.price)})"
        )
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

        with pytest.raises(exc.ModelNotFoundException):
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

        with pytest.raises(exc.ModelNotFoundException):
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
        Recursive parameter only applies to search for scope element.
        Once scope is found, search for fields is always recursive,
        unless specified otherwise with ex. relative selector.
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
        with pytest.raises(exc.FieldExtractionException, match="price"):
            selector.find(bs, strict=strict)

    @pytest.mark.parametrize(argnames="strict", argvalues=[True, False])
    def test_find_raises_error_when_field_element_not_found_and_operation_failed(
        self, strict: bool
    ):
        """
        Tests if FieldExtractionException is raised when field element is not found
        by selector and subsequent operation failed as it expected Tag.
        If this case is not explicitly handled in selector by ex. Suppress or SkipNone,
        field extraction fails. This works the same way for both strict
        and non-strict mode to ensure integrity.
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

        with pytest.raises(exc.FieldExtractionException, match="title"):
            selector.find(bs, strict=strict)

    @pytest.mark.parametrize(argnames="strict", argvalues=[True, False])
    def test_find_allows_empty_attributes_of_model_if_errors_handled_properly(
        self, strict: bool
    ):
        """
        Tests if find method allows empty attributes of model
        if fields are defined in a way, that it handles exceptions properly.
        MockTextOperation is set to skip None values, so if no title is found,
        it returns None. Strict option applies only to scope search,
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
        Tests if find_all method returns a list of models extracted
        from all found scopes.
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
        Tests if find_all method returns a list of models
        extracted from all found scopes when recursive is set to False.
        Recursive option applies only to scope search, so only models from
        scope elements, that are children of body element are extracted.
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

        with pytest.raises(exc.FieldExtractionException, match="price"):
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
        assert getattr(migrated, "hello") == "World"
        assert getattr(migrated, "number") == 42

    def test_copy_is_equivalent_to_migrating_model_to_its_class(self):
        """Tests if copy method is equivalent to migrating model to its class."""
        model = MockModel(title="Title", price=10)
        migrated = model.migrate(MockModel)
        copied = model.copy()

        assert isinstance(migrated, MockModel)
        assert migrated == copied == model
        assert migrated.title == "Title"
        assert migrated.price == 10

    def test_copy_creates_deep_copy_of_the_model(self):
        """
        Tests if copy method creates deep copy of the model instance, by creating
        new instances of fields.
        """
        title = MockTitle(name="Title")
        model = MockModelTitleField(title=title, price=10)
        copied = model.copy()

        assert isinstance(copied, MockModelTitleField)
        assert copied.title is not title
        assert copied.title == MockTitle(name="Title")
        assert copied == model

    def test_migrate_propagates_errors_from_model_init(self):
        """
        Tests if migrate method propagates errors from model init method.
        In this case, MockMigrationModel raises ValueError.
        """
        model = MockModel(title="Title", price=10)

        with pytest.raises(ValueError):
            model.migrate(MockMigrationModel, hello="World", error="Error")

    def test_migrate_raises_error_if_model_param_in_keyword_params(self):
        """
        Tests if migrate method raises TypeError if one of keyword arguments passed
        has the same name as one of the field model attributes.
        It results in `multiple values for keyword argument`.
        """
        model = MockModelTitleField(title=MockTitle(name="Title"), price=10)

        with pytest.raises(TypeError):
            model.migrate(MockMigrationModel, hello="World", price=20)

    def test_migrate_raises_error_if_field_model_param_in_its_migration_schema(self):
        """
        Tests if migrate method raises TypeError
        if MigrationSchema in field model mapping contains param of the same name
        as one of the field model attributes.
        It results in `multiple values for keyword argument`.
        """
        model = MockModelTitleField(title=MockTitle(name="Title"), price=10)

        with pytest.raises(TypeError):
            model.migrate(
                MockMigrationModel,
                mapping={
                    MockTitle: MigrationSchema(
                        MockMigrationTitle, params={"top": False, "name": "Title2"}
                    )
                },
            )

    def test_field_of_type_model_is_migrated_as_itself_by_default(self):
        """
        Tests if field, which is another model, is migrated as itself by default.
        Field in target model is equal to field in source model,
        but they are different objects.
        """
        title = MockTitle(name="Title")
        model = MockModelTitleField(title=title, price=10)
        migrated = model.migrate(MockMigrationModel)

        assert isinstance(migrated, MockMigrationModel)
        assert migrated.title is not title
        assert migrated.title == MockTitle(name="Title") == title
        assert migrated.price == 10

    def test_field_of_type_model_is_migrated_as_itself_when_missing_from_mapping(self):
        """
        Tests if field, which is another model, is migrated as itself when mapping
        is provided, but it does not contain field class as key.
        Field in target model is equal to field in source model,
        but they are different objects.
        """
        title = MockTitle(name="Title")
        model = MockModelTitleField(title=title, price=10)
        migrated = model.migrate(
            MockMigrationModel,
            mapping={MockAddress: MockMigrationModel},
        )

        assert isinstance(migrated, MockMigrationModel)
        assert migrated.title is not title
        assert migrated.title == MockTitle(name="Title") == title
        assert migrated.price == 10

    def test_field_of_type_model_is_migrated_as_target_model_if_included_in_mapping(
        self,
    ):
        """
        Tests if field, which is another model, is migrated as target model,
        when mapping is provided and it contains field class as key.
        Testing case, where value of mapping is class of the model to migrate to.
        """

        model = MockModelTitleField(title=MockTitle(name="Title"), price=10)
        migrated = model.migrate(
            MockMigrationModel,
            mapping={MockTitle: MockMigrationTitle, MockAddress: MockMigrationModel},
        )

        assert isinstance(migrated, MockMigrationModel)
        assert migrated.title == MockMigrationTitle(name="Title", top=True)
        assert migrated.price == 10

    def test_keyword_parameters_are_not_passes_to_field_model_inits_in_migration(
        self,
    ):
        """
        Tests if keyword parameters passed to migrate method
        are used only for high level model init, not for any field model init.
        When there is need for specifying additional parameters for field model,
        it should be done in mapping via MigrationSchema.
        """

        model = MockModelTitleField(title=MockTitle(name="Title"), price=10)
        migrated = model.migrate(
            MockMigrationModel,
            mapping={MockTitle: MockMigrationTitle, MockAddress: MockMigrationModel},
            hello="World",
        )

        assert isinstance(migrated, MockMigrationModel)
        assert migrated.title == MockMigrationTitle(name="Title", top=True)
        assert migrated.price == 10
        assert getattr(migrated, "hello") == "World"
        assert not hasattr(migrated.title, "hello")

    def test_field_of_type_model_is_migrated_with_migration_schema(self):
        """
        Tests if field, which is another model, is migrated with MigrationSchema
        provided in mapping. MigrationSchema allows to specify class to migrate to
        and additional parameters for its constructor.
        """
        model = MockModelTitleField(title=MockTitle(name="Title"), price=10)
        migrated = model.migrate(
            MockMigrationModel,
            mapping={
                MockTitle: MigrationSchema(MockMigrationTitle, params={"top": False})
            },
        )

        assert isinstance(migrated, MockMigrationModel)
        # optional parameter `top` was passed to MockMigrationTitle constructor
        assert migrated.title == MockMigrationTitle(name="Title", top=False)
        assert migrated.price == 10

    def test_all_model_fields_are_migrated_recursively_if_they_are_of_type_model(self):
        """
        Tests if all model fields are migrated recursively if they are of type model.
        When field is another model, all its fields of type model are migrated as well.
        """

        class MockName(BaseModel):
            __scope__ = MockLinkSelector()

            name = MockLinkSelector()

        class MockTitle(BaseModel):
            __scope__ = MockLinkSelector()

            name = MockName

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            title = MockTitle
            price = PRICE_SELECTOR

        model = MockModel(title=MockTitle(name=MockName(name="Title")), price=10)
        migrated = model.migrate(
            MockMigrationModel,
            mapping={
                MockTitle: MigrationSchema(MockMigrationTitle, params={"top": False}),
                MockName: MockMigrationName,
                MockAddress: MockMigrationModel,
            },
        )

        assert isinstance(migrated, MockMigrationModel)
        assert migrated.title == MockMigrationTitle(
            name=MockMigrationName(name="Title"), top=False
        )
        assert migrated.price == 10

    def test_migrate_model_missing_from_mapping_but_its_field_is_mapped(self):
        """
        Tests if in case of model class missing from mapping, but its field model class
        existing in mapping, field is migrated as specified in mapping.
        """

        class MockName(BaseModel):
            __scope__ = MockLinkSelector()

            name = MockLinkSelector()

        class MockTitle(BaseModel):
            __scope__ = MockLinkSelector()

            name = MockName

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            title = MockTitle
            price = PRICE_SELECTOR

        title = MockTitle(name=MockName(name="Title"))
        model = MockModel(title=title, price=10)
        migrated = model.migrate(
            MockMigrationModel,
            mapping={
                MockName: MockMigrationName,
                MockAddress: MockMigrationModel,
            },
        )

        assert isinstance(migrated, MockMigrationModel)
        assert migrated.title is not title
        assert migrated.title == MockTitle(name=MockMigrationName(name="Title"))
        assert migrated.price == 10

    def test_not_frozen_model_instance_attributes_can_be_modified(self):
        """
        Tests if model instance (which is not frozen if not defined otherwise)
        attributes can be modified, by setting new value to one of its fields.
        """
        model = MockModel(title="Title", price=10)
        model.title = "Title2"  # type: ignore
        assert model.title == "Title2"
        assert model.price == 10

    def test_frozen_model_instance_attributes_cannot_be_modified(self):
        """
        Tests if frozen model instance cannot be modified, by setting new value
        to one of its fields. It raises FrozenInstanceError.
        """
        model = MockFrozenModel(title="Title", price=10)

        with pytest.raises(exc.FrozenModelException):
            model.title = "Title2"  # type: ignore

    def test_frozen_model_instance_can_be_modified_during_initialization(self):
        """
        Tests if frozen model instance can be modified during initialization,
        post init is part of initialization exposed to user in which model attributes
        can freely be modified. It is not restricted by frozen attribute.
        """

        class MockFrozenModel(BaseModel):
            __scope__ = MockDivSelector()
            __frozen__ = True

            title = TITLE_SELECTOR
            price = PRICE_SELECTOR

            def __post_init__(self) -> None:
                self.title = "Title2"

        MockFrozenModel(title="Title", price=10)

    @pytest.mark.parametrize(argnames="frozen", argvalues=[True, False])
    def test_no_fields_attributes_cannot_be_set(self, frozen: bool):
        """
        Tests if attributes, that are not defined as fields in model, cannot be set
        on model instance. It raises AttributeError, as it is not allowed to set
        arbitrary attributes on model instance. This behavior is independent of frozen
        attribute and takes precedence over it.
        """

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()
            __frozen__ = frozen

            title = TITLE_SELECTOR
            price = PRICE_SELECTOR

        model = MockModel(title="Title", price=10)

        with pytest.raises(AttributeError):
            model.name = 20  # type: ignore

    def test_hash_raises_error_if_model_not_frozen(self):
        """
        Tests if calling hash on model instance raises TypeError
        if model is not frozen.
        """
        model = MockModel(title="Title", price=10)

        with pytest.raises(TypeError):
            hash(model)

    def test_hash_raises_error_if_field_model_not_frozen(self):
        """
        Tests if calling hash on model instance raises TypeError if any of field models
        or their nested field models are not frozen.
        """

        class MockModelTitleField(BaseModel):
            __scope__ = MockDivSelector()
            __frozen__ = True

            title = MockTitle
            price = PRICE_SELECTOR

        model = MockModelTitleField(title=MockTitle(name="Title"), price=10)

        with pytest.raises(TypeError):
            hash(model)

    def test_hash_equality_on_models_with_model_field(self):
        """
        Tests if has is computed correctly for different instances of the model
        with another model as field.
        """

        class MockTitle(BaseModel):
            __scope__ = MockLinkSelector()
            __frozen__ = True

            name = MockLinkSelector()

        class MockModelTitleField(BaseModel):
            __scope__ = MockDivSelector()
            __frozen__ = True

            title = MockTitle
            price = PRICE_SELECTOR

        model1 = MockModelTitleField(title=MockTitle(name="Title"), price=10)
        model2 = MockModelTitleField(title=MockTitle(name="Title"), price=10)
        model3 = MockModelTitleField(title=MockTitle(name="Title2"), price=10)

        assert hash(model1) == hash(model2)
        assert hash(model1) != hash(model3)

    def test_hash_equality_of_different_instances(self):
        """Tests if has is computed correctly for different instances of the model."""

        class MockNotEqualFrozenModel(BaseModel):
            __scope__ = MockDivSelector()
            __frozen__ = True

            title = TITLE_SELECTOR
            price = PRICE_SELECTOR

        model1 = MockFrozenModel(title="Title", price=10)
        model2 = MockFrozenModel(title="Title", price=10)
        model3 = MockFrozenModel(title="Title2", price=10)
        model4 = MockNotEqualFrozenModel(title="Title", price=10)

        assert hash(model1) == hash(model2)
        assert hash(model1) != hash(model3)
        assert hash(model1) != hash(model4)

    def test_frozen_model_instances_can_be_keys_in_dict(self):
        """
        Tests if frozen model instances can be used as keys in dictionary.
        They are hashable, which makes it possible.
        """
        lookup = {
            MockFrozenModel(title="Title", price=10): 1,
            MockFrozenModel(title="Title", price=20): 2,
        }

        assert lookup[MockFrozenModel(title="Title", price=10)] == 1
        assert lookup[MockFrozenModel(title="Title", price=20)] == 2


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

        with pytest.raises(exc.FieldExtractionException, match="title"):
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
        bs = to_bs(text)
        selector = MockModel

        with pytest.raises(exc.FieldExtractionException, match="title"):
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

    def test_ifelse_operation_evaluates_condition_properly(self):
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
        bs = to_bs(text)
        selector = MockModel
        result = selector.find(bs)
        assert result == MockModel(title="TITLE", price=30)

    def test_ifelse_operation_conditionally_breaks_operation_pipeline(self):
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
        bs = to_bs(text)
        selector = MockModel
        result = selector.find(bs)
        assert result == MockModel(title="Title", price=5)

    def test_ifelse_operation_conditionally_skip_operation(self):
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
        bs = to_bs(text)
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

    def test_find_methods_work_properly_on_field(self):
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
        bs = to_bs(text)
        selector = MockModel
        result = selector.find(bs)
        assert result == MockModel(title="Title", price=10)

        result = selector.find_all(bs)
        assert result == [
            MockModel(title="Title", price=10),
            MockModel(title="Title2", price=20),
        ]


@pytest.mark.selector
class TestField:
    """
    Unit tests suite for Field class, it's a wrapper of selector to which it delegates.
    Runs full set of tests on find methods with use of simple selector to make sure
    it delegates correctly with passing all parameters.
    Field is supposed to be used with BaseModel, so it's tested in integration tests
    as well, but, it's worth to have unit tests as it can be used independently.
    """

    def test_find_returns_first_tag_matching_selector(self):
        """Tests if find method returns first tag matching selector."""
        text = """
            <div href="github"></div>
            <a class="widget">1</a>
            <a><p>2</p></a>
            <span>
                <a>3</a>
            </span>
        """
        bs = to_bs(text)
        selector = Field(MockLinkSelector())
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<a class="widget">1</a>""")

    def test_find_returns_none_if_no_match_and_strict_false(self):
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
        bs = to_bs(text)
        selector = Field(MockLinkSelector())
        result = selector.find(bs)
        assert result is None

    def test_find_raises_exception_if_no_match_and_strict_true(self):
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
        bs = to_bs(text)
        selector = Field(MockLinkSelector())

        with pytest.raises(exc.TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_all_returns_empty_list_when_no_match(self):
        """Tests if find returns an empty list if no element matches the selector."""
        text = """
            <div href="github"></div>
            <span class="widget"></span>
            <div><p>Hello</p></div>
            <span>
                <div>Hello</div>
            </span>
        """
        bs = to_bs(text)
        selector = Field(MockLinkSelector())
        result = selector.find_all(bs)
        assert result == []

    def test_find_all_returns_all_matching_elements(self):
        """Tests if find_all returns a list of all matching elements."""
        text = """
            <div href="github"></div>
            <a class="widget">1</a>
            <a><p>2</p></a>
            <span>
                <a>3</a>
            </span>
        """
        bs = to_bs(text)
        selector = Field(MockLinkSelector())
        result = selector.find_all(bs)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="widget">1</a>"""),
            strip("""<a><p>2</p></a>"""),
            strip("""<a>3</a>"""),
        ]

    def test_find_returns_first_matching_child_if_recursive_false(self):
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
        bs = find_body_element(to_bs(text))
        selector = Field(MockLinkSelector())
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<a href="github">1</a>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
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
        bs = find_body_element(to_bs(text))
        selector = Field(MockLinkSelector())
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
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
        bs = find_body_element(to_bs(text))
        selector = Field(MockLinkSelector())

        with pytest.raises(exc.TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
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
        bs = find_body_element(to_bs(text))
        selector = Field(MockLinkSelector())
        result = selector.find_all(bs, recursive=False)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a href="github">1</a>"""),
            strip("""<a><p>2</p></a>"""),
            strip("""<a>3</a>"""),
        ]

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self,
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
        bs = find_body_element(to_bs(text))
        selector = Field(MockLinkSelector())
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
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
        bs = find_body_element(to_bs(text))
        selector = Field(MockLinkSelector())
        result = selector.find_all(bs, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="widget">1</a>"""),
            strip("""<a><p>2</p></a>"""),
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
            <div class="google">
                <a href="github">Not child</a>
            </div>
            <a href="github">1</a>
            <div><a>Not child</a></div>
            <a><p>2</p></a>
            <span>Hello</span>
            <a>3</a>
        """
        bs = find_body_element(to_bs(text))
        selector = Field(MockLinkSelector())
        result = selector.find_all(bs, recursive=False, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a href="github">1</a>"""),
            strip("""<a><p>2</p></a>"""),
        ]

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            (Field(MockLinkSelector()), Field(MockLinkSelector())),
            (
                Field(MockLinkSelector(), repr=True),
                Field(MockLinkSelector(), repr=True),
            ),
            (
                Field(MockLinkSelector(), repr=True, migrate=True),
                Field(MockLinkSelector(), repr=True, migrate=True),
            ),
            (
                Field(MockLinkSelector(), repr=True, migrate=True, compare=True),
                Field(MockLinkSelector(), repr=True, migrate=True, compare=True),
            ),
        ],
    )
    def test_two_tag_selectors_are_equal(self, selectors: tuple):
        """Tests if two field selectors are equal."""
        assert (selectors[0] == selectors[1]) is True

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            # different selectors
            (Field(MockLinkSelector()), Field(MockDivSelector())),
            # different param
            (
                Field(MockLinkSelector(), repr=True),
                Field(MockLinkSelector(), repr=False),
            ),
            # different one param
            (
                Field(MockLinkSelector(), repr=True, migrate=True),
                Field(MockLinkSelector(), repr=True, migrate=False),
            ),
            # not field
            (Field(MockLinkSelector()), MockLinkSelector()),
        ],
    )
    def test_two_tag_selectors_are_not_equal(self, selectors: tuple):
        """Tests if two field selectors are not equal."""
        assert (selectors[0] == selectors[1]) is False
