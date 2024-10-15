"""Python script for building changelog from releases.json file."""

import json
import re
from os import path

INPUT_FILE = "releases.json"
OUTPUT_FILE = path.join("docs", "source", "changelog.md")

# releases json keys
BODY_KEY = "body"
TAG_NAME_KEY = "tagName"

TITLE = "Changelog"

with open(INPUT_FILE, "r", encoding="utf8") as f:
    releases = json.load(f)

title = f"# {TITLE}\n\n"

info = title + "\n\n".join(
    f"## {release[TAG_NAME_KEY]}\n{release[BODY_KEY]}".replace("\n", "")
    for release in releases
)

# remove 'What's Changed' header
info = re.sub(r"## What's Changed", r"", info, flags=re.MULTILINE)

with open(OUTPUT_FILE, "w", encoding="utf8") as f:
    f.write(info)
