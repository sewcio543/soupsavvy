"""Module with HTML generators."""

from __future__ import annotations

from typing import Iterable, Optional, Union

import soupsavvy.testing.generators.exceptions as exc
from soupsavvy.testing.generators import namespace
from soupsavvy.testing.generators.base import BaseGenerator
from soupsavvy.testing.generators.templates.base import BaseTemplate
from soupsavvy.testing.generators.templates.config import (
    DEFAULT_TEXT_TEMPLATE,
    DEFAULT_VALUE_TEMPLATE,
)
from soupsavvy.testing.generators.templates.templates import ConstantTemplate

# types for generators
TemplateType = Optional[Union[BaseTemplate, str]]

AttributeType = Union["AttributeGenerator", str, tuple[str, TemplateType]]
ChildType = Union["TagGenerator", str]

AttributeList = Iterable[AttributeType]
ChildList = Iterable[ChildType]

AttributeGeneratorInitExceptions = (
    TypeError,
    exc.InvalidTemplateException,
    exc.EmptyNameException,
)


def _get_template_type(
    value: TemplateType, param: str, default: BaseTemplate
) -> BaseTemplate:
    """
    Get the template type from the input value.

    Parameters
    ----------
    value : TemplateType
        The value to get the template type from.
    param : str
        The name of the parameter.
    default : BaseTemplate
        The default template to use if the value is None.

    Returns
    -------
    BaseTemplate
        The template instance.

    Raises
    ------
    InvalidTemplateException
        If the value is not a string, BaseTemplate or None.
    """
    if value is None:
        return default
    elif isinstance(value, str):
        return ConstantTemplate(value)
    elif not isinstance(value, BaseTemplate):
        raise exc.InvalidTemplateException(
            f"{param} must be a string or a BaseTemplate, not {type(value)}"
        )

    return value


class AttributeGenerator(BaseGenerator):
    """
    Class for generating HTML attribute strings.

    AttributeGenerator allows to generate empty HTML attribute with specific name:

    Example
    --------
    >>> gen = AttributeGenerator("class")
    >>> gen.generate()
    'class=""'

    Attribute can also be generated with specified constant value:

    Example
    --------
    >>> gen = AttributeGenerator("class", value="container")
    >>> gen.generate()
    'class="container"'

    Value can be passed as BaseTemplate instance as well:

    Example
    --------
    >>> from soupsavvy.testing.generators import RandomTemplate
    >>> template = RandomTemplate(length=4, seed=42)
    >>> gen = AttributeGenerator("id", value=template)
    >>> gen.generate()
    'id="Nbrn"'

    For more information on available Templates, how to use them
    and customize for your needs, see the documentation.

    See also
    --------
    soupsavvy.testing.generators.templates module
    soupsavvy.testing.generators.TagGenerator class
    """

    def __init__(self, name: str, value: TemplateType = None) -> None:
        """
        Initializes the AttributeGenerator.

        Parameters
        ----------
        name : str
            The name of the attribute.
        value : TemplateType, optional
            The value of the attribute. Defaults to None.
        """

        self._check_name(name)
        self.name = name
        self.value = _get_template_type(
            value,
            param="name",
            default=DEFAULT_VALUE_TEMPLATE,
        )

    def _check_name(self, name: str) -> None:
        """
        Check if the input name is a valid HTML attribute name.

        Parameters
        ----------
        name : str
            The name to check.

        Raises
        ------
        TypeError
            If the name is not a string.
        EmptyNameException
            If the name is an empty string.
        """
        if not isinstance(name, str):
            raise TypeError(f"'name' parameter must be a string, not {type(name)}")

        if not name:
            raise exc.EmptyNameException(
                "Empty string is not allowed html attribute name, "
                "not-empty string must be provided for 'name' parameter."
            )

    def generate(self) -> str:
        """
        Generates the HTML attribute string.

        Returns
        -------
        str
            The generated HTML attribute string.
        """
        value = self.value.generate()
        return f'{self.name}="{value}"'


class TagGenerator(BaseGenerator):
    """
    Class for generating HTML tag strings.

    TagGenerator allows to generate empty HTML tag with specific name:

    Example
    --------
    >>> gen = TagGenerator("div")
    >>> gen.generate()
    '<div></div>'

    Tag can also be generated with specified attributes:

    Example
    --------
    >>> gen = TagGenerator("div", attrs=[("class", "container")])
    >>> gen.generate()
    '<div class="container"></div>'

    Attributes can be passed as an iterable of of mixed types:
    * AttributeGenerator - instance of AttributeGenerator class
    * str - attribute name, value would be a default Template (empty string)
    * tuple[str, TemplateType] - attribute name and literal value or Template

    Example
    --------
    >>> gen = TagGenerator(
    >>>     name="a",
    >>>     attrs=[
    >>>         ("id", "link"),
    >>>         AttributeGenerator("href", "/endpoint"),
    >>>         "class",
    >>>     ],
    >>> )
    >>> gen.generate()
    '<div id="link" href="/endpoint", class=""></div>'

    Similarly, children can be passed as an iterable of mixed types:
    * TagGenerator - instance of TagGenerator class
    * str - tag name, children tags would be empty

    Example
    --------
    >>> gen = TagGenerator(
    >>>     name="div",
    >>>     children=[
    >>>         "a",
    >>>         TagGenerator("span", attrs=[("class", "container")],
    >>>     ],
    >>> )
    >>> gen.generate()
    '<div><a></a><span class="container"></span></div>'

    Text of the tag can be passed as a string or a Template:

    Example
    --------
    >>> gen = TagGenerator("p", text="Hello, World!")
    >>> gen.generate()
    '<p>Hello, World!</p>'

    Example
    --------
    >>> from soupsavvy.testing.generators import RandomTemplate
    >>> template = RandomTemplate(length=4, seed=42)
    >>> gen = TagGenerator("p", text=template)
    >>> gen.generate()
    '<p>Nbrn</p>'

    For more information on available Templates, how to use them
    and customize for your needs, see the documentation.

    Void tags like <img>, <br>, <hr> etc. can be generated as well
    and are automatically closed:

    Example
    --------
    >>> gen = TagGenerator("img", attrs=[("src", "/path/to/image.jpg")])
    >>> gen.generate()
    '<img src="/path/to/image.jpg"/>'

    No children are allowed for void tags, and an error will be raised.

    See also
    --------
    soupsavvy.testing.generators.templates module
    soupsavvy.testing.generators.AttributeGenerator class
    """

    def __init__(
        self,
        name: str,
        attrs: AttributeList = (),
        children: ChildList = (),
        text: TemplateType = None,
    ) -> None:
        """
        Initialize the TagGenerator.

        Parameters
        ----------
        name : str
            The name of the HTML tag.
        attrs : AttributeList, optional
            The attributes of the tag. Defaults to empty tuple.
        children : ChildList, optional
            The children of the tag. Defaults to empty tuple.
        text : TemplateType, optional
            The text content of the tag.
            Defaults to None, which generates empty string.
        """
        self._void = name in namespace.VOID_TAGS

        if self._void and children:
            raise exc.VoidTagWithChildrenException(
                f"{name} is a void tag and cannot have children"
            )

        self._check_name(name)
        self.name = name

        self.text = _get_template_type(
            text,
            param="text",
            default=DEFAULT_TEXT_TEMPLATE,
        )
        self.attributes = self._process_attributes(attrs)
        self.children = [
            child if isinstance(child, TagGenerator) else TagGenerator(child)
            for child in children
        ]

    def _check_name(self, name: str) -> None:
        """
        Check if the input name is a valid HTML tag name.

        Parameters
        ----------
        name : str
            The name to check.

        Raises
        ------
        TypeError
            If the name is not a string.
        EmptyNameException
            If the name is an empty string.
        """
        if not isinstance(name, str):
            raise TypeError(f"'name' parameter must be a string, not {type(name)}")

        if not name:
            raise exc.EmptyNameException(
                "Empty string is not allowed html tag name, "
                "not-empty string must be provided for 'name' parameter."
            )

    def _process_attributes(
        self, attributes: AttributeList
    ) -> list[AttributeGenerator]:
        """
        Process the input attributes of the tag.

        Parameters
        ----------
        attributes : AttributeList
            The attributes to process.

        Returns
        -------
        list[AttributeGenerator]
            The processed instances of AttributeGenerators.

        Raises
        ------
        AttributeParsingError
            If the input attributes could not be parsed into AttributeGenerators.
        """
        # dict approach for uniqueness check
        attr_dict: dict[str, AttributeGenerator] = {}

        for attr in attributes:
            if isinstance(attr, str):
                attr = (attr, None)

            if not isinstance(attr, AttributeGenerator):
                try:
                    attr = AttributeGenerator(*attr)
                except AttributeGeneratorInitExceptions as e:
                    raise exc.AttributeParsingError(
                        f"Attribute {attr} could not be parsed into AttributeGenerator "
                        "due to following error."
                    ) from e

            attr_name = attr.name

            if attr_name in attr_dict:
                raise exc.NotUniqueAttributesException(
                    f"Input attribute {attr_name} is not unique."
                )

            attr_dict[attr_name] = attr

        return list(attr_dict.values())

    def generate(self) -> str:
        """
        Generates the HTML tag string.

        Returns
        -------
        str
            The generated HTML tag string.
        """
        attrs = " ".join(attr.generate() for attr in self.attributes)
        sep = " " if attrs else ""
        children = "".join(child.generate() for child in self.children)
        tag_content = f"{self.name}{sep}{attrs}"

        if self._void:
            return f"<{tag_content}/>"

        text = self.text.generate()
        return f"<{tag_content}>{children}{text}</{self.name}>"
