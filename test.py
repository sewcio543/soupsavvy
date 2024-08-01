from bs4 import BeautifulSoup

from soupsavvy import AttributeSelector, TagSelector

soup = BeautifulSoup(
    """<p class="title">Animal Farm</p><p class="price">Price: $10</p>""", "lxml"
)
price_selector = TagSelector(
    "p",
    attributes=[
        AttributeSelector("class", "price"),
        AttributeSelector("class", "title"),
    ],
)
price_selector.find(soup)
