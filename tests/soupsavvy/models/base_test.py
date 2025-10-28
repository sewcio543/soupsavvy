"""
Module with unit tests for BaseModel component,
which is parent class of all user-defined models
and all its utilities, including Field and decorators.
"""

# mypy: disable-error-code="arg-type"

import pytest

import soupsavvy.exceptions as exc
from soupsavvy.interfaces import JSONSerializable
from soupsavvy.models import Required
from soupsavvy.models.base import BaseModel, Field, MigrationSchema, post, serializer
from soupsavvy.operations.selection_pipeline import SelectionPipeline
from tests.soupsavvy.conftest import (
    MockClassMenuSelector,
    MockClassWidgetSelector,
    MockDivSelector,
    MockLinkSelector,
    MockTextOperation,
    ToElement,
    strip,
)
from tests.soupsavvy.models.conftest import (
    PRICE_SELECTOR,
    SCOPE,
    TITLE_SELECTOR,
    MockAddress,
    MockAllowEmptyTitle,
    MockFrozenModel,
    MockMigrationModel,
    MockMigrationName,
    MockMigrationTitle,
    MockModel,
    MockModelOperation,
    MockModelTitleField,
    MockNotEqualModel,
    MockTitle,
)


class MockNotJsonSerializable:
    def __init__(self, x):
        self.x = x


class MockJsonSerializable(JSONSerializable):
    def __init__(self, x):
        self.x = x

    def json(self) -> dict:
        return {"x": self.x}


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
        """
        name_selector = MockClassWidgetSelector() | MockTextOperation()

        class ChildModel(MockModel):
            name = name_selector

        assert ChildModel.fields == {
            "title": Field(TITLE_SELECTOR),
            "price": Field(PRICE_SELECTOR),
            "name": Field(name_selector),
        }

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

    def test_find_returns_first_found_model_instance(self, to_element: ToElement):
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
        bs = to_element(text)
        selector = MockModel
        result = selector.find(bs)

        assert result == MockModel(title="Title", price=10)
        assert result.title == "Title"
        assert result.price == 10
        assert result.attributes == {"title": "Title", "price": 10}

    def test_find_returns_none_if_no_scope_found_and_strict_false(
        self, to_element: ToElement
    ):
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
        bs = to_element(text)
        selector = MockModel
        result = selector.find(bs)
        assert result is None

    def test_find_raises_error_when_no_scope_found_and_strict_true(
        self, to_element: ToElement
    ):
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
        bs = to_element(text)
        selector = MockModel

        with pytest.raises(exc.ModelNotFoundException):
            selector.find(bs, strict=True)

    def test_find_returns_none_if_no_scope_found_with_recursive_false_and_strict_false(
        self, to_element: ToElement
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
        bs = to_element(text)
        selector = MockModel
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_error_if_no_scope_found_with_recursive_false_and_strict_true(
        self, to_element: ToElement
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
        bs = to_element(text)
        selector = MockModel

        with pytest.raises(exc.ModelNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_returns_first_matched_instance_with_recursive_false(
        self, to_element: ToElement
    ):
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
        bs = to_element(text)
        selector = MockModel
        result = selector.find(bs, recursive=False)
        assert result == MockModel(title="Title", price=20)

    def test_find_uses_recursive_search_inside_scope_element_with_recursive_true(
        self, to_element: ToElement
    ):
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
        bs = to_element(text)
        selector = MockModel
        result = selector.find(bs)
        assert result == MockModel(title="Title", price=20)

    def test_find_uses_recursive_search_inside_scope_element_with_recursive_false(
        self, to_element: ToElement
    ):
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
        bs = to_element(text)
        selector = MockModel
        result = selector.find(bs, recursive=False)
        assert result == MockModel(title="Title", price=20)

    @pytest.mark.parametrize(argnames="strict", argvalues=[True, False])
    def test_find_raises_error_when_extraction_of_field_in_scope_failed(
        self, strict: bool, to_element: ToElement
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
        bs = to_element(text)
        selector = MockModel

        # first scope price - <p class="widget">abc</p> is found, text is extracted,
        # but conversion to int raises error.
        with pytest.raises(exc.FieldExtractionException, match="price"):
            selector.find(bs, strict=strict)

    @pytest.mark.parametrize(argnames="strict", argvalues=[True, False])
    def test_find_raises_error_when_field_element_not_found_and_operation_failed(
        self, strict: bool, to_element: ToElement
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
        bs = to_element(text)
        selector = MockModel

        with pytest.raises(exc.FieldExtractionException, match="title"):
            selector.find(bs, strict=strict)

    @pytest.mark.parametrize(argnames="strict", argvalues=[True, False])
    def test_find_allows_empty_attributes_of_model_if_errors_handled_properly(
        self, strict: bool, to_element: ToElement
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
        bs = to_element(text)
        selector = MockAllowEmptyTitle
        result = selector.find(bs, strict=strict)
        assert result == MockAllowEmptyTitle(title=None, price=10)

    def test_find_all_returns_list_of_models_from_all_found_scopes(
        self, to_element: ToElement
    ):
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
        bs = to_element(text)
        selector = MockModel
        result = selector.find_all(bs)
        assert result == [
            MockModel(title="Title", price=10),
            MockModel(title="Title2", price=20),
            MockModel(title="Title3", price=30),
        ]

    def test_find_all_returns_empty_list_if_no_scope_was_found(
        self, to_element: ToElement
    ):
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
        bs = to_element(text)
        selector = MockModel
        result = selector.find_all(bs)
        assert result == []

    def test_find_all_returns_empty_list_if_no_scope_was_found_with_recursive_false(
        self, to_element: ToElement
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
        bs = to_element(text)
        selector = MockModel
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_list_of_models_from_all_found_scopes_with_recursive_false(
        self, to_element: ToElement
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
        bs = to_element(text)
        selector = MockModel
        result = selector.find_all(bs, recursive=False)
        assert result == [
            MockModel(title="Title", price=10),
            MockModel(title="Title2", price=20),
        ]

    def test_find_all_returns_first_x_models_with_limit(self, to_element: ToElement):
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
        bs = to_element(text)
        selector = MockModel
        result = selector.find_all(bs, limit=2)
        assert result == [
            MockModel(title="Title", price=10),
            MockModel(title="Title2", price=20),
        ]

    def test_find_all_returns_first_x_models_with_limit_and_recursive_false(
        self, to_element: ToElement
    ):
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
        bs = to_element(text)
        selector = MockModel
        result = selector.find_all(bs, recursive=False, limit=2)
        assert result == [
            MockModel(title="Title", price=10),
            MockModel(title="Title2", price=20),
        ]

    def test_find_all_raises_error_if_any_model_extraction_failed(
        self, to_element: ToElement
    ):
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
        bs = to_element(text)
        selector = MockModel

        with pytest.raises(exc.FieldExtractionException, match="price"):
            selector.find_all(bs)

    def test_find_all_allows_empty_attribute_if_handled_properly(
        self, to_element: ToElement
    ):
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
        bs = to_element(text)
        selector = MockAllowEmptyTitle
        result = selector.find_all(bs)
        assert result == [
            MockAllowEmptyTitle(title="Title", price=10),
            MockAllowEmptyTitle(title=None, price=20),
        ]

    def test_field_can_be_another_model_class(self, to_element: ToElement):
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
        bs = to_element(text)
        selector = MockModel
        result = selector.find(bs)
        assert result == MockModel(
            info=MockInfoModel(title="Title", author="Author"), price=10
        )

    def test_model_field_is_not_required_if_scope_not_found(
        self, to_element: ToElement
    ):
        """
        Tests if model as standard field is not required both in non and strict mode.
        If scope defined in nested model is not found, then field will be None.
        """

        class MockInfoModel(BaseModel):
            __scope__ = MockDivSelector()

            title = Required(TITLE_SELECTOR)
            author = MockClassMenuSelector() | MockTextOperation()

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            info = MockInfoModel
            price = PRICE_SELECTOR

        text = """
            <div>
                <span>
                    <a>Title</a>
                    <p class="menu">Author</p>
                </span>
                <p class="widget">10</p>
            </div>
        """
        bs = to_element(text)
        selector = MockModel

        result = selector.find(bs)
        assert result == MockModel(info=None, price=10)

        result = selector.find(bs, strict=True)
        assert result == MockModel(info=None, price=10)

    def test_fields_of_nested_model_field_is_not_required(self, to_element: ToElement):
        """
        Tests if fields of nested model are not required both in non and strict mode.
        If scope defined in nested model is found, but some field defined in submodel
        cannot be found in subscope, then field will be None.
        """

        class MockInfoModel(BaseModel):
            __scope__ = MockDivSelector()

            title = TITLE_SELECTOR
            author = MockClassMenuSelector()

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            info = MockInfoModel
            price = PRICE_SELECTOR

        text = """
            <div>
                <div>
                    <a>Title</a>
                </div>
                <p class="widget">10</p>
            </div>
        """
        bs = to_element(text)
        selector = MockModel

        result = selector.find(bs)
        assert result == MockModel(
            info=MockInfoModel(title="Title", author=None), price=10
        )

        result = selector.find(bs, strict=True)
        assert result == MockModel(
            info=MockInfoModel(title="Title", author=None), price=10
        )

    def test_missing_required_nested_model_field_raises_exception(
        self, to_element: ToElement
    ):
        """
        Tests if there is a missing field of nested model, which is required by its
        definition, then FieldExtractionException exception will be raised in both
        non and strict mode.
        """

        class MockInfoModel(BaseModel):
            __scope__ = MockDivSelector()

            title = TITLE_SELECTOR
            author = Required(MockClassMenuSelector())

        class MockModel(BaseModel):
            __scope__ = MockDivSelector()

            info = MockInfoModel
            price = PRICE_SELECTOR

        text = """
            <div>
                <div>
                    <a>Title</a>
                </div>
                <p class="widget">10</p>
            </div>
        """
        bs = to_element(text)
        selector = MockModel

        with pytest.raises(exc.FieldExtractionException):
            selector.find(bs)

        with pytest.raises(exc.FieldExtractionException):
            selector.find(bs, strict=True)

    def test_error_in_field_extraction_of_nested_model_is_propagated(
        self, to_element: ToElement
    ):
        """
        Tests if any error in extraction of fields of nested model is propagated
        and instance of model is not created both in non and strict mode.
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
                </div>
                <p class="widget">10</p>
            </div>
        """
        bs = to_element(text)
        selector = MockModel

        with pytest.raises(exc.FieldExtractionException):
            selector.find(bs)

        with pytest.raises(exc.FieldExtractionException):
            selector.find(bs, strict=True)

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

    @pytest.mark.parametrize(
        "models",
        [
            # not BaseMode instance
            (MockModel(title="Title", price=10), MockLinkSelector()),
            # attributes the same, but different model type
            (
                MockModel(title="Title", price=10),
                MockNotEqualModel(title="Title", price=10),
            ),
        ],
    )
    def test_equality_check_returns_not_implemented(self, models):
        """Tests if equality check returns NotImplemented for non comparable types."""
        result = models[0].__eq__(models[1])
        assert result is NotImplemented

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

    def test_json_serialization_on_basic_model(self):
        """
        Tests if `json` method serializes basic model properly.
        This should only return the dictionary of object attributes - the same
        output as in case of `attributes` property.
        """
        instance = MockModel(title="Title", price=10)
        json_dict = instance.json()

        assert json_dict == {"title": "Title", "price": 10} == instance.attributes

    def test_json_serialization_on_nested_models(self):
        """
        Tests if `json` method serializes fields, that are instances of other models.
        It should return a nested dictionary representation of the model.
        """

        class MockNestedModel(BaseModel):
            __scope__ = SCOPE

            title = MockTitle
            price = PRICE_SELECTOR

        title_instance = MockTitle(name="Title")
        instance = MockNestedModel(title=title_instance, price=10)
        json_dict = instance.json()
        title_json = title_instance.json()

        assert title_json == {"name": "Title"}
        assert json_dict == {"title": title_json, "price": 10}

    def test_serialize_decorator_changes_serialization(self):
        """
        Tests if the serialize decorator changes the serialization output
        for particular field.
        """

        class ChildModel(MockModel):

            @serializer("title")
            def serialize_title(self, value: str):
                return value.upper()

        instance = ChildModel(title="Title", price=10)
        json_dict = instance.json()

        assert json_dict == {"title": "TITLE", "price": 10}

    def test_method_decorated_with_serializer_with_invalid_field_name_is_ignored(self):
        """
        Tests if method decorated with serializer with argument,
        that is not a field name is ignored and not applied to the model instance.
        The same way, any method not decorated is ignored.
        """

        class ChildModel(MockModel):

            @serializer("random")
            def process_title(self, value: str) -> str:
                return value + "!"

            def serialize_price(self, value: int) -> int:
                return value + 10

        model = ChildModel(title="Title", price=10)
        assert model.json() == {"title": "Title", "price": 10}

    def test_serializers_of_the_same_field_are_overwritten(self):
        """
        Tests if serializers of the same field are overwritten by the last one.
        Only last defined serializer is applied to the field.
        """

        class ChildModel(MockModel):

            @serializer("title")
            def serialize_title(self, value: str) -> str:
                return value + "!"

            @serializer("title")
            def serialize_title2(self, value: str) -> str:
                return value + "!?"

        model = ChildModel(title="Title", price=10)
        assert model.json() == {"title": "Title!?", "price": 10}

    def test_custom_serializer_methods_are_inherited_and_overridden(self):
        """
        Tests if custom serializer methods are inherited from base class
        and can be overridden in child class.
        """

        class ChildModel(MockModel):

            @serializer("title")
            def serialize_title(self, value: str) -> str:
                return value + "!"

            @serializer("price")
            def serialize_price(self, value: int) -> int:
                return value + 10

        class GrandChildModel(ChildModel):

            @serializer("title")
            def serialize_title(self, value: str) -> str:
                return value + "!!"

        model = GrandChildModel(title="Title", price=10)
        json_dict = model.json()

        assert json_dict == {"title": "Title!!", "price": 20}

    def test_errors_in_serializer_methods_are_propagated(self):
        """
        Tests if any error raised in serializer method is propagated and not handled.
        """

        class ChildModel(MockModel):

            @serializer("title")
            def serialize_title(self, value: str) -> str:
                raise ValueError("Error")

        instance = ChildModel(title="Title", price=10)

        with pytest.raises(ValueError):
            instance.json()

    def test_raises_exception_when_method_is_both_postprocessor_and_serializer(self):
        """
        Tests if any error raised in serializer method is propagated and not handled,
        even when one of them is invalid and would be otherwise ignored.
        Class with this configuration is invalid and won't be created.
        """

        with pytest.raises(exc.InvalidDecorationException):

            class ChildModel1(MockModel):

                @serializer("title")
                @post("title")
                def method(self, value: str) -> str:
                    return value

        with pytest.raises(exc.InvalidDecorationException):

            class ChildModel2(MockModel):

                @serializer("title")
                @post("random")
                def method(self, value: str) -> str:
                    return value

    def test_json_serializable_objects_are_serialized(self):
        """
        Tests if any object as a field that inherits from JsonSerializable
        is serialized using its json method.
        """

        title_instance = MockJsonSerializable(10)
        instance = MockModel(title=title_instance, price=10)
        json_dict = instance.json()
        title_json = title_instance.json()

        assert title_json == {"x": 10}
        assert json_dict == {"title": title_json, "price": 10}

    @pytest.mark.parametrize(
        argnames="title",
        argvalues=[
            MockTitle(name="Title"),
            MockJsonSerializable(20),
            MockNotJsonSerializable(67),
        ],
        ids=["single_model", "json_serializable", "not_json_serializable_object"],
    )
    def test_serializer_decorator_overrides_default_serialization_and_raises_error(
        self, title
    ):
        """
        Tests if serializer decorator overrides default serialization
        and raises ModelNotJsonSerializableException when returned object
        is not JSON serializable.
        """

        class ChildModel(MockModel):

            @serializer("title")
            def serialize_title(self, value):
                # override serialization to just return the value directly
                return value

        instance = ChildModel(title=title, price=10)

        with pytest.raises(exc.ModelNotJsonSerializableException):
            instance.json()

    @pytest.mark.parametrize(
        argnames="title",
        argvalues=[
            [MockTitle(name="Title1"), "some_string"],
            MockNotJsonSerializable(67),
            {"key1": MockTitle(name="Title"), "key2": "value2"},
        ],
        ids=[
            "list_with_not_json_serializable",
            "not_json_serializable_object",
            "dict_with_not_json_serializable",
        ],
    )
    def test_raises_error_when_field_object_is_not_json_serializable(self, title):
        """
        Tests if ModelNotJsonSerializableException is raised
        when any of field objects is not JSON serializable.
        """

        instance = MockModel(
            title=title,
            price=10,
        )

        with pytest.raises(exc.ModelNotJsonSerializableException):
            instance.json()

    def test_or_operation_on_model_class_returns_selection_pipeline(self):
        """
        Tests if or operation on model class returns SelectionPipeline.
        Only valid argument is instance of BaseOperation.
        """
        operation = MockModelOperation()
        pipe = MockModel | operation

        assert isinstance(pipe, SelectionPipeline)
        assert pipe.selector == MockModel
        assert pipe.operation == operation

    def test_or_raises_error_if_not_operation(self):
        """
        Tests if or operation raises NotOperationException
        when argument is not an instance of BaseOperation.
        """
        operation = "invalid_operation"

        with pytest.raises(exc.NotOperationException):
            MockModel | operation  # type: ignore

    def test_or_raises_type_error_if_done_on_instance(self):
        """
        Tests if or operation performed on model instance raises TypeError.
        It does not make sense to used it this way and it's not implemented.
        Instance of model can be passed directly to SelectionPipeline initializer
        though as valid argument, which does not make much sense, since it works
        exactly the same way as model class, but it's still valid TagSearcher instance
        and can be used anywhere as standard TagSearcher.
        """
        instance = MockModel(title="Title", price=10)

        with pytest.raises(TypeError):
            instance | MockModelOperation()  # type: ignore


@pytest.mark.selector
class TestField:
    """
    Unit tests suite for Field class, it's a wrapper of selector to which it delegates.
    Runs full set of tests on find methods with use of simple selector to make sure
    it delegates correctly with passing all parameters.
    Field is supposed to be used with BaseModel, so it's tested in integration tests
    as well, but, it's worth to have unit tests as it can be used independently.
    """

    def test_find_returns_first_element_matching_selector(self, to_element: ToElement):
        """Tests if find method returns first element matching selector."""
        text = """
            <div href="github"></div>
            <a class="widget">1</a>
            <a><p>2</p></a>
            <span>
                <a>3</a>
            </span>
        """
        bs = to_element(text)
        selector = Field(MockLinkSelector())
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<a class="widget">1</a>""")

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
        selector = Field(MockLinkSelector())
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
            <div href="github"></div>
            <span class="widget"></span>
            <div><p>Hello</p></div>
            <span>
                <div>Hello</div>
            </span>
        """
        bs = to_element(text)
        selector = Field(MockLinkSelector())

        with pytest.raises(exc.TagNotFoundException):
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
        selector = Field(MockLinkSelector())
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
        selector = Field(MockLinkSelector())
        result = selector.find_all(bs)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="widget">1</a>"""),
            strip("""<a><p>2</p></a>"""),
            strip("""<a>3</a>"""),
        ]

    def test_find_returns_first_matching_child_if_recursive_false(
        self, to_element: ToElement
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
        selector = Field(MockLinkSelector())
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<a href="github">1</a>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(
        self, to_element: ToElement
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
        selector = Field(MockLinkSelector())
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
            <div class="google">
                <a href="github">Not child</a>
            </div>
            <div><a>Not child</a></div>
            <span>Hello</span>
        """
        bs = to_element(text)
        selector = Field(MockLinkSelector())

        with pytest.raises(exc.TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_all_returns_all_matching_children_when_recursive_false(
        self, to_element: ToElement
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
        selector = Field(MockLinkSelector())
        result = selector.find_all(bs, recursive=False)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a href="github">1</a>"""),
            strip("""<a><p>2</p></a>"""),
            strip("""<a>3</a>"""),
        ]

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self, to_element: ToElement
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
        selector = Field(MockLinkSelector())
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_only_x_elements_when_limit_is_set(
        self, to_element: ToElement
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
        selector = Field(MockLinkSelector())
        result = selector.find_all(bs, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="widget">1</a>"""),
            strip("""<a><p>2</p></a>"""),
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
            (
                Field(MockTitle),
                Field(MockTitle),
            ),
            (
                Field(MockTitle, repr=True, migrate=True),
                Field(MockTitle, repr=True, migrate=True),
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
            # different models
            (Field(MockTitle), Field(MockModel)),
            # model and selector
            (Field(MockTitle), Field(MockLinkSelector())),
            # same model with different config
            (Field(MockTitle, repr=False), Field(MockTitle, repr=True)),
        ],
    )
    def test_two_tag_selectors_are_not_equal(self, selectors: tuple):
        """Tests if two field selectors are not equal."""
        assert (selectors[0] == selectors[1]) is False

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[(Field(MockLinkSelector()), MockLinkSelector())],
    )
    def test_equality_check_returns_not_implemented(self, selectors: tuple):
        """Tests if equality check returns NotImplemented for non comparable types."""
        result = selectors[0].__eq__(selectors[1])
        assert result is NotImplemented
