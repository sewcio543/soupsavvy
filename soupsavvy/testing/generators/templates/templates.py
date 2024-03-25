import random
import string

from soupsavvy.testing.generators import namespace, settings
from soupsavvy.testing.generators.templates.examples import TEMPLATES


class BaseTemplate:
    TEXT = """
    <html>
        <body>
            {tag}
        </body>
    </html>
    """

    def fill(self, tag: str) -> str:
        return self.TEXT.format(tag=tag)

    def generate(self, attr: str) -> str:
        if attr == namespace.TEXT:
            return ""

        options = TEMPLATES.get(attr, None)
        value = random.choice(options) if options else self._generate_unique_id()
        return value

    def _generate_unique_id(self, length: int = 4) -> str:
        new_id = "".join(
            random.choices(
                string.ascii_letters + string.digits,
                k=settings.UNIQUE_ID_LENGTH,
            )
        )
        return new_id
