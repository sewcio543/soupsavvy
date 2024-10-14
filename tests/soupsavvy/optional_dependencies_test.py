"""Testing module for handling optional dependencies."""

import builtins
import importlib
import sys

import pytest
from pytest import MonkeyPatch

real_import = builtins.__import__

SOUPSIEVE = "soupsieve"
LXML = "lxml"

OPTIONAL = {SOUPSIEVE, LXML}


def mock_importerror(name, globals=None, locals=None, fromlist=(), level=0):
    """
    Mock function to patch `builtins.__import__`.
    Whenever optional dependency is imported, raises an ImportError,
    mocking the case when the dependency is not installed.
    """
    if name in OPTIONAL:
        raise ImportError(f"Mocked import error {name}")
    return real_import(
        name, globals=globals, locals=locals, fromlist=fromlist, level=level
    )


def test_css_selectors_module_raises_error_when_soupsieve_is_not_installed(
    monkeypatch: MonkeyPatch,
):
    """
    Test that an ImportError is raised when `soupsieve` is not installed
    while importing `soupsavvy.selectors.css.selectors`.
    """
    monkeypatch.delitem(sys.modules, SOUPSIEVE, raising=False)
    monkeypatch.setattr(builtins, "__import__", mock_importerror)

    with pytest.raises(ImportError, match=SOUPSIEVE):
        import soupsavvy.selectors.css.selectors as css

        importlib.reload(css)


def test_xpath_module_raises_error_when_lxml_is_not_installed(
    monkeypatch: MonkeyPatch,
):
    """
    Test that an ImportError is raised when `lxml` is not installed
    while importing `soupsavvy.selectors.xpath`.
    """
    monkeypatch.delitem(sys.modules, LXML, raising=False)
    monkeypatch.setattr(builtins, "__import__", mock_importerror)

    with pytest.raises(ImportError, match=LXML):
        import soupsavvy.selectors.xpath as xpath

        importlib.reload(xpath)
