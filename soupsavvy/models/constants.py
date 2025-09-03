"""Module with constants and defaults for model classes."""

# default recursive value for finding fields of model within the scope
DEFAULT_RECURSIVE = True
# default strict value for finding fields of model within the scope
DEFAULT_STRICT = False

# attribute to set on method that post-processes field value of model
POST_ATTR = "__post_process_method__"
# attribute to set on method that serializes field value of model
SERIALIZER_ATTR = "__serializer_method__"
# name of the attribute that keep tracks of initialization state
INITIALIZED = "_initialized"

SCOPE = "__scope__"
INHERIT_FIELDS = "__inherit_fields__"
POST_PROCESSORS = "__post_processors__"
SERIALIZERS = "__serializers__"
FROZEN = "__frozen__"

SPECIAL_FIELDS = {SCOPE, INHERIT_FIELDS, POST_PROCESSORS, FROZEN}

# based model classes that skip initialization checks
BASE_MODELS = {"BaseModel"}
