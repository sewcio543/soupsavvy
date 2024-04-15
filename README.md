# soupsavvy

-----------------

## Python package that makes web-scraping more manageable

| | |
| --- | --- |
| Package | ![Deployment PyPI](https://github.com/sewcio543/soupsavvy/actions/workflows/production_release.yml/badge.svg) [![GitHub](https://img.shields.io/badge/GitHub-sewcio543-181717.svg?style=flat&logo=github)](https://github.com/sewcio543) [![PyPI](https://img.shields.io/pypi/v/soupsavvy?color=orange)](https://pypi.org/project/soupsavvy/) [![Python Versions](https://img.shields.io/pypi/pyversions/soupsavvy)](https://www.python.org/)|
| Testing | ![Tests](https://github.com/sewcio543/soupsavvy/actions/workflows/tests.yml/badge.svg) [![Codecov](https://codecov.io/gh/sewcio543/soupsavvy/graph/badge.svg?token=RZ51VS3QLB)](https://codecov.io/gh/sewcio543/soupsavvy)|
| Code Quality | ![Build](https://github.com/sewcio543/soupsavvy/actions/workflows/build_package.yml/badge.svg) ![Linting](https://github.com/sewcio543/soupsavvy/actions/workflows/linting.yml/badge.svg) [![pre-commit.ci status](https://results.pre-commit.ci/badge/github/sewcio543/soupsavvy/main.svg)](https://results.pre-commit.ci/latest/github/sewcio543/soupsavvy/main)|
| Documentation | [![readthedocs](https://img.shields.io/readthedocs/pip?logo=readthedocs)](https://github.com/sewcio543/soupsavvy/actions/workflows/documentation.yml/badge.svg) [![Docs link](https://img.shields.io/badge/docs-check_out-blue)](https://sewcio543.github.io/soupsavvy/)|

## Table of Contents

- [About](#about)
- [Key features](#key-features)
- [Instalation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)
- [In the future](#in-the-future)

## About

**soupsavvy** is a library designed to make web scraping tasks more efficient and manageable. Automating web scraping can be a thankless and time-consuming job. It builds around [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) library enabling developers to create more complex workflows and advanced searches with ease.

## Key Features

- **Automated Web Scraping**: soupsavvy simplifies the process of web scraping by providing intuitive interfaces and tools for automating tasks.

- **Complex Workflows**: With soupsavvy, developers can create complex scraping workflows effortlessly, allowing for more intricate data extraction.

- **Productionalize Scraping Code**: By providing structured workflows and error handling mechanisms, soupsavvy facilitates the productionalization of scraping code, making it easier to integrate into larger projects and pipelines.

## Getting Started

### Installation

soupsavvy is published on PyPi and can be installed via pip:

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

This streamlined soupsavvy approach and encapsulating complex tag(s) into single objects transforms web scraping tasks from a potential 'soup sandwich'🥪 into a 'duck soup' 🦆 scenario.

With soupsavvy's robust features, developers can avoid common problems encountered in web scraping, such as exception handling or integration with type checkers.

Full documentation can be found at **[soupsavvy Docs](https://sewcio543.github.io/soupsavvy/)**

## Contributing

If you'd like to contribute to soupsavvy, feel free to check out the [GitHub repository](https://github.com/sewcio543/soupsavvy) and submit pull requests into one of development branches. Any feedback, bug reports, or feature requests are welcome!

## License

[![MIT License](https://img.shields.io/badge/license-MIT-green?style=plastic)](https://choosealicense.com/licenses/mit/)  
soupsavvy is licensed under the [MIT License](https://opensource.org/licenses/MIT), allowing for both personal and commercial use. See the `LICENSE` file for more information.

## Acknowledgements

Soupsavvy is built upon the foundation of excellent BeautifulSoup. We extend our gratitude to the developers and contributors of this projects for their invaluable contributions to the Python community and making our life a lot easier!

-----------------

**Let's soap this soup!**  
**Happy scraping!** ✨

## In the future

- Scraping workflows from soup to nuts
- New Tag components
- Enhanced CI pipeline
- Documentation  
