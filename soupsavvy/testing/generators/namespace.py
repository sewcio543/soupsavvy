import os

SETUP_FILE = os.path.join("soupsavvy", "_resources", "generator_setup.json")

VOID_TAGS = [
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "source",
    "track",
    "wbr",
]

ALL_ATTRS = ["alt", "class", "href", "src", "id", "title"]
ALL_TAGS = ["div", "a", "img", "span"]
TEXT = "text"

DEFAULT_N_ELEMENTS = 3
DEFAULT_MAX_DEPTH = 3
PARSER = "lxml"
