# coding=utf-8
import re

import markdown2

from bs4 import BeautifulSoup

__author__ = "Gareth Coles"

ISSUE_REGEX = re.compile(r"([\s(])(#[\d]+)([\s)])")
ISSUE_URL = "https://github.com/GlowstoneMC/Glowstone/issues/{}"
ISSUE_HTML = """{}<a href="{}">{}</a>{}"""


class Markdown:
    def __init__(self, markdown):
        self.markdown = self.fix_markdown(markdown)

        html = markdown2.markdown(
            self.markdown, extras={
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

    def fix_markdown(self, markdown):
        done_tags = []

        for start, tag, end in ISSUE_REGEX.findall(markdown):
            if tag in done_tags:
                continue

            done_tags.append(tag)
            num = tag[1:]
            markdown = markdown.replace(
                "{}{}{}".format(start, tag, end),
                ISSUE_HTML.format(start, ISSUE_URL.format(num), tag, end)
            )

        return markdown

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
