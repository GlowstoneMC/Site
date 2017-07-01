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

        self.html = self.fix_html(html)
        self.summary = self.get_summary(html)

    def fix_html(self, html):
        soup = BeautifulSoup(html, "html.parser")
        headers = soup.find_all("img")

        for tag in headers:
            attrs = {
                "href": tag["src"],
                "data-caption": tag["alt"]
            }
            anchor = soup.new_tag("a", **attrs)

            tag["class"] = "image box"

            tag.wrap(anchor)

        return str(soup)

    def get_summary(self, html):
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ")

        return text.split("\n", 1)[0].strip()
