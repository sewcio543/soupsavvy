"""Module for testing the generator module components."""

import pytest

import soupsavvy.exceptions as exc
from soupsavvy.testing.generators.generators import AttributeGenerator, TagGenerator
from soupsavvy.testing.generators.templates.templates import (
    BaseTemplate,
    ConstantTemplate,
)
from tests.soupsavvy.testing.generators.conftest import TEMPLATE_VALUE, MockTemplate


@pytest.mark.generator
class TestAttributeGenerator:
    """Component with unit tests for the AttributeGenerator class."""

    @pytest.fixture(scope="class")
    def mock_template(self) -> BaseTemplate:
        """Fixture for a custom template."""
        return MockTemplate()

    def test_generates_exact_value_when_string_passed(self):
        """
        Test that the generator returns the exact value along attribute name
        when a string is passed.
        """
        generator = AttributeGenerator(name="class", value="test")
        actual = generator.generate()
        expected = 'class="test"'
        assert actual == expected

    def test_generates_template_attribute_value_if_template_specified(
        self, mock_template: BaseTemplate
    ):
        """
        Test that the generator returns attribute value generated by template
        when the template is specified.
        """
        generator = AttributeGenerator(name="class", value=mock_template)
        actual = generator.generate()
        assert actual == f'class="{TEMPLATE_VALUE}"'

    def test_generates_empty_string_value_when_no_value_specified(self):
        """
        Test that the generator returns empty string if no value is specified.
        Empty string is generated by empty template.
        """
        generator = AttributeGenerator(name="name")
        actual = generator.generate()
        assert actual == f'name=""'

    def test_empty_value_is_converted_to_constant_template(self):
        """
        Tests that if value parameter is empty string, value is ConstantTemplate
        that always generate the same value (empty string). It should not be converted
        to EmptyTemplate, even though it would yield the same results.
        """
        generator = AttributeGenerator(name="src", value="")
        assert isinstance(generator.value, ConstantTemplate)
        assert generator.generate() == 'src=""'

    @pytest.mark.parametrize(
        "value",
        [123, ["hello", "world"]],
        ids=["int", "list"],
    )
    def test_raises_error_when_invalid_types_is_passed_as_value(self, value):
        """
        Test that init raises TypeError when invalid type is passed as value.
        Allowed types are str, BaseTemplate and None. Passing other types
        is not acceptable and should raise an error.
        """
        with pytest.raises(exc.InvalidTemplateException):
            AttributeGenerator(name="class", value=value)

    @pytest.mark.parametrize(
        argnames="name", argvalues=[123, ["hello", "world"]], ids=["int", "list"]
    )
    def test_raises_error_when_name_has_invalid_type(self, name):
        """
        Test that init raises TypeError when invalid type is passed as name.
        Allowed type is ony str. Passing other types is not acceptable
        and should raise an error.
        """
        with pytest.raises(TypeError):
            AttributeGenerator(name=name)

    def test_raises_exception_if_empty_string_passed_as_name(self):
        """
        Test that init raises EmptyNameException when empty string is passed as name.
        Name must be a non-empty string, empty string
        is of course not allowed html attribute name.
        """
        with pytest.raises(exc.EmptyNameException):
            AttributeGenerator(name="")


@pytest.mark.generator
class TestTagGenerator:
    """Component with unit tests for the TagGenerator class."""

    def test_raises_error_if_attrs_parameter_is_string(self):
        """
        Test that the generator raises TypeError upon initialization
        if the attrs parameter is a string.
        """
        with pytest.raises(TypeError):
            TagGenerator(name="div", attrs="class")

    def test_generates_empty_tag_if_only_name_specified(self):
        """
        Test that the generator returns string with empty tag
        if only the name is specified.
        """
        generator = TagGenerator(name="div")
        actual = generator.generate()
        expected = "<div></div>"
        assert actual == expected

    @pytest.mark.parametrize(
        argnames="name",
        argvalues=["img", "hr"],
        ids=["img", "hr"],
    )
    def test_generates_closed_tag_for_void_tags_with_no_children(self, name: str):
        """
        Test that the generator returns string with self-closing tag for void tags
        if no children are specified.
        """
        generator = TagGenerator(name=name)
        actual = generator.generate()
        expected = f"<{name}/>"
        assert actual == expected

    def test_generates_tag_with_attributes(self):
        """
        Test that the generator returns string with tag
        that has specified constant attributes.
        Attributes should be generated in order they were specified.
        In this case passing list of AttributeGenerator instances.
        """
        generator = TagGenerator(
            name="div",
            attrs=[
                AttributeGenerator(name="class", value="test"),
                AttributeGenerator(name="id", value="unique"),
            ],
        )
        actual = generator.generate()
        expected = '<div class="test" id="unique"></div>'
        assert actual == expected

    def test_generates_tag_with_children(self):
        """
        Test that the generator returns string with tag with child elements
        if children are specified. Children tags should be generated in order
        they were specified. In this case passing list of TagGenerator instances.
        """
        generator = TagGenerator(
            name="div",
            children=[
                TagGenerator(name="span"),
                TagGenerator(name="p"),
            ],
        )
        actual = generator.generate()
        expected = "<div><span></span><p></p></div>"
        assert actual == expected

    def test_generates_tag_with_constant_text(self):
        """
        Test that the generator returns string with tag and constant text.
        In this case testing string value as text parameter, which should result
        in constant text template.
        """
        generator = TagGenerator(name="div", text="test")
        actual = generator.generate()
        expected = "<div>test</div>"
        assert actual == expected

    def test_generates_tag_with_text_template(self):
        """
        Test that the generator returns string with tag with text that was
        generated by the template.
        In this case testing mock template as text parameter and checking if
        expected value was generated.
        """
        generator = TagGenerator(name="div", text=MockTemplate())
        actual = generator.generate()
        expected = f"<div>{TEMPLATE_VALUE}</div>"
        assert actual == expected

    def test_generates_tag_with_children_and_text_template(self):
        """
        Test that the generator returns string with tag
        that has specified children and text template.
        """
        generator = TagGenerator(
            name="div",
            children=[
                TagGenerator(name="span"),
                TagGenerator(name="p"),
            ],
            text=MockTemplate(),
        )
        actual = generator.generate()
        expected = f"<div><span></span><p></p>{TEMPLATE_VALUE}</div>"
        assert actual == expected

    def test_raises_error_when_void_tag_has_children(self):
        """
        Test that VoidTagWithChildrenException is raised when a void tag has children.
        Void tags cannot have children.
        """
        with pytest.raises(exc.VoidTagWithChildrenException):
            TagGenerator(name="img", children=[TagGenerator(name="span")])

    @pytest.mark.parametrize(
        argnames="duplicate",
        argvalues=[
            AttributeGenerator(name="class"),
            "class",
            ("class", "hello"),
            AttributeGenerator(name="id"),
            "id",
            ("id", "1234"),
            AttributeGenerator(name="name", value="test"),
            "name",
            ("name", "random"),
        ],
        ids=[
            "attribute-attribute",
            "attribute-string",
            "attribute-tuple",
            "string-attribute",
            "string-string",
            "string-tuple",
            "tuple-attribute",
            "tuple-string",
            "tuple-tuple",
        ],
    )
    def test_raises_error_when_attribute_names_not_unique(self, duplicate):
        """
        Test that NotUniqueAttributesException is raised
        when the input attribute names are not unique.
        Allowed attribute types are AttributeGenerator, string, and tuple.
        Input attributes are converted to AttributeGenerator instances
        that must generate unique names.
        Testing all combinations of duplicate attribute names.
        """
        attributes = [
            AttributeGenerator(name="class", value="test"),
            "name",
            ("id", "unique"),
            "business",
            ("url", "wiki.com"),
            AttributeGenerator(name="level", value="1"),
        ] + [duplicate]

        with pytest.raises(exc.NotUniqueAttributesException):
            TagGenerator(name="div", attrs=attributes)

    def test_passing_attributes_as_strings(self):
        """
        Test that attributes can be passed as strings.
        """
        generator = TagGenerator(name="div", attrs=["class", "name"])
        actual = generator.generate()
        expected = '<div class="" name=""></div>'
        assert actual == expected

    def test_passing_attributes_as_tuples_parses_to_attribute_properly(self):
        """
        Test that attributes can be passed as tuples, which is equivalent to
        passing AttributeGenerator instances with (name, value) arguments.
        Under the hood, tuples are converted to AttributeGenerator instances.
        """
        generator = TagGenerator(
            name="div",
            attrs=[
                ("class", "test"),
                ("id", "unique"),
            ],
        )
        actual = generator.generate()
        expected = '<div class="test" id="unique"></div>'
        assert actual == expected

    def test_passing_mixed_types_as_attributes(self):
        """
        Test that attributes can be passed as mixed types, all of them should be
        converted to AttributeGenerator instances under the hood.
        """
        generator = TagGenerator(
            name="div",
            attrs=[
                "class",
                ("name", "test"),
                AttributeGenerator(name="id", value="unique"),
            ],
        )
        actual = generator.generate()
        expected = '<div class="" name="test" id="unique"></div>'
        assert actual == expected

    def test_passing_attribute_with_specified_template(self):
        """
        Test that attributes can be passed with specified template.
        Value of the attribute should be generated by the template.
        Template can be passed as the second element of the tuple for value as well.
        """
        generator = TagGenerator(
            name="div",
            attrs=[
                AttributeGenerator(name="class", value=MockTemplate()),
                ("id", MockTemplate()),
            ],
        )
        actual = generator.generate()
        expected = f'<div class="{TEMPLATE_VALUE}" id="{TEMPLATE_VALUE}"></div>'
        assert actual == expected

    def test_passing_nested_generators_as_children(self):
        """
        Test that nested generators can be passed as children. Any TagGenerator
        can be passed as a child, its nested tags should be generated and placed
        in the parent tag.
        """
        generator = TagGenerator(
            name="div",
            children=[
                TagGenerator(
                    name="span",
                    children=[
                        TagGenerator(
                            name="a",
                            attrs=[("href", "www.soupsavvy.com"), "alt"],
                            text="link",
                        )
                    ],
                    attrs=["class"],
                ),
            ],
        )
        actual = generator.generate()
        expected = '<div><span class=""><a href="www.soupsavvy.com" alt="">link</a></span></div>'
        assert actual == expected

    @pytest.mark.parametrize(
        "text",
        [123, ["hello", "world"]],
        ids=["int", "list"],
    )
    def test_raises_error_when_invalid_types_is_passed_as_text(self, text):
        """
        Test that init raises TypeError when invalid type is passed as value.
        Allowed types are str, BaseTemplate and None. Passing other types
        is not acceptable and should raise an error.
        """
        with pytest.raises(exc.InvalidTemplateException):
            TagGenerator(name="div", text=text)

    @pytest.mark.parametrize(
        argnames="name",
        argvalues=[123, ["hello", "world"]],
        ids=["int", "list"],
    )
    def test_raises_error_when_invalid_type_is_passed_as_name(self, name):
        """
        Test that init raises TypeError when invalid type is passed as name.
        Allowed types is only string.
        Passing other types is not acceptable and should raise an error.
        """
        with pytest.raises(TypeError):
            TagGenerator(name=name)

    def test_raises_exception_when_empty_string_is_passed_as_name(self):
        """
        Test that init raises EmptyNameException when empty string is passed as name.
        Tag name should be a non-empty string.
        """
        with pytest.raises(exc.EmptyNameException):
            TagGenerator(name="")

    @pytest.mark.parametrize(
        argnames="attr",
        argvalues=["", ("", "test")],
        ids=["string-empty", "tuple-empty"],
    )
    def test_raises_error_if_attribute_name_is_empty(self, attr):
        """
        Test that init raises AttributeParsingError when empty string
        is passed as attribute name.
        It causes error on AttributeGenerator initialization
        and raises EmptyNameException.
        Checking if exception was raised from EmptyNameException exception.
        """
        with pytest.raises(exc.AttributeParsingError) as exc_info:
            TagGenerator(name="div", attrs=[attr])

        assert isinstance(exc_info.value.__context__, exc.EmptyNameException)

    def test_raises_error_if_invalid_typ_was_passed_as_attribute_value(self):
        """
        Test that init raises AttributeParsingError when invalid type
        is passed as attribute value.
        It causes error on AttributeGenerator initialization
        and raises InvalidTemplateException.
        Checking if exception was raised from InvalidTemplateException exception.
        """
        with pytest.raises(exc.AttributeParsingError) as exc_info:
            TagGenerator(
                name="div", attrs=[("class", ["hello", "soupsavvy"])]  # type: ignore
            )

        assert isinstance(exc_info.value.__context__, exc.InvalidTemplateException)

    @pytest.mark.parametrize(
        argnames="attr",
        argvalues=[10, (10, "test")],
        ids=["single", "tuple-like"],
    )
    def test_raises_error_if_invalid_typ_was_passed_as_attribute_name(self, attr):
        """
        Test that init raises AttributeParsingError when invalid type is passed
        for attribute name. It causes error on AttributeGenerator initialization
        and raises TypeError.
        Checking if exception was raised from TypeError exception.
        """
        with pytest.raises(exc.AttributeParsingError) as exc_info:
            TagGenerator(name="div", attrs=[attr])

        assert isinstance(exc_info.value.__context__, TypeError)
