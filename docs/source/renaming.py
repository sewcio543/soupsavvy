"""
Script for renaming the content names in the rst files.

All rst files contain package/module names in the first line.
The script removes soupsavvy name shortening the content name
and suffixes like module or package added by default by sphinx.

CLI Arguments
-------------
directory: str [positional, required]
    Directory with rst files generated with sphinx-apidoc.

Usage
-----
>>> python renaming.py <directory>
"""

import argparse
import glob
import os
import re

parser = argparse.ArgumentParser(description="Rename content names")
parser.add_argument(
    "directory",
    nargs="?",
    type=str,
    default=os.getcwd(),
    help="Directory with rst files to update.",
)

PACKAGE = "soupsavvy"
# ex. soupsavvy.utils.deprecation module - only the header in first line
NAME_PATTERN = re.compile(rf"^{PACKAGE}\.")
# to be removed from the name
SUFFIXES = ["module", "package"]


def main(dir: str) -> None:
    """Rename the content names in the rst files."""
    print(f"Search directory: {dir}")

    for path in glob.glob(f"{dir.rstrip('/')}/*.rst"):

        with open(path, "r") as file:
            content = file.read()

        if not NAME_PATTERN.match(content):
            continue

        print(f"Processing file: {path}")
        content = NAME_PATTERN.sub("", content)

        for suffix in SUFFIXES:
            content = content.replace(f" {suffix}", "")

        with open(path, "w") as file:
            file.write(content)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args.directory)
