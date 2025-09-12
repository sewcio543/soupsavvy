import pytest

BS4 = "bs4"
LXML = "lxml"
SELENIUM = "selenium"
PLAYWRIGHT = "playwright"

IMPLEMENTATIONS = [BS4, LXML, SELENIUM, PLAYWRIGHT]


def pytest_addoption(parser):
    parser.addoption(
        "--impl",
        action="store",
        default=BS4,
        choices=IMPLEMENTATIONS,
        help="Choose the IElement implementation to test with",
    )


@pytest.fixture
def implementation(request):
    return request.config.getoption("--impl")


def pytest_collection_modifyitems(config, items):
    impl = config.getoption("--impl")
    skip = pytest.mark.skip(reason=f"Does not support {impl} implementation")
    marker = f"skip_{impl}"

    for item in items:
        apply = set(IMPLEMENTATIONS) & set(item.keywords)

        if apply and impl not in apply:
            item.add_marker(skip)
            continue

        if marker in item.keywords:
            item.add_marker(skip)
