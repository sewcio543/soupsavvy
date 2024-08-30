"""Module with constants and defaults for model classes."""

# default recursive value for finding fields of model within the scope
DEFAULT_RECURSIVE = True
# default strict value for finding fields of model within the scope
DEFAULT_STRICT = False

SCOPE = "__scope__"
INHERIT_FIELDS = "__inherit_fields__"

SPECIAL_FIELDS = {SCOPE, INHERIT_FIELDS}

# based model classes that skip initialization checks
BASE_MODELS = {"BaseModel"}
