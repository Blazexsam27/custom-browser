from ui.element import Element
from ui.text import Text
from config.constants import *


class HTMLParser:
    def __init__(self, body):
        self.body = body
        self.unfinished = []

    def add_text(self, text):
        if text.isspace():
            return
        self.implicit_tags(None)
        parent = self.unfinished[-1]
        node = Text(text, parent)
        parent.children.append(node)

    def add_tag(self, tag):
        tag, attributes = self.parse_tag(tag)
        if tag.startswith("!"):
            return
        self.implicit_tags(tag)
        if tag.startswith("/"):
            closing_tag = tag[1:]
            # Pop until the correct opening tag is found
            while len(self.unfinished) > 1:
                node = self.unfinished.pop()
                if node.tag == closing_tag:
                    parent = self.unfinished[-1]
                    parent.children.append(node)
                    break
                else:
                    # Unmatched tag; still attach it
                    parent = self.unfinished[-1]
                    parent.children.append(node)

        elif tag in SELF_CLOSING_TAGS:
            parent = self.unfinished[-1]
            node = Element(tag, attributes, parent)
            parent.children.append(node)

        else:
            parent = self.unfinished[-1] if self.unfinished else None
            node = Element(tag, attributes, parent)
            self.unfinished.append(node)

    def parse(self):
        text = ""
        in_tag = False

        for c in self.body:
            if c == "<":
                in_tag = True
                if text:
                    self.add_text(text)
                text = ""

            elif c == ">":
                in_tag = False
                self.add_tag(text)
                text = ""
            else:
                text += c

        if not in_tag and text:
            self.add_text(text)

        return self.finish()

    # parses the tag and yeilds its name and attributes
    def parse_tag(self, tag_str):
        import re

        tag_match = re.match(r"^(\w+)", tag_str)
        tag_name = tag_match.group(1) if tag_match else tag_str

        attr_matches = re.findall(r'(\w+)(?:=(["\'])(.*?)\2)?', tag_str)
        attrs = {}
        for attr in attr_matches:
            key, quote, value = attr
            attrs[key.casefold()] = value if quote else ""

        return tag_name, attrs

    def finish(self):
        if not self.unfinished:
            self.implicit_tags(None)
        while len(self.unfinished) > 1:
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)

        return self.unfinished.pop()

    def implicit_tags(self, tag):
        while True:
            open_tags = [node.tag for node in self.unfinished]
            if open_tags == [] and tag != "html":
                self.add_tag("html")
            elif open_tags == ["html"] and tag not in ["head", "body", "/html"]:
                if tag in HEAD_TAGS:
                    self.add_tag("head")
                else:
                    self.add_tag("body")
            elif open_tags == ["html", "head"] and tag not in ["/head"] + HEAD_TAGS:
                self.add_tag("/head")
            else:
                break


def print_tree(node, indent=0):
    print(" " * indent, node)
    for child in node.children:
        print_tree(child, indent + 2)
