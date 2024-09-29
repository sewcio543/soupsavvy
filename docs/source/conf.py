# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

from sphinx.application import Sphinx

sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "soupsavvy"
author = "sewcio543"
copyright = "2024, soupsavvy"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "m2r2",
    "myst_nb",
]

exclude_patterns = [
    "*namespace*.rst",
    "soupsavvy.selectors.nth.nth_utils.rst",
    "soupsavvy.models.constants.rst",
]

add_module_names = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
source_suffix = [".rst", ".md", ".ipynb"]
html_show_sphinx = False

autodoc_member_order = "bysource"


def skip(app, what, name, obj, would_skip, options):
    if name == "__init__":
        return False

    return would_skip


def setup(app: Sphinx):
    app.connect("autodoc-skip-member", skip)
    app.add_css_file("css/custom.css")
