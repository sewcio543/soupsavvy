# SoupSavvy

## Package

[![jhc github](https://img.shields.io/badge/GitHub-sewcio543-181717.svg?style=flat&logo=github)](https://github.com/jhrcook)
[![!pypi](https://img.shields.io/pypi/v/soupsavvy?color=orange)](https://pypi.org/project/soupsavvy/)
[![!python-versions](https://img.shields.io/pypi/pyversions/soupsavvy)](https://www.python.org/)

## Testing

![example workflow](https://github.com/sewcio543/soupsavvy/actions/workflows/tests.yml/badge.svg)
[![codecov](https://codecov.io/gh/sewcio543/soupsavvy/graph/badge.svg?token=RZ51VS3QLB)](https://codecov.io/gh/sewcio543/soupsavvy)

## Code Quality

![Build](https://github.com/sewcio543/soupsavvy/actions/workflows/build_package.yml/badge.svg)

![example workflow](https://github.com/sewcio543/soupsavvy/actions/workflows/linting.yml/badge.svg)
[![Linter: flake8](https://img.shields.io/badge/flake8-checked-blueviolet)](https://github.com/PyCQA/flake8)

![example workflow](https://github.com/sewcio543/soupsavvy/actions/workflows/formatting.yml/badge.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

![example workflow](https://github.com/sewcio543/soupsavvy/actions/workflows/type_checking.yml/badge.svg)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

![example workflow](https://github.com/sewcio543/soupsavvy/actions/workflows/pre-commit.yml/badge.svg)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

## About

**SoupSavvy** is a library designed to make web scraping tasks more efficient and manageable. Automating web scraping can be a thankless and time-consuming job. SoupSavvy builds around [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) library enabling developers to create more complex workflows and advanced searches with ease.

## Key Features

- **Automated Web Scraping**: SoupSavvy simplifies the process of web scraping by providing intuitive interfaces and tools for automating tasks.

- **Complex Workflows**: With SoupSavvy, developers can create complex scraping workflows effortlessly, allowing for more intricate data extraction.

- **Productionalize Scraping Code**: By providing structured workflows and error handling mechanisms, SoupSavvy facilitates the productionalization of scraping code, making it easier to integrate into larger projects and pipelines.

## Getting Started

### Installation

SoupSavvy is published on PyPi and can be installed via pip:

```bash
pip install soupsavvy
```

### Usage

For simple html code snippet parsed into bs4 Tag we want to extract specific tag(s):

```html
    <div class="menu" role="search">
        <a class="option" href="twitter.com/page">Twitter Page</a>
        <a class="option" href="github.com/fake">Fake Ghb Page</a>
        <a class="blank" href="github.com/blank">Blank Github Page</a>
        <a class="option" href="github.com/correct">Correct Github Page</a>
    </div>
    <div class="menu" role="placeholder">
        <a class="option" href="github.com/oos">Out of Scope Github Page</a>
    </div>
```

Replace convoluted BeautifulSoup approach:

```python
div = markup.find(
    "div",
    class_="menu",
    role="search",
)

if not isinstance(div, Tag):
    raise ValueError("No element found")

a = div.find(
    "a",
    class_="option",
    href=re.compile("github.com"),
    string=re.compile("Github"),
)

if not isinstance(a, Tag):
    raise ValueError("No element found")
```

with savvier version:

```python
import re

from soupsavvy import AttributeTag, ElementTag, PatternElementTag, StepsElementTag

# define your complex tag once
tag = StepsElementTag(
    ElementTag(
        "div",
        attributes=[
            AttributeTag(name="class", value="menu"),
            AttributeTag(name="role", value="search"),
        ],
    ),
    PatternElementTag(
        tag=ElementTag(
            "a",
            attributes=[
                AttributeTag(name="class", value="option"),
                AttributeTag(name="href", value="github.com", re=True),
            ],
        ),
        pattern="Github",
        re=True,
    ),
)
# reuse it in any place to search for tag in any markup, if not found, strict mode raises exception
a = tag.find(markup, strict=True)
```

This streamlined SoupSavvy approach and encapsulating complex tag(s) into single objects transforms web scraping tasks from a potential 'soup sandwich'🥪 into a 'duck soup' 🦆 scenario.

With SoupSavvy's robust features, developers can avoid common problems encountered in web scraping, such as exception handling or integration with type checkers.

## Contributing

If you'd like to contribute to SoupSavvy, feel free to check out the [GitHub repository](https://github.com/sewcio543/soupsavvy) and submit pull requests into one of development branches. Any feedback, bug reports, or feature requests are welcome!

## 📄 License

[![MIT License](https://img.shields.io/badge/license-MIT-green?style=plastic)](https://choosealicense.com/licenses/mit/)  
SoupSavvy is licensed under the [MIT License](https://opensource.org/licenses/MIT), allowing for both personal and commercial use. See the `LICENSE` file for more information.

## Acknowledgements

SoupSavvy is built upon the foundation of excellent BeautifulSoup. We extend our gratitude to the developers and contributors of this projects for their invaluable contributions to the Python community and making our life a lot easier!

---

Make your soup more beautiful and savvier!  
Happy scraping! 🍲✨

## TODO

- Scraping workflows from soup to nuts
- New Tag components
- Enhanced CI pipeline
- Documentation
