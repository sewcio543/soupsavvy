import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--impl",
        action="store",
        default="bs4",
        choices=["bs4", "lxml", "selenium"],
        help="Choose the IElement implementation to test with",
    )


@pytest.fixture
def implementation(request):
    return request.config.getoption("--impl")


def pytest_collection_modifyitems(config, items):
    impl = config.getoption("--impl")
    skip = pytest.mark.skip(reason=f"does not support {impl} implementation")
    marker = f"skip_{impl}"

    for item in items:
        if marker in item.keywords:
            item.add_marker(skip)
