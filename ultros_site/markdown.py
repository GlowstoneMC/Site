# coding=utf-8
import markdown2

from bs4 import BeautifulSoup

__author__ = "Gareth Coles"


class Markdown:
    def __init__(self, markdown):
        self.markdown = markdown
        html = markdown2.markdown(
            markdown, extras={
                "fenced-code-blocks": {},
                "header-ids": {},
                "html-classes": {
                    "table": "table is-bordered is-striped"
                },
                "target-blank-links": {},
                "tables": {}
            },
        )

        self.html = self.add_classes(html)

    def add_classes(self, html):
        soup = BeautifulSoup(html, "html.parser")
        h1 = soup.find_all("h1")
        h2 = soup.find_all("h2")

        for tag in h1:
            tag["class"] = "title"

        for tag in h2:
            tag["class"] = "subtitle"

        return str(soup)
